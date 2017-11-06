# -*- coding: utf-8 -*-

"""
Tests relacionados con las campañas
"""
from __future__ import unicode_literals

import json
import threading

from mock import patch

from django.core.urlresolvers import reverse
from django.db import connections
from django.forms import ValidationError

from ominicontacto_app.models import AgenteEnContacto, Campana, QueueMember

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory, AgenteProfileFactory,
                                               AgenteEnContactoFactory, QueueMemberFactory)

from ominicontacto_app.tests.utiles import OMLBaseTest, OMLTransaccionBaseTest

from ominicontacto_app.utiles import validar_nombres_campanas
from ominicontacto_app.services.creacion_queue import ActivacionQueueService


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
        self.agente_profile = AgenteProfileFactory.create(user=self.usuario_admin_supervisor)

        self.contacto = ContactoFactory.create(bd_contacto=self.campana_activa.bd_contacto)
        self.campana_activa.bd_contacto.contactos.add(self.contacto)
        self.queue = QueueFactory.create(campana=self.campana_activa)

        self.client.login(username=self.usuario_admin_supervisor.username, password=self.PWD)

    def test_campana_contiene_atributo_entero_positivo_llamado_objetivo(self):
        self.assertTrue(self.campana.objetivo >= 0)

    def test_validacion_nombres_de_campana_no_permite_caracteres_no_ASCII(self):
        error_ascii = "el nombre no puede contener tildes ni caracteres no ASCII"
        with self.assertRaisesMessage(ValidationError, error_ascii):
            validar_nombres_campanas("áéíóúñ")

    def test_validacion_nombres_de_campana_no_permite_espacios(self):
        with self.assertRaisesMessage(ValidationError, "el nombre no puede contener espacios"):
            validar_nombres_campanas("nombre con espacios")

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

    def test_usuarios_logueados_pueden_ver_lista_de_campanas_preview_borras(self):
        url = reverse('campana_preview_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.campana_borrada.nombre)

    def test_usuario_logueado_puede_crear_campana_preview(self):
        url = reverse('campana_preview_create')
        nombre_campana = 'campana_preview_test'
        post_data = {'nombre': nombre_campana,
                     'calificacion_campana': self.campana.calificacion_campana.pk,
                     'bd_contacto': self.campana_activa.bd_contacto.pk,
                     'tipo_interaccion': Campana.FORMULARIO,
                     'formulario': self.campana.formulario.pk,
                     'gestion': 'Venta',
                     'detectar_contestadores': True,
                     'auto_grabacion': True,
                     'objetivo': 1,
                     'tiempo_desconexion': 10}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(Campana.objects.get(nombre=nombre_campana))

    def test_usuario_logueado_puede_modificar_campana_preview(self):
        url = reverse('campana_preview_update', args=[self.campana_activa.pk])
        nombre_campana = 'campana_preview_actualizada'
        post_data = {'nombre': nombre_campana,
                     'calificacion_campana': self.campana.calificacion_campana.pk,
                     'bd_contacto': self.campana_activa.bd_contacto.pk,
                     'tipo_interaccion': Campana.FORMULARIO,
                     'formulario': self.campana.formulario.pk,
                     'gestion': 'Venta',
                     'detectar_contestadores': True,
                     'auto_grabacion': True,
                     'objetivo': 1,
                     'tiempo_desconexion': 10}
        self.assertNotEqual(Campana.objects.get(pk=self.campana_activa.pk).nombre, nombre_campana)
        self.client.post(url, post_data, follow=True)
        self.assertEqual(Campana.objects.get(pk=self.campana_activa.pk).nombre, nombre_campana)

    def test_usuario_logueado_puede_eliminar_campana_preview(self):
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
        post_data = {'nombre': nombre_campana,
                     'calificacion_campana': self.campana.calificacion_campana.pk,
                     'bd_contacto': self.campana_activa.bd_contacto.pk,
                     'tipo_interaccion': Campana.FORMULARIO,
                     'formulario': self.campana.formulario.pk,
                     'gestion': 'Venta',
                     'detectar_contestadores': True,
                     'auto_grabacion': True,
                     'objetivo': 1,
                     'tiempo_desconexion': 10}
        self.assertFalse(AgenteEnContacto.objects.all().exists())
        self.client.post(url, post_data, follow=True)
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

    def test_agregar_contacto_campana_preview_crea_entrada_agente_agente_contacto(self):
        url = reverse('nuevo_contacto_campana_dialer',
                      kwargs={'pk_campana': self.campana_activa.pk})
        telefono = '23534534'
        post_data = {'apellido': 'apellido-test', 'telefono3': '1322434573',
                     'telefono2': '1242355345', 'dni': '1233242', 'nombre': 'nombre-test',
                     'telefono': '23534534'}
        self.client.post(url, post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.filter(telefono_contacto=telefono).exists())
