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
import requests

from mock import patch

from django.urls import reverse

from constance import config

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD


class RegistroTest(OMLBaseTest):
    ejecutar_actualizar_permisos = True

    def setUp(self):
        super(RegistroTest, self).setUp()
        self.usuario_agente = self.crear_agente_profile().user
        self.usuario_admin = self.crear_administrador()
        self.client.login(username=self.usuario_agente.username, password=PASSWORD)

    def test_usuario_no_administrador_no_puede_registrar_instancia(self):
        url = reverse('registrar_usuario')
        post_data = {
            'nombre': 'test-nombre',
            'email': 'test@test.com.ar',
            'telefono': '+54 9 333 7777',
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, '403.html')

    @patch('requests.post')
    def test_usuario_no_administrador_puede_acceder_al_registro_de_su_instancia(self, post):
        self.client.logout()
        self.client.login(username=self.usuario_admin.username, password=PASSWORD)
        url = reverse('registrar_usuario')
        response = requests.models.Response()
        response.status_code = 200
        response._content = json.dumps({"status": "OK", "msg": "Credentials created",
                                        "user_name": config.CLIENT_NAME,
                                        "user_key": config.CLIENT_KEY,
                                        "user_email": config.CLIENT_EMAIL,
                                        "user_phone": config.CLIENT_PHONE})
        post.return_value = response
        post_data = {
            'nombre': 'test-nombre',
            'email': 'test@test.com.ar',
            'telefono': '+54 9 333 7777',
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateUsed(response, 'registro.html')
