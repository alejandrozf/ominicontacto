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
Tests relacionados a los Grupos de Agentes
"""
from __future__ import unicode_literals
from mock import patch
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    GrupoFactory, CampanaFactory, QueueFactory, ActividadAgenteLogFactory)
from ominicontacto_app.models import (
    Campana)


def request_host_port(request):
    return request.get_host(), request.get_port()


class TestConsolaAgente (OMLBaseTest):
    def setUp(self, *args, **kwargs):
        super(TestConsolaAgente, self).setUp(*args, **kwargs)
        self.url = reverse('consola_de_agente')
        self.grupo = GrupoFactory(nombre='grupo_test')
        self.usr_agente = self.crear_user_agente(username='agente1')
        self.usr_agente.set_password(PASSWORD)
        self.agente = self.crear_agente_profile(self.usr_agente)
        self.agente.grupo = self.grupo
        self.agente.save()
        self.client.login(username=self.agente.user.username, password=PASSWORD)
        ActividadAgenteLogFactory(agente_id=self.agente.id, event='ADDMEMBER')
        self.campana_preview = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                     type=Campana.TYPE_PREVIEW)
        self.queue = QueueFactory.create(campana=self.campana_preview)
        self._hacer_miembro(self.agente, self.campana_preview)

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_show_console_timers(self, generar_sip_password, generar_sip_user):
        self.grupo.show_console_timers = True
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, '<div id="operationTime" class="label label-default">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_hidden_console_timers(self, generar_sip_password, generar_sip_user):
        self.grupo.show_console_timers = False
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, '<div id="operationTime" class="label label-default">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_show_contactos_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_contactos_agente = True
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<ul class="collapse list-unstyled submenu" id="menuContacts"')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_hidden_contactos_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_contactos_agente = False
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(
            response,
            '<ul class="collapse list-unstyled submenu" id="menuContacts"')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_show_agendas_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_agendas_agente = True
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<a class="menu-link" href="/agenda_contacto/eventos/" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_hidden_agendas_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_agendas_agente = False
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(
            response,
            '<a class="menu-link" href="/agenda_contacto/eventos/" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_show_calificaciones_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_calificaciones_agente = True
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<a class="menu-link" href="/agente/reporte/calificaciones/" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_hidden_calificaciones_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_calificaciones_agente = False
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(
            response,
            '<a class="menu-link" href="/agente/reporte/calificaciones/" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_show_campanas_preview_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_campanas_preview_agente = True
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<a class="menu-link" href="/agente/campanas_preview/activas" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_hidden_campanas_preview_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_campanas_preview_agente = False
        self.grupo.save()
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(
            response,
            '<a class="menu-link" href="/agente/campanas_preview/activas" target="crm">')

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_allows_cambiar_contrasena_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_cambiar_contrasena_agente = True
        self.grupo.save()
        response = self.client.get(reverse('update_agent_password'))
        self.assertEqual(response.status_code, 200)

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_forbid_cambiar_contrasena_agente(self, generar_sip_password, generar_sip_user):
        self.grupo.acceso_cambiar_contrasena_agente = False
        self.grupo.save()
        response = self.client.get(reverse('update_agent_password'))
        self.assertEqual(response.status_code, 403)
