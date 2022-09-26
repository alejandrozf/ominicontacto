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
from mock import patch
from django.utils.translation import ugettext as _
from django.urls import reverse
from ominicontacto_app.tests.factories import (
    PausaFactory, ConfiguracionDePausaFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User, Pausa


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Pausas"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.pausa = PausaFactory(nombre='Pausa1', tipo='P')
        self.pausaConConfiguracion = PausaFactory(nombre='Pausa2', tipo='R')
        self.configuracionDePausa = ConfiguracionDePausaFactory(
            pausa=self.pausaConConfiguracion)
        self.dataForm = {
            'nombre': 'Nueva_Pausa',
            'tipo': 'P'
        }
        self.urls_api = {
            'PausesList': 'api_pauses_list',
            'PausesCreate': 'api_pauses_create',
            'PausesDetail': 'api_pauses_detail',
            'PausesUpdate': 'api_pauses_update',
            'PausesDelete': 'api_pauses_delete',
            'PausesReactivate': 'api_pauses_reactivate'
        }


class PausasTest(APITest):
    def test_listar_pausas(self):
        URL = reverse(self.urls_api['PausesList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron las pausas '
              'de forma exitosa'))

    def test_detalle_pausa(self):
        URL = reverse(
            self.urls_api['PausesDetail'],
            args=[self.pausa.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['pause']['id'], self.pausa.pk)
        self.assertEqual(
            response_json['pause']['nombre'],
            self.pausa.nombre)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion de la '
              'pausa de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionPausaAsterisk.regenerar_asterisk')
    def test_crear_pausa(self, regenerar_asterisk):
        URL = reverse(self.urls_api['PausesCreate'])
        numBefore = Pausa.objects.all().count()
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        numAfter = Pausa.objects.all().count()
        pausa = Pausa.objects.last()
        response_json = json.loads(response.content)
        regenerar_asterisk.assert_called_with(pausa)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la pausa '
              'de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionPausaAsterisk.eliminar_y_regenerar_asterisk')
    def test_elimina_pausa(self, eliminar_y_regenerar_asterisk):
        pk = self.pausa.pk
        self.pausa.eliminada = False
        self.pausa.save()
        URL = reverse(
            self.urls_api['PausesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        pausa = Pausa.objects.get(pk=pk)
        response_json = json.loads(response.content)
        eliminar_y_regenerar_asterisk.assert_called_with(pausa)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pausa.eliminada, True)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la pausa '
              'de forma exitosa'))

    def test_elimina_pausa_con_configuraciones(self):
        pk = self.pausaConConfiguracion.pk
        URL = reverse(
            self.urls_api['PausesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar un '
              'pausa con configuraciones creadas'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionPausaAsterisk.regenerar_asterisk')
    def test_actualiza_pausa(self, regenerar_asterisk):
        pk = self.pausa.pk
        URL = reverse(
            self.urls_api['PausesUpdate'],
            args=[pk, ])
        request_data = {
            'nombre': 'Edit_Pause',
            'tipo': 'R'
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        pausa = Pausa.objects.get(pk=pk)
        response_json = json.loads(response.content)
        regenerar_asterisk.assert_called_with(pausa)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pausa.nombre, request_data['nombre'])
        self.assertEqual(pausa.tipo, request_data['tipo'])
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo la pausa '
              'de forma exitosa'))

    def test_actualiza_pausa_con_nombre_repetido(self):
        pk = self.pausa.pk
        URL = reverse(
            self.urls_api['PausesUpdate'],
            args=[pk, ])
        request_data = {
            'nombre': 'Pausa2',
            'tipo': 'R'
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionPausaAsterisk.regenerar_asterisk')
    def test_reactiva_pausa(self, regenerar_asterisk):
        pk = self.pausa.pk
        self.pausa.eliminada = True
        self.pausa.save()
        URL = reverse(
            self.urls_api['PausesReactivate'],
            args=[pk, ])
        response = self.client.put(
            URL, follow=True)
        pausa = Pausa.objects.get(pk=pk)
        response_json = json.loads(response.content)
        regenerar_asterisk.assert_called_with(pausa)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pausa.eliminada, False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se reactivo la pausa '
              'de forma exitosa'))
