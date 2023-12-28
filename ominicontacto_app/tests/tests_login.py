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
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.timezone import now
from mock import patch
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User
from reportes_app.models import ActividadAgenteLog


def request_host_port(request):
    return request.get_host(), request.get_port()


class LoginTests(OMLBaseTest):

    def setUp(self):
        super(LoginTests, self).setUp()
        self.agente = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)

    @patch('defender.utils.is_already_locked')
    @patch('defender.utils.check_request')
    @patch('defender.utils.add_login_attempt_to_db')
    def test_redirects_to_next_url_on_login(
            self, add_login_attempt_to_db, check_request, is_already_locked):
        self.supervisor.user.last_login = now()
        self.supervisor.user.save()
        is_already_locked.return_value = False
        check_request.return_value = True
        next_url = reverse('agente_list')
        login_url = reverse('login') + '?next=' + next_url
        login_data = {'username': self.supervisor.user.username, 'password': PASSWORD}
        response = self.client.post(login_url, login_data, follow=True)
        self.assertRedirects(response, next_url)

    @patch('defender.utils.is_already_locked')
    @patch('defender.utils.check_request')
    @patch('defender.utils.add_login_attempt_to_db')
    def test_redirects_to_change_password_on_first_login(
            self, add_login_attempt_to_db, check_request, is_already_locked):
        is_already_locked.return_value = False
        check_request.return_value = True
        next_url = reverse('agente_list')
        login_url = reverse('login') + '?next=' + next_url
        login_data = {'username': self.supervisor.user.username, 'password': PASSWORD}
        response = self.client.post(login_url, login_data, follow=True)
        self.assertRedirects(response, reverse('user_change_password'))

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    def test_redirects_agent_to_agent_view(self, generar_sip_password, generar_sip_user):
        self.client.login(username=self.agente.user.username, password=PASSWORD)
        index_url = reverse('index')
        consola_agente_url = reverse('consola_de_agente')
        response = self.client.get(index_url, follow=True)
        self.assertRedirects(response, consola_agente_url)

    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_user')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    @patch('utiles_globales.obtener_request_host_port', request_host_port)
    @patch('defender.utils.is_already_locked')
    @patch('defender.utils.check_request')
    @patch('defender.utils.add_login_attempt_to_db')
    def test_logs_agent_login(
            self, add_login_attempt_to_db, check_request, is_already_locked,
            generar_sip_password, generar_sip_user):
        cant_logs = ActividadAgenteLog.objects.count()
        is_already_locked.return_value = False
        check_request.return_value = True
        consola_agente_url = reverse('consola_de_agente')
        login_url = reverse('login')
        login_data = {'username': self.agente.user.username, 'password': PASSWORD}
        response = self.client.post(login_url, login_data, follow=True)
        self.assertRedirects(response, consola_agente_url)
        self.assertEqual(ActividadAgenteLog.objects.count(), cant_logs + 1)
        log = ActividadAgenteLog.objects.last()
        self.assertEqual(log.agente_id, self.agente.id)
        self.assertEqual(log.event, ActividadAgenteLog.LOGIN)
