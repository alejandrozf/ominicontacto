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

# from django.utils.translation import gettext as _
from django.conf import settings
from django.urls import reverse

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
