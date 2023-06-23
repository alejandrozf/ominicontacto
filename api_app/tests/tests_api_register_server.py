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
from __future__ import unicode_literals

import json
from mock import patch
from django.utils.translation import gettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User
from constance import config


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Registro"""

    def setUp(self):
        super(APITest, self).setUp()
        self.admin = self.crear_administrador()
        self.sup = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=self.sup, rol=User.SUPERVISOR)
        self.dataForm = {
            'client': 'Test Client',
            'password': 'asdf1324..#$',
            'email': 'test@gmail.com',
            'phone': '5555555555'
        }


class RegisterServerTest(APITest):
    def test_obtener_detalle_del_registro(self):
        self.client.login(username=self.admin.username, password=PASSWORD)
        URL = reverse('api_register_server_detail')
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo el registro del servidor forma exitosa'))

    @patch('api_app.serializers.register_server'
           '.RegisterServerSerializer._create_credentials')
    def test_crear_registro(self, _create_credentials):
        self.client.login(username=self.admin.username, password=PASSWORD)
        URL = reverse('api_register_server_create')
        _create_credentials.return_value = {
            "status": "OK", "msg": "Credentials created",
            "user_name": self.dataForm['client'],
            "user_key": config.CLIENT_KEY,
            "user_email": self.dataForm['email'],
            "user_phone": self.dataForm['phone'],
            "user_password": self.dataForm['password'],
        }
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(config.CLIENT_NAME, self.dataForm['client'])
        self.assertEqual(config.CLIENT_PASSWORD, self.dataForm['password'])
        self.assertEqual(config.CLIENT_EMAIL, self.dataForm['email'])
        self.assertEqual(config.CLIENT_PHONE, self.dataForm['phone'])
        self.assertEqual(
            response_json['message'],
            _('Se creo el registro al servidor '
              'de forma exitosa'))

    def test_obtener_detalle_del_registro_como_sup(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        URL = reverse('api_register_server_detail')
        response = self.client.get(URL, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_crear_registro_como_sup(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        URL = reverse('api_register_server_create')
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        self.assertEqual(response.status_code, 403)
