# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Tests busqueda y reasignacion de Agendas de contacto
"""

# from mock import patch
import random

# from django.utils.translation import gettext as _
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import (
    NombreCalificacion, Campana, OpcionCalificacion, AgendaContacto, )
from ominicontacto_app.tests.factories import (
    CampanaFactory, QueueFactory, ContactoFactory, QueueMemberFactory, OpcionCalificacionFactory,
    AgendaContactoFactory, CalificacionClienteFactory,
)


class CalificacionTests(OMLBaseTest):

    def setUp(self):
        super(CalificacionTests, self).setUp()

        self.agente_1 = self.crear_agente_profile()
        self.agente_2 = self.crear_agente_profile()
        self.agente_3 = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile()

        self.campana = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_MANUAL)
        self.campana.supervisors.add(self.supervisor.user)

        self.nombre_calificacion_agenda = NombreCalificacion.objects.get(
            nombre=settings.CALIFICACION_REAGENDA)
        self.opcion_calificacion_agenda = OpcionCalificacionFactory.create(
            campana=self.campana, nombre=self.nombre_calificacion_agenda.nombre,
            tipo=OpcionCalificacion.AGENDA)

        self.contacto_1 = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto_1)
        self.contacto_2 = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto_2)

        self.calificacion_1 = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_agenda, agente=self.agente_1,
            contacto=self.contacto_1)
        self.agenda_1 = AgendaContactoFactory(
            agente=self.agente_1, contacto=self.contacto_1, campana=self.campana,
            tipo_agenda=AgendaContacto.TYPE_PERSONAL)
        self.calificacion_2 = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_agenda, agente=self.agente_2,
            contacto=self.contacto_2)
        self.agenda_2 = AgendaContactoFactory(
            agente=self.agente_2, contacto=self.contacto_2, campana=self.campana,
            tipo_agenda=AgendaContacto.TYPE_PERSONAL)

        self.queue = QueueFactory.create(campana=self.campana)
        QueueMemberFactory.create(member=self.agente_1, queue_name=self.queue)
        QueueMemberFactory.create(member=self.agente_2, queue_name=self.queue)

        self.client.login(username=self.supervisor.user.username, password=PASSWORD)

    def test_filtrar_por_agente(self):
        url = reverse('agenda_contactos_por_campana', kwargs={'pk_campana': self.campana.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])

        self.assertContains(response, self.agente_1.user.get_full_name())
        self.assertContains(response, self.agente_2.user.get_full_name())
        self.assertNotContains(response, self.agente_3.user.get_full_name())

        self.assertContains(response, self.contacto_1.telefono)
        self.assertContains(response, self.contacto_2.telefono)

        fecha = self.agenda_1.fecha.strftime('%d/%m/%Y - %d/%m/%Y')
        response = self.client.post(url, data={'fecha': fecha, 'usuario': self.agente_1.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.contacto_1.telefono)
        self.assertNotContains(response, self.contacto_2.telefono)

    def test_reasignar_agente(self):
        url = reverse('api_reasignar_agenda_contacto')
        response = self.client.post(
            url, data={'agenda_id': self.agenda_1.id, 'agent_id': self.agente_2.id})
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'OK')
        self.assertEqual(response_json['agenda_id'], str(self.agenda_1.id))
        self.assertEqual(response_json['agent_name'], self.agente_2.user.get_full_name())
        self.agenda_1.refresh_from_db()
        self.assertEqual(self.agenda_1.agente, self.agente_2)
        self.calificacion_1.refresh_from_db()
        self.assertEqual(self.calificacion_1.agente, self.agente_2)

    def test_crear_editar_agendar_contacto_con_telefono(self):
        siguiente_dia = timezone.now()
        fecha = str(siguiente_dia.date())
        hora = str(siguiente_dia.time())
        contacto_nuevo = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(contacto_nuevo)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_agenda, agente=self.agente_1,
            contacto=contacto_nuevo)
        url_create = reverse('agenda_contacto_create',
                             kwargs={'pk_campana': self.campana.pk,
                                     'pk_contacto': contacto_nuevo.pk})
        telefono = random.choice(contacto_nuevo.lista_de_telefonos_de_contacto())
        post_data = {
            'agente': self.agente_1.id,
            'contacto': contacto_nuevo.id,
            'campana': self.campana.id,
            'fecha': fecha,
            'telefono': telefono,
            'hora': hora,
            'tipo_agenda': AgendaContacto.TYPE_PERSONAL,
            'observaciones': 'test_schedule'
        }
        self.client.login(username=self.agente_1.user.username, password=PASSWORD)
        response = self.client.post(url_create, post_data, follow=True)
        self.assertEqual(response.context['agendacontacto'].telefono, telefono)
        agendacontacto_id = response.context['agendacontacto'].id
        url_update = reverse('agenda_contacto_update', kwargs={'pk': agendacontacto_id})
        telefono_2 = random.choice(contacto_nuevo.lista_de_telefonos_de_contacto())
        post_data['telefono'] = telefono_2
        response2 = self.client.post(url_update, post_data, follow=True)
        self.assertEqual(response2.context['agendacontacto'].telefono, telefono_2)

    def test_editar_telefono_agenda(self):
        agendacontacto_id = self.agenda_1.id
        url_update = reverse('agenda_contacto_update', kwargs={'pk': agendacontacto_id})
        telefono = random.choice(self.agenda_1.contacto.lista_de_telefonos_de_contacto())
        self.client.login(username=self.agente_1.user.username, password=PASSWORD)
        response = self.client.post(url_update, {'telefono': telefono}, follow=True)
        self.assertEqual(response.context['agendacontacto'].telefono, telefono)

    def test_editar_telefono_agenda_con_telefono_erroneo(self):
        agendacontacto_id = self.agenda_1.id
        url_update = reverse('agenda_contacto_update', kwargs={'pk': agendacontacto_id})
        telefono = "00110011"
        self.client.login(username=self.agente_1.user.username, password=PASSWORD)
        response = self.client.post(url_update, {'telefono': telefono}, follow=True)
        self.assertNotEqual(response.context['agendacontacto'].telefono, telefono)


class ExportCsvAgendasTests(OMLBaseTest):
    def setUp(self):
        super().setUp()
        self.agente_1 = self.crear_agente_profile()
        self.agente_2 = self.crear_agente_profile()
        self.agente_3 = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile()

        self.campana1 = CampanaFactory.create(nombre='campana1', estado=Campana.ESTADO_ACTIVA)
        self.campana2 = CampanaFactory.create(nombre='campana2', estado=Campana.ESTADO_ACTIVA)
        self.campana3 = CampanaFactory.create(nombre='campana3', estado=Campana.ESTADO_ACTIVA)

        self.contacto_1 = ContactoFactory.create()
        self.contacto_2 = ContactoFactory.create()

        self.agenda_1 = AgendaContactoFactory(
            agente=self.agente_1, tipo_agenda=AgendaContacto.TYPE_PERSONAL,
            contacto=self.contacto_1, campana=self.campana1, telefono=11111)
        self.agenda_2 = AgendaContactoFactory(
            agente=self.agente_1, tipo_agenda=AgendaContacto.TYPE_PERSONAL,
            contacto=self.contacto_2, campana=self.campana2, telefono=22222)
        self.agenda_3 = AgendaContactoFactory(
            agente=self.agente_1, tipo_agenda=AgendaContacto.TYPE_PERSONAL,
            contacto=self.contacto_2, campana=self.campana2, telefono=33333)
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)

    def test_filtrado_ok(self):
        fecha = timezone.now().date().strftime('%d/%m/%Y - %d/%m/%Y')
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "agente": self.agente_1.id,
                "fecha": fecha
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cantidad'], 3)
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "campana": [self.campana1.id],
                "fecha": fecha
            },
        )
        self.assertEqual(response.context['cantidad'], 1)
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "campana": [self.campana1.id, self.campana2.id],
                "fecha": fecha
            },
        )
        self.assertEqual(response.context['cantidad'], 3)

    def test_exportar_ok(self):
        fecha = timezone.now().date().strftime('%d/%m/%Y - %d/%m/%Y')
        csv_row_0 = "id,fecha,hora,tipo_agenda,first_name,last_name,campana,telefono"
        csv_row_1 = "{},{},{},1,User_0,Test,campana1,11111".format(
            self.agenda_1.id, self.agenda_1.fecha, self.agenda_1.hora.strftime('%H:%M:%S'))
        csv_row_2 = "{},{},{},1,User_0,Test,campana2,22222".format(
            self.agenda_2.id, self.agenda_2.fecha, self.agenda_2.hora.strftime('%H:%M:%S'))
        csv_row_3 = "{},{},{},1,User_0,Test,campana2,33333".format(
            self.agenda_3.id, self.agenda_3.fecha, self.agenda_3.hora.strftime('%H:%M:%S'))
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "campana": [self.campana1.id],
                "fecha": fecha,
                '_exportar': ['']
            },
        )
        self.assertEqual(
            response.getvalue().decode().splitlines(),
            [
                csv_row_0,
                csv_row_1,
            ],
        )
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "campana": [self.campana2.id],
                "fecha": fecha,
                '_exportar': ['']
            },
        )
        self.assertEqual(
            response.getvalue().decode().splitlines(),
            [
                csv_row_0,
                csv_row_2,
                csv_row_3
            ],
        )

    def test_eliminar_ok(self):
        fecha = timezone.now().date().strftime('%d/%m/%Y - %d/%m/%Y')
        response = self.client.post(
            reverse("agenda_contactos"),
            {
                "agente": self.agente_1.id,
                "fecha": fecha,
                "_eliminar": ['']
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cantidad'], 0)
