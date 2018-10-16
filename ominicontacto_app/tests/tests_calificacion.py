# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Tests sobre los procesos realicionados con la calificaciones de los contactos de las campañas
"""
import json

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
                                      OpcionCalificacion)


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
        self.agente_profile = AgenteProfileFactory.create(user=self.usuario_agente)

        self.calificacion_cliente = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_camp_manual, agente=self.agente_profile,
            contacto=self.contacto)

        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)

        self.client.login(username=self.usuario_agente.username, password=self.PWD)

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

    def test_llamada_manual_telefono_no_contacto_muestra_formulario_calificacion_blanco(self):
        # garantizamos un número distinto al existente en la campaña
        telefono = str(self.contacto.telefono) + '11'
        url = reverse('calificar_por_telefono',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        contacto_form = response.context_data['contacto_form']
        datos_contacto_form = set(contacto_form.initial.values())
        self.assertEqual(datos_contacto_form, set(['', telefono]))

    def test_llamada_manual_telefono_con_1_contacto_muestra_datos_contacto_formulario(self):
        contacto = self.contacto
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        contacto_form = response.context_data['contacto_form']
        datos_contacto_form = set(contacto_form.initial.values())
        datos_contacto_model = set(json.loads(contacto.datos) + [str(telefono)])
        self.assertEqual(datos_contacto_form, datos_contacto_model)

    def test_llamada_manual_telefono_con_n_contactos_redirecciona_vista_escoger_contacto(self):
        contacto = self.contacto
        ContactoFactory(bd_contacto=self.campana.bd_contacto, telefono=contacto.telefono)
        telefono = contacto.telefono
        url = reverse('calificar_por_telefono',
                      kwargs={'id_agente': self.agente_profile.pk,
                              'pk_campana': self.campana.pk,
                              'telefono': telefono})
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'agente/contactos_telefonos_repetidos.html')
