# -*- coding: utf-8 -*-

"""
Tests relacionados con las campañas
"""
from __future__ import unicode_literals

import os
import json
import threading

from crontab import CronTab
from mock import patch

from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import connections
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext as _

from ominicontacto_app.models import AgenteEnContacto, Campana, QueueMember, OpcionCalificacion
from ominicontacto_app.forms import CampanaPreviewForm, TIEMPO_MINIMO_DESCONEXION

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory, AgenteProfileFactory,
                                               AgenteEnContactoFactory, QueueMemberFactory,
                                               NombreCalificacionFactory,
                                               CalificacionClienteFactory,
                                               OpcionCalificacionFactory, ArchivoDeAudioFactory)

from ominicontacto_app.tests.utiles import OMLBaseTest, OMLTransaccionBaseTest

from ominicontacto_app.utiles import (
    validar_nombres_campanas,
    convertir_ascii_string,
)
from ominicontacto_app.services.creacion_queue import ActivacionQueueService
from ominicontacto_app.services.wombat_service import WombatService


def test_concurrently(args_list):
    """
    Add this decorator to small pieces of code that you want to test
    concurrently to make sure they don't raise exceptions when run at the
    same time.  E.g., some Django views that do a SELECT and then a subsequent
    INSERT might fail when the INSERT assumes that the data has not changed
    since the SELECT.
    (adapted from
     https://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/)
    """
    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []

            def call_test_func(*args, **kwargs):
                try:
                    test_func(*args, **kwargs)
                except Exception, e:
                    exceptions.append(e)
                    raise
            threads = []
            for arg in args_list:
                threads.append(threading.Thread(target=call_test_func, args=[arg]))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception('test_concurrently intercepted %s exceptions: %s' %
                                (len(exceptions), exceptions))
        return wrapper
    return test_concurrently_decorator


class CampanasThreadsTests(OMLTransaccionBaseTest):

    PWD = u'admin123'

    def setUp(self):
        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        self.campana = CampanaFactory.create()
        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW)

        self.campana_borrada = CampanaFactory.create(
            estado=Campana.ESTADO_BORRADA, oculto=False, type=Campana.TYPE_PREVIEW)

        self.contacto = ContactoFactory.create(bd_contacto=self.campana_activa.bd_contacto)
        self.campana_activa.bd_contacto.contactos.add(self.contacto)
        self.queue = QueueFactory.create(campana=self.campana_activa)

        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

    def tearDown(self):
        self.campana_activa.eliminar_tarea_actualizacion()
        self.campana_borrada.eliminar_tarea_actualizacion()

    def test_no_se_devuelve_un_mismo_contacto_a_mas_de_un_agente_en_campanas_preview(self):
        user1 = UserFactory(username='user1', is_agente=True)
        user2 = UserFactory(username='user2', is_agente=True)
        user1.set_password(self.PWD)
        user2.set_password(self.PWD)
        user1.save()
        user2.save()
        agente1 = AgenteProfileFactory.create(user=user1)
        agente2 = AgenteProfileFactory.create(user=user2)
        QueueMemberFactory.create(member=agente1, queue_name=self.queue)
        QueueMemberFactory.create(member=agente2, queue_name=self.queue)
        agente_en_contacto = AgenteEnContactoFactory.create(
            campana_id=self.campana_activa.pk, agente_id=-1)
        url = reverse('campana_preview_dispatcher', args=[self.campana_activa.pk])
        responses_threads = {}

        @test_concurrently([user1, user2])
        def obtener_contacto(user):
            self.client.login(username=user.username, password=self.PWD)
            response = self.client.post(url, follow=True)
            responses_threads[user.username] = json.loads(response.content)
            connections.close_all()

        obtener_contacto()

        user1_data = responses_threads['user1'].get('telefono_contacto') == unicode(
            agente_en_contacto.telefono_contacto)
        user2_no_data = responses_threads['user2'].get('code') == 'error-no-contactos'

        user1_no_data = responses_threads['user1'].get('code') == 'error-no-contactos'
        user2_data = responses_threads['user2'].get('telefono_contacto') == unicode(
            agente_en_contacto.telefono_contacto)

        test_condition = (user1_data and user2_no_data) or (user1_no_data and user2_data)

        self.assertTrue(test_condition)


