# -*- coding: utf-8 -*-

"""
Tests sobre los procesos realicionados con la calificaciones de los contactos de las campañas
"""

from mock import patch

from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (CampanaFactory, QueueFactory, UserFactory,
                                               ContactoFactory, AgenteProfileFactory,
                                               QueueMemberFactory,
                                               CalificacionClienteFactory,
                                               NombreCalificacionFactory,
                                               OpcionCalificacionFactory)

from ominicontacto_app.models import (AgendaContacto, NombreCalificacion, Campana,
                                      OpcionCalificacion, WombatLog)


class CalificacionTests(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self):
        super(CalificacionTests, self).setUp()
        self.usuario_agente = UserFactory(is_agente=True)
        self.usuario_agente.set_password(self.PWD)
        self.usuario_agente.save()

        self.campana = CampanaFactory.create()
        self.nombre_opcion_gestion = NombreCalificacionFactory.create(nombre=self.campana.gestion)
        self.nombre_calificacion_agenda = NombreCalificacion.objects.get(
            nombre=settings.CALIFICACION_REAGENDA)
        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_gestion.nombre,
            tipo=OpcionCalificacion.GESTION)
        self.opcion_calificacion_agenda = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_calificacion_agenda.nombre,
            tipo=OpcionCalificacion.AGENDA)
        self.opcion_calificacion_camp_manual = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_opcion_gestion.nombre)

        self.contacto = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto)

        self.queue = QueueFactory.create(campana=self.campana)
        self.agente_profile = AgenteProfileFactory.create(user=UserFactory(is_agente=True))

        self.calificacion_cliente = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_camp_manual, agente=self.agente_profile,
            contacto=self.contacto)

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)

        self.client.login(username=self.usuario_agente, password=self.PWD)

    def _setUp_campana_dialer(self):
        self.campana_dialer = CampanaFactory.create(type=Campana.TYPE_DIALER)
        self.campana_dialer.opciones_calificacion.add(self.opcion_calificacion_gestion)
        self.campana_dialer.opciones_calificacion.add(self.opcion_calificacion_agenda)

        self.contacto_dialer = ContactoFactory.create()
        self.campana_dialer.bd_contacto.contactos.add(self.contacto_dialer)

        self.queue_dialer = QueueFactory.create(campana=self.campana_dialer)

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue_dialer)

    def _obtener_post_data_calificacion_cliente(self, campana=None, contacto=None):
        if campana is None:
            campana = self.campana
        if contacto is None:
            contacto = self.contacto
        post_data = {
            'telefono': contacto.telefono,
            'campana': campana.pk,
            'contacto': contacto.pk,
            'agente': self.agente_profile.pk,
            'opcion_calificacion': '',
        }
        return post_data

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_creacion_calificacion(self):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    def test_no_se_admite_tipo_calificacion_cliente_vacia_en_modificacion_calificacion(self):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        response = self.client.post(url, post_data, follow=True)
        calificacion_form = response.context_data.get('calificacion_form')
        self.assertFalse(calificacion_form.is_valid())

    @patch('requests.post')
    def test_calificacion_cliente_creacion_redirecciona_formulario_gestion(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/formulario_create.html')

    @patch('requests.post')
    def test_calificacion_cliente_modificacion_redirecciona_formulario_gestion(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'formulario/formulario_create.html')

    def test_existe_calificacion_especial_agenda(self):
        self.assertTrue(NombreCalificacion.objects.filter(nombre=settings.CALIFICACION_REAGENDA))

    def _obtener_post_data_calificacion_manual(self):
        post_data = {
            'agente': self.agente_profile.pk,
            'calificacion': '',
            'observaciones': 'test',
            'es_venta': False,
            'campana': self.campana.pk,
            'agendado': False,
            'telefono': self.contacto.pk
        }
        return post_data

    @patch('requests.post')
    def test_escoger_calificacion_agenda_redirecciona_formulario_agenda(self, post):
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente()
        post_data['opcion_calificacion'] = self.opcion_calificacion_agenda.pk
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'agenda_contacto/create_agenda_contacto.html')

    # Test: Llega WombatLog antes de calificar
    @patch('requests.post')
    def test_update_wombat_log_calificacion_vacia(self, post):
        self._setUp_campana_dialer()
        # Llega el WombatLog desde WombatDialer antes de calificar (cuelga y luego califica)
        url = reverse('wombat_log')
        post_data = {'I_ID_CLIENTE': self.contacto_dialer.id,
                     'I_ID_CAMPANA': self.campana_dialer.id,
                     'num': str(self.contacto_dialer.telefono),
                     'state': 'BASURA',
                     'extstate': '',
                     'timeout': '0',
                     'reschedule': '',
                     'retry': '',
                     }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.json()['status'], 'OK')
        log = WombatLog.objects.get(campana=self.campana_dialer, contacto=self.contacto_dialer)
        self.assertEqual(log.telefono, str(self.contacto_dialer.telefono))

        # Califico localmente, y el WombatLog debe quedar con ese valor de calificacion
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana_dialer.pk,
                              'pk_contacto': self.contacto_dialer.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente(campana=self.campana_dialer,
                                                                 contacto=self.contacto_dialer)
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        self.client.post(url, post_data, follow=True)
        log = WombatLog.objects.get(id=log.id)
        self.assertEqual(log.agente, self.agente_profile)
        self.assertEqual(log.estado, 'TERMINATED')
        self.assertEqual(log.calificacion, self.opcion_calificacion_gestion.nombre)

    @patch('requests.post')
    def test_update_wombat_log_despues_de_calificar(self, post):
        # Llega WombatLog despues de calificar con calificacion
        self._setUp_campana_dialer()

        # Calificacion
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana_dialer.pk,
                              'pk_contacto': self.contacto_dialer.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente(campana=self.campana_dialer,
                                                                 contacto=self.contacto_dialer)
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        self.client.post(url, post_data, follow=True)
        log = WombatLog.objects.get(campana=self.campana_dialer, contacto=self.contacto_dialer)
        self.assertEqual(log.calificacion, self.opcion_calificacion_gestion.nombre)

        # Llega el WombatLog desde WombatDialer después de calificar (califica y luego cuelga)
        url = reverse('wombat_log')
        post_data = {'I_ID_CLIENTE': self.contacto_dialer.id,
                     'I_ID_CAMPANA': self.campana_dialer.id,
                     'num': str(self.contacto_dialer.telefono),
                     'O_id_agente': self.agente_profile.id,
                     'state': 'TERMINAL',
                     'extstate': 'CALIFICACION_NUEVA',
                     'timeout': '0',
                     'reschedule': '',
                     'retry': '',
                     }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.json()['status'], 'OK')
        log = WombatLog.objects.get(id=log.id)
        self.assertEqual(log.agente, self.agente_profile)
        self.assertEqual(log.calificacion, 'CALIFICACION_NUEVA')

    @patch('requests.post')
    def test_update_wombat_log_con_calificacion_vacia_despues_de_calificar(self, post):
        # Test: Llega WombatLog despues de calificar sin calificacion
        self._setUp_campana_dialer()

        # Calificacion
        url = reverse('calificacion_formulario_update_or_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana_dialer.pk,
                              'pk_contacto': self.contacto_dialer.pk,
                              'wombat_id': 0})
        post_data = self._obtener_post_data_calificacion_cliente(campana=self.campana_dialer,
                                                                 contacto=self.contacto_dialer)
        post_data['opcion_calificacion'] = self.opcion_calificacion_gestion.pk
        self.client.post(url, post_data, follow=True)
        log = WombatLog.objects.get(campana=self.campana_dialer, contacto=self.contacto_dialer)
        self.assertEqual(log.calificacion, self.opcion_calificacion_gestion.nombre)

        # Llega el WombatLog desde WombatDialer después de calificar (califica y luego cuelga)
        url = reverse('wombat_log')
        post_data = {'I_ID_CLIENTE': self.contacto_dialer.id,
                     'I_ID_CAMPANA': self.campana_dialer.id,
                     'num': str(self.contacto_dialer.telefono),
                     'O_id_agente': self.agente_profile.id,
                     'state': 'TERMINAL',
                     'extstate': '',
                     'timeout': '0',
                     'reschedule': '',
                     'retry': '',
                     }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.json()['status'], 'OK')
        log = WombatLog.objects.get(id=log.id)
        self.assertEqual(log.agente, self.agente_profile)
        self.assertEqual(log.calificacion, self.opcion_calificacion_gestion.nombre)

    @patch('requests.post')
    def test_calificacion_cliente_marcada_agendado_cuando_se_salva_agenda(self, post):
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.agendado = False
        self.calificacion_cliente.save()
        url = reverse('agenda_contacto_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        self.assertFalse(self.calificacion_cliente.agendado)
        self.client.post(url, post_data, follow=True)
        self.calificacion_cliente.refresh_from_db()
        self.assertTrue(self.calificacion_cliente.agendado)

    def _obtener_post_data_agenda(self):
        observaciones = 'test_schedule'
        siguiente_dia = timezone.now() + timezone.timedelta(days=1)
        fecha = str(siguiente_dia.date())
        hora = str(siguiente_dia.time())
        post_data = {'contacto': self.contacto.pk,
                     'campana': self.campana.pk,
                     'agente': self.agente_profile.pk,
                     'fecha': fecha,
                     'telefono': self.contacto.telefono,
                     'hora': hora,
                     'tipo_agenda': AgendaContacto.TYPE_PERSONAL,
                     'observaciones': observaciones}
        return post_data

    @patch('requests.post')
    def test_no_se_programan_en_wombat_agendas_globales_calificaciones_campanas_no_dialer(
            self, post):
        self.campana.type = Campana.TYPE_PREVIEW
        self.campana.save()
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()

        url = reverse('agenda_contacto_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        post_data['tipo_agenda'] = AgendaContacto.TYPE_GLOBAL
        self.client.post(url, post_data, follow=True)
        self.assertEqual(post.call_count, 0)

    @patch('requests.post')
    def test_se_programan_en_wombat_agendas_globales_calificaciones_campanas_dialer(
            self, post):
        self.campana.type = Campana.TYPE_DIALER
        self.campana.save()
        self.calificacion_cliente.opcion_calificacion = self.opcion_calificacion_agenda
        self.calificacion_cliente.save()
        url = reverse('agenda_contacto_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        post_data['tipo_agenda'] = AgendaContacto.TYPE_GLOBAL
        self.client.post(url, post_data, follow=True)
        self.assertEqual(post.call_count, 1)

    @patch('requests.post')
    def test_creacion_agenda_contacto_adiciona_campo_campana(self, post):
        self.calificacion_cliente.opcion_calificacion_gestion = self.opcion_calificacion_agenda
        url = reverse('agenda_contacto_create',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'pk_contacto': self.contacto.pk})
        post_data = self._obtener_post_data_agenda()
        self.client.post(url, post_data, follow=True)
        agenda_contacto = AgendaContacto.objects.first()
        self.assertEqual(agenda_contacto.campana.pk, self.campana.pk)
