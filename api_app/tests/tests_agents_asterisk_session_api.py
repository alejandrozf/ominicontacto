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
from __future__ import unicode_literals

from mock import patch

# from django.utils.translation import gettext as _
from django.urls import reverse

from ominicontacto_app.tests.factories import PausaFactory
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.utiles import PASSWORD


class AgentsAsteriskSessionAPITest(OMLBaseTest):

    def setUp(self):
        super(AgentsAsteriskSessionAPITest, self).setUp()
        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)
        url = reverse('api_login')
        post_data = {'username': self.agente.user.username, 'password': PASSWORD}
        response = self.client.post(url, post_data)
        self.auth_header = 'Bearer ' + response.json()['token']
        self.pausa = PausaFactory(nombre='pausa')

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.login_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_login_ok(self, connect_manager, disconnect_manager, login_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        login_agent.return_value = False
        url = reverse('api_agent_asterisk_login')
        response = self.client.post(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'OK')
        login_agent.assert_called_once_with(self.agente, manage_connection=True)

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.login_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_login_error(self, connect_manager, disconnect_manager, login_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        login_agent.return_value = True
        url = reverse('api_agent_asterisk_login')
        response = self.client.post(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'ERROR')
        login_agent.assert_called_once_with(self.agente, manage_connection=True)

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'logout_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_logout_ok(self, connect_manager, disconnect_manager, logout_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        logout_agent.return_value = False, False
        url = reverse('api_agent_asterisk_logout')
        response = self.client.post(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'OK')
        logout_agent.assert_called_once_with(self.agente, manage_connection=True)

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'logout_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_logout_error(self, connect_manager, disconnect_manager, logout_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        logout_agent.return_value = False, True
        url = reverse('api_agent_asterisk_logout')
        response = self.client.post(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'ERROR')
        logout_agent.assert_called_once_with(self.agente, manage_connection=True)

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'pause_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_pause_agent(self, connect_manager, disconnect_manager, pause_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        pause_agent.return_value = False, False
        url = reverse('api_make_pause')
        response = self.client.post(url, data={'pause_id': self.pausa.id},
                                    HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'OK')
        pause_agent.assert_called_once_with(self.agente, str(self.pausa.id), manage_connection=True)

    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'unpause_agent')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'disconnect_manager')
    @patch('ominicontacto_app.services.asterisk.agent_activity.AgentActivityAmiManager.'
           'connect_manager')
    def test_asterisk_session_unpause_agent(self, connect_manager, disconnect_manager,
                                            unpause_agent):
        connect_manager.return_value = False
        disconnect_manager.return_value = False
        unpause_agent.return_value = False, False
        url = reverse('api_make_unpause')
        response = self.client.post(url, data={'pause_id': self.pausa.id},
                                    HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'OK')
        unpause_agent.assert_called_once_with(self.agente, str(self.pausa.id),
                                              manage_connection=True)
