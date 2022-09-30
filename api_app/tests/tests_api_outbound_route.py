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
from configuracion_telefonia_app.models import RutaSaliente
from configuracion_telefonia_app.tests.factories import (
    OrdenTroncalFactory,
    PatronDeDiscadoFactory,
    RutaSalienteFactory,
    TroncalSIPFactory)
from ominicontacto_app.tests.factories import CampanaFactory
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User, Campana


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Rutas Salientes"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.troncal1 = TroncalSIPFactory()
        self.troncal2 = TroncalSIPFactory()
        self.ruta_saliente = RutaSalienteFactory()
        self.ruta_saliente_con_campana = RutaSalienteFactory()
        self.patron_de_discado = PatronDeDiscadoFactory(
            ruta_saliente=self.ruta_saliente, match_pattern="ZXXXXXXXXX")
        self.orden_trocal = OrdenTroncalFactory(
            ruta_saliente=self.ruta_saliente, troncal=self.troncal1)
        self.campana = CampanaFactory(
            type=Campana.TYPE_ENTRANTE, outr=self.ruta_saliente_con_campana)
        self.dataForm = {
            "nombre": "RutaSaliente",
            "ring_time": 30,
            "dial_options": "Tt",
            "patrones_de_discado": [
                {
                    "id": None,
                    "prepend": None,
                    "prefix": None,
                    "match_pattern": "ZXXXXXXXXX"
                }
            ],
            "troncales": [
                {
                    "id": None,
                    "troncal": self.troncal1.id
                }
            ]
        }
        self.dataSinPatronesDeDiscado = {
            "nombre": "RutaSaliente",
            "ring_time": 30,
            "dial_options": "Tt",
            "troncales": [
                {
                    "id": None,
                    "troncal": self.troncal1.id
                }
            ]
        }
        self.dataSinTroncal = {
            "nombre": "RutaSaliente",
            "ring_time": 30,
            "dial_options": "Tt",
            "patrones_de_discado": [
                {
                    "id": None,
                    "prepend": None,
                    "prefix": None,
                    "match_pattern": "ZXXXXXXXXX"
                }
            ]
        }
        self.urls_api = {
            'OutboundRoutesList': 'api_outbound_routes_list',
            'OutboundRoutesCreate': 'api_outbound_routes_create',
            'OutboundRoutesDetail': 'api_outbound_routes_detail',
            'OutboundRoutesUpdate': 'api_outbound_routes_update',
            'OutboundRoutesDelete': 'api_outbound_routes_delete'
        }


