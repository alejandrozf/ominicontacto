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

import json
from django.utils.translation import ugettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    ConfiguracionDePausaFactory, ConjuntoDePausaFactory,
    GrupoFactory, PausaFactory)
from ominicontacto_app.models import User


class APITest(OMLBaseTest):
    """Tests para la API Conjuntos de Pausa"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        self.grupo = GrupoFactory(nombre='grupo_test')
        self.conjunto_de_pausa = ConjuntoDePausaFactory(nombre='conjunto_test')
        self.pausa1 = PausaFactory(nombre='pausa1')
        self.pausa2 = PausaFactory(nombre='pausa2')
        self.configuracion_de_pausa = ConfiguracionDePausaFactory(
            pausa=self.pausa1,
            conjunto_de_pausa=self.conjunto_de_pausa
        )

        self.urls_api = {
            'PauseSetsList': 'api_pause_set_list',
            'PauseSetCreate': 'api_pause_set_create',
            'PauseSetDetail': 'api_pause_set_detail',
            'PauseSetUpdate': 'api_pause_set_update',
            'PauseSetDelete': 'api_pause_set_delete'
        }


class ConjuntosDePausaTest(APITest):
    def test_lista_conjuntos_de_pausa(self):
        URL = reverse(self.urls_api['PauseSetsList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los conjuntos '
              'de pausas de forma exitosa'))

    def test_crea_conjunto_de_pausas(self):
        URL = reverse(self.urls_api['PauseSetCreate'])
        post_data = {
            'nombre': 'Conjunto Test',
            'pausas': [
                {
                    'pauseId': self.pausa1.pk,
                    'timeToEndPause': 123
                }
            ]
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo el conjunto de pausa de forma exitosa'))

    def test_crea_conjunto_de_pausas_sin_nombre(self):
        URL = reverse(self.urls_api['PauseSetCreate'])
        post_data = {
            'nombre': '',
            'pausas': [
                {
                    'pauseId': self.pausa1.pk,
                    'timeToEndPause': 123
                }
            ]
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('El nombre del conjunto es requerido'))

    def test_crea_conjunto_de_pausas_sin_pausas(self):
        URL = reverse(self.urls_api['PauseSetCreate'])
        post_data = {
            'nombre': 'Conjunto Test',
            'pausas': []
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('Debe existir al menos '
              'una pausa en el conjunto'))

    def test_actualiza_conjunto_de_pausas(self):
        URL = reverse(
            self.urls_api['PauseSetUpdate'],
            args=[self.conjunto_de_pausa.pk, ])
        post_data = {
            'nombre': 'Conjunto Test Update'
        }
        response = self.client.put(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo el conjunto de pausa de forma exitosa'))

    def test_actualiza_conjunto_de_pausas_sin_nombre(self):
        URL = reverse(
            self.urls_api['PauseSetUpdate'],
            args=[self.conjunto_de_pausa.pk, ])
        post_data = {
            'nombre': ''
        }
        response = self.client.put(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('El nombre del conjunto es requerido'))

    def test_elimina_conjunto_de_pausas_sin_grupo_de_agentes(self):
        URL = reverse(
            self.urls_api['PauseSetDelete'],
            args=[self.conjunto_de_pausa.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino el conjunto de pausa de forma exitosa'))

    def test_elimina_conjunto_de_pausas_con_grupo_de_agentes(self):
        self.grupo.conjunto_de_pausa = self.conjunto_de_pausa
        self.grupo.save()
        URL = reverse(
            self.urls_api['PauseSetDelete'],
            args=[self.conjunto_de_pausa.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No puedes borrar un conjunto de '
              'pausas que esta asignado a '
              'un grupo de agentes'))
