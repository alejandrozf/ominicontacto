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
Tests relacionados a los Grupos de Agentes
"""
from __future__ import unicode_literals
from mock import patch
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import GrupoFactory


def request_host_port(request):
    return request.get_host(), request.get_port()


class TestConsolaAgente (OMLBaseTest):
    def setUp(self, *args, **kwargs):
        super(TestConsolaAgente, self).setUp(*args, **kwargs)
        self.url = reverse('index')
        self.grupo = GrupoFactory(nombre='grupo_test')
        self.usr_agente = self.crear_user_agente(username='agente1')
        self.usr_agente.set_password(PASSWORD)
        self.agente = self.crear_agente_profile(self.usr_agente)
        self.agente.grupo = self.grupo
        self.agente.save()
        self.client.login(username=self.agente.user.username, password=PASSWORD)

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