class CampanasTests(OMLBaseTest):

    PWD = 'admin123'

    GESTION = 'Venta'

    def setUp(self):
        self.tiempo_desconexion = 3

        self.usuario_admin_supervisor = UserFactory(is_staff=True, is_supervisor=True)
        self.usuario_admin_supervisor.set_password(self.PWD)
        self.usuario_admin_supervisor.save()

        calificacion_nombre = "calificacion_nombre"

        self.calificacion = NombreCalificacionFactory.create(nombre=calificacion_nombre)

        calificacion_gestion = NombreCalificacionFactory.create(nombre=self.GESTION)

        self.campana = CampanaFactory.create()

        self.campana_activa = CampanaFactory.create(
            estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_PREVIEW,
            tiempo_desconexion=self.tiempo_desconexion, gestion=self.GESTION)
        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=calificacion_gestion.nombre,
            tipo=OpcionCalificacion.GESTION)
        self.opcion_calificacion_agenda = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=settings.CALIFICACION_REAGENDA,
            tipo=OpcionCalificacion.AGENDA)
        self.opcion_calificacion_noaccion = OpcionCalificacionFactory.create(
            campana=self.campana_activa, nombre=calificacion_nombre)
        self.campana_borrada = CampanaFactory.create(
            estado=Campana.ESTADO_BORRADA, oculto=False, type=Campana.TYPE_PREVIEW,
            gestion=self.GESTION)
        OpcionCalificacionFactory.create(
            campana=self.campana_borrada, nombre=calificacion_nombre,
            tipo=OpcionCalificacion.GESTION)

        self.agente_profile = AgenteProfileFactory.create(user=self.usuario_admin_supervisor)

        self.contacto = ContactoFactory.create(bd_contacto=self.campana_activa.bd_contacto)
        self.campana_activa.bd_contacto.contactos.add(self.contacto)
        self.queue = QueueFactory.create(campana=self.campana_activa)

        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

    def tearDown(self):
        for camp_prev in Campana.objects.obtener_campanas_preview():
            camp_prev.eliminar_tarea_actualizacion()

    def test_campana_contiene_atributo_entero_positivo_llamado_objetivo(self):
        self.assertTrue(self.campana.objetivo >= 0)

    def test_validacion_nombres_de_campana_no_permite_caracteres_no_ASCII(self):
        error_ascii = "el nombre no puede contener tildes ni caracteres no ASCII"
        with self.assertRaisesMessage(ValidationError, error_ascii):
            validar_nombres_campanas("áéíóúñ")

    def test_validacion_nombres_de_campana_no_permite_espacios(self):
        with self.assertRaisesMessage(ValidationError, "el nombre no puede contener espacios"):
            validar_nombres_campanas("nombre con espacios")

    def test_validacion_campana_debe_tener_alguna_opcion_calificacion_de_gestion(self):
        pass

    def test_tipo_campanas_preview(self):
        self.assertEqual(Campana.TYPE_PREVIEW, 4)

    def test_tiempo_desconexion_campanas_preview(self):
        self.assertTrue(self.campana.tiempo_desconexion >= 0)

    def test_usuarios_no_logueados_no_acceden_a_vista_lista_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_creacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_create')
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_modificacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_update', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_no_logueados_no_acceden_a_vista_eliminacion_campanas_preview(self):
        self.client.logout()
        url = reverse('campana_preview_delete', args=[self.campana_borrada.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuarios_logueados_pueden_ver_lista_de_campanas_preview_activas(self):
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_activa.nombre)

    def test_usuarios_logueados_pueden_ver_lista_de_campanas_preview_borradas(self):
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_borrada.nombre)

    def test_usuario_logueado_puede_crear_campana_preview(self):
        url = reverse('campana_preview_create')
        nombre_campana = 'campana_preview_test'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_preview(
             nombre_campana, audio_ingreso)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.assertTrue(Campana.objects.get(nombre=nombre_campana))

    def test_usuario_logueado_puede_modificar_campana_preview(self):
        url = reverse('campana_preview_update', args=[self.campana_activa.pk])
        nuevo_objetivo = 3
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_modificacion_campana_preview(
             self.campana_activa.nombre, audio_ingreso)
        post_step0_data['0-objetivo'] = nuevo_objetivo
        self.assertNotEqual(Campana.objects.get(pk=self.campana_activa.pk).objetivo,
                            nuevo_objetivo)
        # realizamos la modificación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.assertEqual(Campana.objects.get(pk=self.campana_activa.pk).objetivo, nuevo_objetivo)

    @patch.object(ActivacionQueueService, "_generar_y_recargar_configuracion_asterisk")
    def test_usuario_logueado_puede_eliminar_campana_preview(
            self, _generar_y_recargar_configuracion_asterisk):
        url = reverse('campana_preview_delete', args=[self.campana_activa.pk])
        self.assertEqual(Campana.objects.get(
            pk=self.campana_activa.pk).estado, Campana.ESTADO_ACTIVA)
        self.client.post(url, follow=True)
        self.assertEqual(Campana.objects.get(
            pk=self.campana_activa.pk).estado, Campana.ESTADO_BORRADA)

    def test_usuario_no_logueado_no_establece_supervisores_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_supervisors', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_establece_supervisores_campana_preview(self):
        url = reverse('campana_preview_supervisors', args=[self.campana_activa.pk])
        self.assertFalse(self.campana_activa.supervisors.all().exists())
        supervisor = UserFactory.create()
        self.campana_activa.supervisors.add(supervisor)
        self.campana_activa.save()
        post_data = {'supervisors': [supervisor.pk]}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(self.campana_activa.supervisors.all().exists())

    def test_usuario_no_logueado_no_agrega_agentes_a_campana(self):
        self.client.logout()
        url = reverse('queue_member_add', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    @patch.object(ActivacionQueueService, "_generar_y_recargar_configuracion_asterisk")
    def test_usuario_logueado_agrega_agentes_a_campana_preview(
            self, _generar_y_recargar_configuracion_asterisk):
        # anulamos con mock la parte de regeneracion de asterisk pues no se esta
        # comprobando en este test y ademas necesita conexión a un servidor externo
        url = reverse('queue_member_add', args=[self.campana_activa.pk])
        self.assertFalse(QueueMember.objects.all().exists())
        post_data = {'member': self.agente_profile.pk, 'penalty': 1}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(QueueMember.objects.all().exists())

    def test_relacion_agente_contacto_campanas_preview(self):
        # test que documenta la existencia del modelo que relaciona a agentes
        # con contactos
        agente_en_contacto = AgenteEnContactoFactory.create()
        self.assertTrue(isinstance(agente_en_contacto, AgenteEnContacto))

    def test_creacion_campana_preview_inicializa_relacion_agente_contacto(self):
        url = reverse('campana_preview_create')
        nombre_campana = 'campana_preview_test'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_preview(
             nombre_campana, audio_ingreso)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.all().exists())

    def test_usuario_no_logueado_no_obtiene_contacto_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_dispatcher', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_no_agente_no_obtiene_contacto_campana_preview(self):
        url = reverse('campana_preview_dispatcher', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_usuario_agente_no_asociado_campana_preview_no_obtiene_contacto(self):
        self.client.logout()
        user = UserFactory(is_agente=True)
        user.set_password(self.PWD)
        user.save()
        AgenteProfileFactory.create(user=user)

        self.client.login(username=user.username, password=self.PWD)

        url = reverse('campana_preview_dispatcher', args=[self.campana_borrada.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_agente_logueado_contacto_obtiene_contacto_campana_preview(self):
        self.client.logout()
        user = UserFactory(is_agente=True)
        user.set_password(self.PWD)
        user.save()
        agente = AgenteProfileFactory.create(user=user)
        QueueMemberFactory.create(member=agente, queue_name=self.queue)
        agente_en_contacto = AgenteEnContactoFactory.create(
            campana_id=self.campana_activa.pk, agente_id=-1)

        self.client.login(username=user.username, password=self.PWD)

        url = reverse('campana_preview_dispatcher', args=[self.campana_activa.pk])
        response = self.client.post(url, follow=True)
        data = json.loads(response.content)
        self.assertEqual(data['agente_id'], agente.pk)
        self.assertEqual(data['telefono_contacto'], unicode(agente_en_contacto.telefono_contacto))
        self.assertEqual(data['estado'], AgenteEnContacto.ESTADO_ENTREGADO)

    def test_usuario_no_logueado_no_accede_a_vista_campanas_preview_agente(self):
        self.client.logout()
        url = reverse('campana_preview_activas_miembro')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_logueado_accede_a_vista_campanas_preview_agente(self):
        url = reverse('campana_preview_activas_miembro')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'agente/campanas_preview.html')

    def test_campanas_preview_activas_muestra_las_asociadas_a_agente(self):
        url = reverse('campana_preview_activas_miembro')
        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_activa.nombre)

    def test_campanas_preview_activas_no_muestra_las_no_asociadas_a_agente(self):
        url = reverse('campana_preview_activas_miembro')
        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, self.campana_borrada.nombre)

    def _inicializar_valores_formulario_cliente(self):
        values = {
            'contacto_id': self.contacto.pk,
            'telefono_contacto': self.contacto.telefono,
            'datos_contacto': self.contacto.datos,
            'agente_id': self.agente_profile.pk,
            'estado': AgenteEnContacto.ESTADO_ENTREGADO,
            'campana_id': self.campana_activa.pk,
        }
        AgenteEnContactoFactory.create(**values)
        kwargs = {'pk_contacto': self.contacto.pk,
                  'pk_campana': self.campana_activa.pk,
                  'id_agente': self.agente_profile.pk,
                  'wombat_id': 0}
        url = reverse('calificacion_formulario_update_or_create', kwargs=kwargs)
        post_data = {'opcion_calificacion': [self.opcion_calificacion_noaccion.pk],
                     'agente': [self.agente_profile.pk],
                     'observaciones': [''],
                     'agendado': ['False'],
                     'campana': [self.campana_activa.pk],
                     'contacto': [self.contacto.pk],
                     'id': ['']}
        return values, url, post_data

    @patch('requests.post')
    def test_al_crear_formulario_cliente_finaliza_relacion_agente_contacto(self, post):
        AgenteEnContactoFactory.create(campana_id=self.campana_activa.pk)
        values, url, post_data = self._inicializar_valores_formulario_cliente()
        base_datos = self.contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(self.contacto.datos)
        for nombre, dato in zip(nombres, datos):
            post_data.update({convertir_ascii_string(nombre): "{0}-modificado".format(dato)})
        self.client.post(url, post_data, follow=True)
        values['estado'] = AgenteEnContacto.ESTADO_FINALIZADO
        self.assertTrue(AgenteEnContacto.objects.filter(**values).exists())

    @patch('requests.post')
    def test_se_finaliza_campana_si_todos_los_contactos_ya_han_sido_atendidos(self, post):
        values, url, post_data = self._inicializar_valores_formulario_cliente()
        base_datos = self.contacto.bd_contacto
        nombres = base_datos.get_metadata().nombres_de_columnas[1:]
        datos = json.loads(self.contacto.datos)
        for nombre, dato in zip(nombres, datos):
            post_data.update({convertir_ascii_string(nombre): "{0}-modificado".format(dato)})
        self.client.post(url, post_data, follow=True)
        self.campana_activa.refresh_from_db()
        self.assertEqual(self.campana_activa.estado, Campana.ESTADO_FINALIZADA)

    def test_solo_un_contacto_se_mantiene_asignado_a_un_agente(self):
        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)
        AgenteEnContactoFactory.create(campana_id=self.campana_activa.pk, agente_id=-1)
        agente_en_contacto = AgenteEnContactoFactory.create(
            campana_id=self.campana_activa.pk, agente_id=self.agente_profile.pk,
            estado=AgenteEnContacto.ESTADO_ENTREGADO)
        url = reverse('campana_preview_dispatcher', args=[self.campana_activa.pk])
        self.client.post(url, follow=True)
        agente_en_contacto.refresh_from_db()
        self.assertEqual(AgenteEnContacto.objects.filter(
            estado=AgenteEnContacto.ESTADO_ENTREGADO).count(), 1)

    def test_usuario_no_logueado_no_valida_asignacion_agente_contacto(self):
        self.client.logout()
        AgenteEnContactoFactory.create(
            campana_id=self.campana_activa.pk, contacto_id=self.contacto.pk,
            agente_id=self.agente_profile.pk, estado=AgenteEnContacto.ESTADO_ENTREGADO)
        url = reverse('validar_contacto_asignado')
        post_data = {
            'pk_agente': self.agente_profile.pk,
            'pk_campana': self.campana_activa.pk,
            'pk_contacto': self.contacto.pk
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_vista_validacion_asignacion_contacto_a_agente(self):
        AgenteEnContactoFactory.create(
            campana_id=self.campana_activa.pk, contacto_id=self.contacto.pk,
            agente_id=self.agente_profile.pk, estado=AgenteEnContacto.ESTADO_ENTREGADO)
        url = reverse('validar_contacto_asignado')
        post_data = {
            'pk_agente': self.agente_profile.pk,
            'pk_campana': self.campana_activa.pk,
            'pk_contacto': self.contacto.pk
        }
        response = self.client.post(url, post_data, follow=True)
        dict_response = json.loads(response.content)
        self.assertTrue(dict_response['contacto_asignado'])

    def test_crear_campana_preview_adiciona_tarea_programada_actualizacion_contactos(self):
        url = reverse('campana_preview_create')
        nombre_campana = 'campana_preview_test'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_preview(
             nombre_campana, audio_ingreso)
        self.assertFalse(AgenteEnContacto.objects.all().exists())
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        crontab = CronTab(user=os.getlogin())
        campana = Campana.objects.get(nombre=nombre_campana)
        jobs_generator = crontab.find_comment(str(campana.pk))
        job = list(jobs_generator)[0]
        self.assertTrue(job.is_enabled())
        self.assertTrue(job.is_valid())
        # eliminamos la tarea generada
        crontab.remove(job)

    @patch.object(ActivacionQueueService, "_generar_y_recargar_configuracion_asterisk")
    def test_borrar_campana_preview_elimina_tarea_programada_actualizacion_contactos(
            self, _generar_y_recargar_configuracion_asterisk):
        self.campana_activa.crear_tarea_actualizacion()
        url = reverse('campana_preview_delete', args=[self.campana_activa.pk])
        self.client.post(url, follow=True)
        crontab = CronTab(user=os.getlogin())
        jobs_generator = crontab.find_comment(str(self.campana_activa.pk))
        jobs = list(jobs_generator)
        self.assertEqual(jobs, [])

    def test_finalizar_campana_preview_elimina_tarea_programada_actualizacion_contactos(self):
        self.campana_activa.crear_tarea_actualizacion()
        self.campana_activa.finalizar()
        crontab = CronTab(user=os.getlogin())
        jobs_generator = crontab.find_comment(str(self.campana_activa.pk))
        jobs = list(jobs_generator)
        self.assertEqual(jobs, [])

    def test_campanas_preview_formularios_validan_minimo_tiempo_de_desconexion(self):
        nombre_campana = 'campana_preview_test'
        tiempo_desconexion = 1
        campana_preview_data = {'nombre': nombre_campana,
                                'bd_contacto': self.campana_activa.bd_contacto.pk,
                                'tipo_interaccion': Campana.FORMULARIO,
                                'formulario': self.campana.formulario.pk,
                                'auto_grabacion': True,
                                'objetivo': 1,
                                'tiempo_desconexion': tiempo_desconexion}
        campana_preview_form = CampanaPreviewForm(data=campana_preview_data)
        message = _('Debe ingresar un minimo de {0} minutos'.format(TIEMPO_MINIMO_DESCONEXION))
        self.assertEqual(campana_preview_form.errors['tiempo_desconexion'], [message])

    def test_usuario_no_logueado_no_accede_a_vista_detalle_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_detalle', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def test_usuario_no_logueado_no_accede_a_vista_detalle_express_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_detalle_express', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def _crear_datos_vistas_detalles_campana_preview(self):
        # ya existe otro contacto para la BD de la campaña creado en el setUp
        # acá creamos otro
        ContactoFactory.create(bd_contacto=self.campana_activa.bd_contacto)
        calif_gestion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=self.agente_profile)
        calif_no_accion = CalificacionClienteFactory.create(
            opcion_calificacion=self.opcion_calificacion_noaccion, agente=self.agente_profile)
        return calif_gestion, calif_no_accion

    def test_usuario_logueado_accede_a_datos_vista_detalle_campana_preview(self):
        calif_gestion, calif_no_accion = self._crear_datos_vistas_detalles_campana_preview()
        url = reverse('campana_preview_detalle', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'campana_preview/detalle.html')
        self.assertEqual(
            response.context_data['categorias'][calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][calif_no_accion.opcion_calificacion.nombre], 1)

    def test_usuario_logueado_accede_a_datos_vista_detalle_express_campana_preview(self):
        calif_gestion, calif_no_accion = self._crear_datos_vistas_detalles_campana_preview()
        url = reverse('campana_preview_detalle_express', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'campana_preview/detalle_express.html')
        self.assertEqual(
            response.context_data['categorias'][calif_gestion.opcion_calificacion.nombre], 1)
        self.assertEqual(
            response.context['categorias'][calif_no_accion.opcion_calificacion.nombre], 1)

    def test_usuario_logueado_no_accede_a_reporte_grafico_campana_preview(self):
        self.client.logout()
        url = reverse('campana_preview_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')

    def _obtener_post_data_wizard_creacion_campana_entrante(self, nombre_campana, audio_ingreso):
        post_step0_data = {
            '0-nombre': nombre_campana,
            '0-bd_contacto': '',
            '0-tipo_interaccion': self.campana.tipo_interaccion,
            '0-formulario': self.campana.formulario.pk,
            '0-objetivo': 0,
            'campana_entrante_create_view-current_step': 0,
        }
        post_step1_data = {
            '1-timeout': 1,
            '1-retry': 1,
            '1-audio_de_ingreso': audio_ingreso.pk,
            '1-maxlen': 1,
            '1-servicelevel': 1,
            '1-strategy': 'ringall',
            '1-weight': 1,
            '1-wait': 1,
            '1-auto_grabacion': 'on',
            '1-audios': audio_ingreso.pk,
            '1-announce_frequency': 1,
            'campana_entrante_create_view-current_step': 1,
            '1-name': nombre_campana,
            '1-campana': '',
        }
        post_step2_data = {
            'campana_entrante_create_view-current_step': 2,
            '2-0-nombre': 'Venta',
            '2-0-tipo': 1,
            '2-0-id': '',
            '2-TOTAL_FORMS': 1,
            '2-INITIAL_FORMS': 0,
            '2-MIN_NUM_FORMS': 1,
            '2-MAX_NUM_FORMS': 1000,
        }
        post_step3_data = {
            'campana_entrante_create_view-current_step': 3,
            '3-0-parametro': '',
            '3-0-columna': '',
            '3-0-id': '',
            '3-TOTAL_FORMS': 1,
            '3-INITIAL_FORMS': 0,
            '3-MIN_NUM_FORMS': 0,
            '3-MAX_NUM_FORMS': 1000,
        }

        return post_step0_data, post_step1_data, post_step2_data, post_step3_data

    def _obtener_post_data_wizard_creacion_campana_dialer(self, nombre_campana, audio_ingreso):
        fecha_inicio = timezone.now()
        fecha_fin = fecha_inicio + timezone.timedelta(days=5)
        post_step0_data = {
            '0-nombre': nombre_campana,
            '0-bd_contacto': self.campana_activa.bd_contacto.pk,
            '0-tipo_interaccion': self.campana.tipo_interaccion,
            '0-formulario': self.campana.formulario.pk,
            '0-objetivo': 0,
            '0-fecha_inicio': fecha_inicio.date().strftime("%d/%m/%Y"),
            '0-fecha_fin': fecha_fin.date().strftime("%d/%m/%Y"),
            'campana_dialer_create_view-current_step': 0,
        }
        post_step1_data = {
            '1-timeout': 1,
            '1-retry': 1,
            '1-audio_de_ingreso': audio_ingreso.pk,
            '1-maxlen': 1,
            '1-servicelevel': 1,
            '1-strategy': 'ringall',
            '1-weight': 1,
            '1-wait': 1,
            '1-auto_grabacion': 'on',
            '1-audios': audio_ingreso.pk,
            '1-announce_frequency': 1,
            '1-name': nombre_campana,
            '1-wrapuptime': 1,
            '1-campana': '',
            '1-detectar_contestadores': 'on',
            '1-initial_predictive_model': 'on',
            '1-initial_boost_factor': 1.0,
            '1-name': nombre_campana,
            '1-audio_para_contestadores': 1,
            'campana_dialer_create_view-current_step': 1,
        }
        post_step2_data = {
            'campana_dialer_create_view-current_step': 2,
            '2-0-nombre': 'Venta',
            '2-0-tipo': 1,
            '2-0-id': '',
            '2-TOTAL_FORMS': 1,
            '2-INITIAL_FORMS': 0,
            '2-MIN_NUM_FORMS': 1,
            '2-MAX_NUM_FORMS': 1000,
        }
        post_step3_data = {
            'campana_dialer_create_view-current_step': 3,
            '3-0-parametro': '',
            '3-0-columna': '',
            '3-0-id': '',
            '3-TOTAL_FORMS': 1,
            '3-INITIAL_FORMS': 0,
            '3-MIN_NUM_FORMS': 0,
            '3-MAX_NUM_FORMS': 1000,
        }
        post_step4_data = {
            'campana_dialer_create_view-current_step': 4,
            '4-lunes': 'on',
            '4-martes': 'on',
            '4-miercoles': 'on',
            '4-jueves': 'on',
            '4-viernes': 'on',
            '4-hora_desde': '09:06',
            '4-hora_hasta': '18:06',
        }
        post_step5_data = {
            'campana_dialer_create_view-current_step': 5,
            '5-0-estado': '',
            '5-0-reintentar_tarde': '',
            '5-0-intento_max': '',
            '5-TOTAL_FORMS': '1',
            '5-INITIAL_FORMS': '0',
            '5-MIN_NUM_FORMS': '0',
            '5-MAX_NUM_FORMS': '1000',
        }
        post_step6_data = {
            '6-evitar_duplicados': 'on',
            '6-evitar_sin_telefono': 'on',
            '6-prefijo_discador': '351',
            'campana_dialer_create_view-current_step': 6,
        }

        return (post_step0_data, post_step1_data, post_step2_data, post_step3_data,
                post_step4_data, post_step5_data, post_step6_data)

    def _obtener_post_data_wizard_creacion_campana_manual(self, nombre_campana):
        post_step0_data = {
            '0-nombre': nombre_campana,
            '0-bd_contacto': '',
            '0-tipo_interaccion': self.campana.tipo_interaccion,
            '0-formulario': self.campana.formulario.pk,
            '0-objetivo': 0,
            'campana_manual_create_view-current_step': 0,
        }
        post_step1_data = {
            'campana_manual_create_view-current_step': 1,
            '1-0-nombre': 'Venta',
            '1-0-tipo': 1,
            '1-0-id': '',
            '1-TOTAL_FORMS': 1,
            '1-INITIAL_FORMS': 0,
            '1-MIN_NUM_FORMS': 1,
            '1-MAX_NUM_FORMS': 1000,
        }
        post_step2_data = {
            'campana_manual_create_view-current_step': 2,
            '2-0-parametro': '',
            '2-0-columna': '',
            '2-0-id': '',
            '2-TOTAL_FORMS': 1,
            '2-INITIAL_FORMS': 0,
            '2-MIN_NUM_FORMS': 0,
            '2-MAX_NUM_FORMS': 1000,
        }

        return post_step0_data, post_step1_data, post_step2_data

    def _obtener_post_data_wizard_creacion_campana_preview(self, nombre_campana, audio_ingreso):
        # los parámetros de creación de una campaña preview son bastante similares a una manual
        # por lo que se reutiliza el código del método que genera los parámetros para las campañas
        # manuales y sólo se modifican algunos
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_manual(
            nombre_campana)
        post_step0_data.pop('campana_manual_create_view-current_step')
        post_step1_data.pop('campana_manual_create_view-current_step')
        post_step2_data.pop('campana_manual_create_view-current_step')
        post_step0_data['0-bd_contacto'] = self.campana_activa.bd_contacto.pk
        post_step0_data['0-tiempo_desconexion'] = 2
        post_step0_data['campana_preview_create_view-current_step'] = 0
        post_step1_data['campana_preview_create_view-current_step'] = 1
        post_step2_data['campana_preview_create_view-current_step'] = 2

        return post_step0_data, post_step1_data, post_step2_data

    def _obtener_post_data_wizard_modificacion_campana_preview(self, nombre_campana, audio_ingreso):
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_preview(
            nombre_campana, audio_ingreso)
        post_step0_data.pop('campana_preview_create_view-current_step')
        post_step1_data.pop('campana_preview_create_view-current_step')
        post_step2_data.pop('campana_preview_create_view-current_step')
        post_step0_data['campana_preview_update_view-current_step'] = 0
        post_step2_data['campana_preview_update_view-current_step'] = 2
        post_step1_data = {
            'campana_preview_update_view-current_step': 1,
            '1-0-nombre': self.opcion_calificacion_gestion.nombre,
            '1-0-tipo': OpcionCalificacion.GESTION,
            '1-0-id': self.opcion_calificacion_gestion.pk,
            '1-1-nombre': self.opcion_calificacion_agenda.nombre,
            '1-1-tipo': OpcionCalificacion.AGENDA,
            '1-1-id': self.opcion_calificacion_agenda.pk,
            '1-TOTAL_FORMS': 2,
            '1-INITIAL_FORMS': 2,
            '1-MIN_NUM_FORMS': 1,
            '1-MAX_NUM_FORMS': 1000,
        }
        post_step2_data['0-2-id'] = None

        return post_step0_data, post_step1_data, post_step2_data

    @patch.object(ActivacionQueueService, "_generar_y_recargar_configuracion_asterisk")
    def test_wizard_crear_campana_entrante_sin_bd_le_asigna_bd_contactos_defecto(
            self, _generar_y_recargar_configuracion_asterisk):
        url = reverse('campana_nuevo')
        nombre_campana = 'campana_name'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data, post_step2_data,
         post_step3_data) = self._obtener_post_data_wizard_creacion_campana_entrante(
             nombre_campana, audio_ingreso)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.client.post(url, post_step3_data, follow=True)

        self.assertTrue(Campana.objects.filter(nombre=nombre_campana).exists())
        campana = Campana.objects.get(nombre=nombre_campana)
        self.assertTrue(campana.bd_contacto is not None)

    @patch.object(ActivacionQueueService, "_generar_y_recargar_configuracion_asterisk")
    def test_wizard_es_posible_asignar_contacto_a_bd_por_defecto_en_campana_entrante(
            self, _generar_y_recargar_configuracion_asterisk):
        url = reverse('campana_nuevo')
        nombre_campana = 'campana_name'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data, post_step2_data,
         post_step3_data) = self._obtener_post_data_wizard_creacion_campana_entrante(
             nombre_campana, audio_ingreso)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.client.post(url, post_step3_data, follow=True)

        campana = Campana.objects.get(nombre=nombre_campana)
        self.assertEqual(campana.bd_contacto.contactos.count(), 0)
        self.contacto = ContactoFactory.create(bd_contacto=campana.bd_contacto)
        campana.bd_contacto.contactos.add(self.contacto)
        self.assertEqual(campana.bd_contacto.contactos.count(), 1)

    def test_wizard_crear_campana_manual_sin_bd_crea_y_le_asigna_bd_contactos_defecto(self):
        url = reverse('campana_manual_create')
        nombre_campana = 'campana_nombre'
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_manual(
             nombre_campana)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)

        self.assertTrue(Campana.objects.filter(nombre=nombre_campana).exists())
        campana = Campana.objects.get(nombre=nombre_campana)
        self.assertTrue(campana.bd_contacto is not None)

    def test_wizard_es_posible_asignar_contacto_a_bd_por_defecto_en_campana_manual(self):
        url = reverse('campana_manual_create')
        nombre_campana = 'campana_nombre'
        (post_step0_data, post_step1_data,
         post_step2_data) = self._obtener_post_data_wizard_creacion_campana_manual(
             nombre_campana)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)

        campana = Campana.objects.get(nombre=nombre_campana)
        self.assertEqual(campana.bd_contacto.contactos.count(), 0)
        self.contacto = ContactoFactory.create(bd_contacto=campana.bd_contacto)
        campana.bd_contacto.contactos.add(self.contacto)
        self.assertEqual(campana.bd_contacto.contactos.count(), 1)

    @patch.object(WombatService, 'list_config_wombat')
    def test_reporte_grafico_campana_preview_no_muestra_llamadas_recibidas(
            self, list_config_wombat):
        url = reverse('campana_preview_reporte_grafico', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        graficos_estadisticas = response.context_data['graficos_estadisticas']
        categorias_llamadas = [nombre for nombre, count in
                               graficos_estadisticas['dict_llamadas_counter']]
        categoria_recibidas = 'Recibidas'
        self.assertFalse(categoria_recibidas in categorias_llamadas)

    @patch('ominicontacto_app.services.campana_service.CampanaService')
    def test_usuario_logueado_puede_crear_campana_dialer(self, CampanaService):
        url = reverse('campana_dialer_create')
        nombre_campana = 'campana_dialer_test'
        audio_ingreso = ArchivoDeAudioFactory.create()
        (post_step0_data, post_step1_data, post_step2_data, post_step3_data,
         post_step4_data, post_step5_data,
         post_step6_data) = self._obtener_post_data_wizard_creacion_campana_dialer(
             nombre_campana, audio_ingreso)
        # realizamos la creación de la campaña mediante el wizard
        self.client.post(url, post_step0_data, follow=True)
        self.client.post(url, post_step1_data, follow=True)
        self.client.post(url, post_step2_data, follow=True)
        self.client.post(url, post_step3_data, follow=True)
        self.client.post(url, post_step4_data, follow=True)
        self.client.post(url, post_step5_data, follow=True)
        self.client.post(url, post_step6_data, follow=True)

        self.assertTrue(Campana.objects.filter(nombre=nombre_campana).exists())
