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
    ConfiguracionDePausaFactory, ConjuntoDePausaFactory, PausaFactory
)
from ominicontacto_app.models import User


class APITest(OMLBaseTest):
    """ Tests para la API Configuraciones de Pausa"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        self.conjunto_de_pausa = ConjuntoDePausaFactory(nombre='grupo')
        self.pausa = PausaFactory(nombre='pausa')
        self.configuracion_de_pausa = ConfiguracionDePausaFactory(
            pausa=self.pausa,
            conjunto_de_pausa=self.conjunto_de_pausa
        )

        self.urls_api = {
            'PauseConfigCreate': 'api_pause_config_create',
            'PauseConfigUpdate': 'api_pause_config_update',
            'PauseConfigDelete': 'api_pause_config_delete'
        }


class ConfiguracionesDePausasTest(APITest):
    def test_crear_configuracion_de_pausa(self):
        URL = reverse(self.urls_api['PauseConfigCreate'])
        post_data = {
            'pauseId': self.pausa.pk,
            'setId': self.conjunto_de_pausa.pk,
            'timeToEndPause': 125
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la configuracion '
              'de pausa de forma exitosa'))

    def test_actualiza_configuracion_de_pausa(self):
        URL = reverse(
            self.urls_api['PauseConfigUpdate'],
            args=[self.configuracion_de_pausa.pk, ])
        post_data = {
            'timeToEndPause': 100
        }
        response = self.client.put(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo la configuracion '
              'de pausa de forma exitosa'))

    def test_eliminar_configuracion_de_pausa(self):
        pausa = PausaFactory(nombre='pausa2')
        configuracion_de_pausa = ConfiguracionDePausaFactory(
            pausa=pausa,
            conjunto_de_pausa=self.conjunto_de_pausa
        )
        URL = reverse(
            self.urls_api['PauseConfigDelete'],
            args=[configuracion_de_pausa.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la configuracion '
              'de pausa de forma exitosa'))

    def test_tiempos_negativos_en_configuracion_de_pausa(self):
        URL = reverse(self.urls_api['PauseConfigCreate'])
        pausa = PausaFactory(nombre='pausa2')
        post_data = {
            'pauseId': pausa.pk,
            'setId': self.conjunto_de_pausa.pk,
            'timeToEndPause': -123
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('El timeout debe ser mayor a cero'))

    def test_no_puede_existir_conjunto_de_pausa_vacio(self):
        URL = reverse(
            self.urls_api['PauseConfigDelete'],
            args=[self.configuracion_de_pausa.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No puedes dejar a un '
              'Conjunto de Pausas vacio'))
