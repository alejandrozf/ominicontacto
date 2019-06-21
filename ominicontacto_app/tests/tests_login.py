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
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from mock import patch
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD


class LoginTests(OMLBaseTest):

    def setUp(self):
        self.agente = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile()

    @patch('defender.utils.is_already_locked')
    @patch('defender.utils.check_request')
    @patch('defender.utils.add_login_attempt_to_db')
    def test_redirects_to_next_url_on_login(
            self, add_login_attempt_to_db, check_request, is_already_locked):
        is_already_locked.return_value = False
        check_request.return_value = True
        next_url = reverse('agente_list')
        login_url = reverse('login') + '?next=' + next_url
        login_data = {'username': self.supervisor.user.username, 'password': PASSWORD}
        response = self.client.post(login_url, login_data, follow=True)
        self.assertRedirects(response, next_url)

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    def test_redirects_agent_to_agent_view(self, generar_sip_password, generar_sip_user):
        self.client.login(username=self.agente.user.username, password=PASSWORD)
        index_url = reverse('index')
        consola_agente_url = reverse('consola_de_agente')
        response = self.client.get(index_url, follow=True)
        self.assertRedirects(response, consola_agente_url)