class RutasSalientesTest(APITest):
    def test_listar_rutas_salientes(self):
        URL = reverse(self.urls_api['OutboundRoutesList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron las rutas entrantes '
              'de forma exitosa'))

    def test_detalle_ruta_saliente(self):
        URL = reverse(
            self.urls_api['OutboundRoutesDetail'],
            args=[self.ruta_saliente.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['outboundRoute']['id'], self.ruta_saliente.pk)
        self.assertEqual(
            response_json['outboundRoute']['nombre'],
            self.ruta_saliente.nombre)
        self.assertEqual(
            response_json['outboundRoute']['ring_time'],
            self.ruta_saliente.ring_time)
        self.assertEqual(
            response_json['outboundRoute']['dial_options'],
            self.ruta_saliente.dial_options)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion de la '
              'ruta saliente de forma exitosa'))

    @patch('api_app.utils.routes.outbound.escribir_ruta_saliente_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk'
           '.regenerar_asterisk')
    def test_crear_ruta_saliente(self, regenerar_asterisk, escribir_ruta_saliente_config):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        numBefore = RutaSaliente.objects.all().count()
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        numAfter = RutaSaliente.objects.all().count()
        ruta = RutaSaliente.objects.last()
        regenerar_asterisk.assert_called_with(ruta)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la ruta saliente '
              'de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk'
           '.eliminar_y_regenerar_asterisk')
    def test_elimina_ruta_saliente(self, eliminar_y_regenerar_asterisk):
        pk = self.ruta_saliente.pk
        URL = reverse(
            self.urls_api['OutboundRoutesDelete'],
            args=[pk, ])
        numBefore = RutaSaliente.objects.all().count()
        response = self.client.delete(URL, follow=True)
        numAfter = RutaSaliente.objects.all().count()
        eliminar_y_regenerar_asterisk.assert_called()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore - 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la ruta saliente '
              'de forma exitosa'))

    def test_elimina_ruta_saliente_con_campana(self):
        pk = self.ruta_saliente_con_campana.pk
        URL = reverse(
            self.urls_api['OutboundRoutesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar una '
              'ruta saliente asociada a una campaña'))

    def test_validar_orden_de_troncales_nulas(self):
        self.dataSinTroncal['troncales'] = [
            {
                "id": None,
                "troncal": None
            }
        ]
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        response = self.client.post(
            URL, json.dumps(self.dataSinTroncal),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['troncales'],
            [{"troncal": ["Este campo no puede ser nulo."]}])

    def test_validar_orden_de_troncales_repetidas(self):
        self.dataSinTroncal['troncales'] = [
            {
                "id": None,
                "troncal": self.troncal1.id
            },
            {
                "id": None,
                "troncal": self.troncal1.id
            }
        ]
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        response = self.client.post(
            URL, json.dumps(self.dataSinTroncal),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['troncales'],
            ['Las troncales deben ser diferentes'])

    def test_validar_troncales_nulas(self):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        self.dataSinTroncal['troncales'] = None
        response = self.client.post(
            URL, json.dumps(self.dataSinTroncal),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['troncales'],
            ["Este campo no puede ser nulo."])

    def test_validar_troncales_minimas(self):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        self.dataSinTroncal['troncales'] = []
        response = self.client.post(
            URL, json.dumps(self.dataSinTroncal),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['troncales'],
            ["Debe existir al menos una troncal"])

    def test_validar_patrones_de_discado_nulos(self):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        self.dataSinPatronesDeDiscado['patrones_de_discado'] = None
        response = self.client.post(
            URL, json.dumps(self.dataSinPatronesDeDiscado),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['patrones_de_discado'],
            ["Este campo no puede ser nulo."])

    def test_validar_patrones_de_discado_minimos(self):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        self.dataSinPatronesDeDiscado['patrones_de_discado'] = []
        response = self.client.post(
            URL, json.dumps(self.dataSinPatronesDeDiscado),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['patrones_de_discado'],
            ["Debe existir al menos un patron de discado"])

    def test_validar_patrones_de_discado_repetidos(self):
        URL = reverse(self.urls_api['OutboundRoutesCreate'])
        self.dataSinPatronesDeDiscado['patrones_de_discado'] = [
            {
                "id": None,
                "prepend": None,
                "prefix": None,
                "match_pattern": "ZXXXXXXXXX"
            },
            {
                "id": None,
                "prepend": None,
                "prefix": None,
                "match_pattern": "ZXXXXXXXXX"
            }
        ]
        response = self.client.post(
            URL, json.dumps(self.dataSinPatronesDeDiscado),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['errors']['patrones_de_discado'],
            ["Los patrones de discado deben ser diferentes"])

    @patch('api_app.utils.routes.outbound.escribir_ruta_saliente_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk'
           '.regenerar_asterisk')
    def test_actualiza_ruta_saliente(self, regenerar_asterisk, escribir_ruta_saliente_config):
        pk = self.ruta_saliente.pk
        URL = reverse(
            self.urls_api['OutboundRoutesUpdate'],
            args=[pk, ])
        request_data = {
            "nombre": "RutaSalienteEdit",
            "ring_time": 50,
            "dial_options": "Tt",
            "patrones_de_discado": [
                {
                    "id": None,
                    "prepend": None,
                    "prefix": None,
                    "match_pattern": "ZYXXXXX"
                }
            ],
            "troncales": [
                {
                    "id": None,
                    "troncal": self.troncal2.id
                }
            ]
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        ruta_saliente = RutaSaliente.objects.get(pk=pk)
        response_json = json.loads(response.content)
        regenerar_asterisk.assert_called_with(ruta_saliente)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ruta_saliente.nombre, request_data['nombre'])
        self.assertEqual(ruta_saliente.ring_time, request_data['ring_time'])
        self.assertEqual(ruta_saliente.dial_options, request_data['dial_options'])
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo la ruta saliente '
              'de forma exitosa'))
