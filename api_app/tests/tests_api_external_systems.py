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
from django.utils.translation import gettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    SistemaExternoFactory, AgenteProfileFactory, AgenteEnSistemaExternoFactory)
from ominicontacto_app.models import SistemaExterno, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Sistemas Externos"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.agente_profile_1 = AgenteProfileFactory()
        self.agente_profile_2 = AgenteProfileFactory()
        self.sistema_externo = SistemaExternoFactory()
        self.agente_en_sistema_1 = AgenteEnSistemaExternoFactory(
            sistema_externo=self.sistema_externo, agente=self.agente_profile_1)
        self.urls_api = {
            'ExternalSystemList': 'api_external_systems_list',
            'ExternalSystemCreate': 'api_external_systems_create',
            'ExternalSystemUpdate': 'api_external_systems_update',
            'ExternalSystemDetail': 'api_external_systems_detail'
        }


class SistemasExternosTest(APITest):
    def test_lista_sistemas_externos(self):
        URL = reverse(self.urls_api['ExternalSystemList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los sistemas externos '
              'de forma exitosa'))

    def test_detalle_sistema_externo(self):
        URL = reverse(
            self.urls_api['ExternalSystemDetail'],
            args=[self.sistema_externo.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['externalSystem']['id'], self.sistema_externo.pk)
        self.assertEqual(
            response_json['externalSystem']['nombre'],
            self.sistema_externo.nombre)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion del '
              'sistema externo de forma exitosa'))

    def test_crea_sistema_externo(self):
        URL = reverse(self.urls_api['ExternalSystemCreate'])
        post_data = {
            'nombre': 'External System New',
            'agentes': [
                {
                    "id_externo_agente": "ID 1",
                    "agente": self.agente_profile_1.pk
                },
                {
                    "id_externo_agente": "ID 2",
                    "agente": self.agente_profile_2.pk
                }
            ]
        }
        numBefore = SistemaExterno.objects.all().count()
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        numAfter = SistemaExterno.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo el sistema externo '
              'de forma exitosa'))

    def test_actualiza_sistema_externo(self):
        URL = reverse(
            self.urls_api['ExternalSystemUpdate'],
            args=[self.sistema_externo.pk, ])
        request_data = {
            'nombre': 'External Systema Edit',
            'agentes': [
                {
                    "id": self.agente_en_sistema_1.pk,
                    "id_externo_agente": "ID Edit",
                    "agente": self.agente_en_sistema_1.agente.pk
                },
                {
                    "id_externo_agente": "ID New 2",
                    "agente": self.agente_profile_2.pk
                }
            ]
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        sistema = SistemaExterno.objects.get(pk=self.sistema_externo.pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sistema.nombre, request_data['nombre'])
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo el sistema externo '
              'de forma exitosa'))
