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
from django.urls import reverse
from ominicontacto_app.tests.factories import GrupoFactory
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User


class APITest(OMLBaseTest):
    """Tests para los Endpoint de Enviar mensaje a Agentes"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)
        self.campana_entrante = self.crear_campana_manual()
        self.grupo = GrupoFactory(nombre='grupo_test')
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.urls_api = {
            'EnviarMensaje': 'api_enviar_mensaje_agentes'
        }


class EnviarMensajeTest(APITest):

    def test_api_enviar_mensaje_agente(self):
        URL = reverse(
            self.urls_api['EnviarMensaje'])
        dataForm = {
            'recipient-type': 'agent',
            'recipient_id': self.agente.id
        }
        response = self.client.post(URL, json.dumps(dataForm),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_enviar_mensaje_group(self):
        URL = reverse(self.urls_api['EnviarMensaje'])
        dataForm = {
            'recipient-type': 'group',
            'recipient_id': self.grupo.id
        }
        response = self.client.post(URL, json.dumps(dataForm),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_enviar_mensaje_campaign(self):
        URL = reverse(self.urls_api['EnviarMensaje'])
        dataForm = {
            'recipient-type': 'campaign',
            'recipient_id': self.campana_entrante.id
        }
        response = self.client.post(URL, json.dumps(dataForm),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
