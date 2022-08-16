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
from configuracion_telefonia_app.models import DestinoEntrante, RutaEntrante
from configuracion_telefonia_app.tests.factories import (
    RutaEntranteFactory)
from ominicontacto_app.tests.factories import CampanaFactory
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User, Campana


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Rutas Entrantes"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        self.destino_campana_entrante = DestinoEntrante.crear_nodo_ruta_entrante(
            self.campana_entrante)
        self.ruta_entrante = RutaEntranteFactory(
            nombre='RutaEntrante1',
            telefono='2222222222',
            idioma=RutaEntrante.ES,
            destino=self.destino_campana_entrante)
        self.dataForm = {
            'nombre': 'RutaEntrante',
            'telefono': '5555555555',
            'idioma': RutaEntrante.EN,
            'prefijo_caller_id': None,
            'destino': {
                'id': self.destino_campana_entrante.id,
                'nombre': self.destino_campana_entrante.nombre,
                'tipo': self.destino_campana_entrante.tipo,
            }
        }
        self.urls_api = {
            'InboundRoutesList': 'api_inbound_routes_list',
            'InboundRoutesCreate': 'api_inbound_routes_create',
            'InboundRoutesDetail': 'api_inbound_routes_detail',
            'InboundRoutesUpdate': 'api_inbound_routes_update',
            'InboundRoutesDelete': 'api_inbound_routes_delete'
        }


class RutasEntrantesTest(APITest):
    def listar_rutas_entrantes(self):
        URL = reverse(self.urls_api['InboundRoutesList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron las rutas entrantes '
              'de forma exitosa'))

    def detalle_ruta_entrante(self):
        URL = reverse(
            self.urls_api['InboundRoutesDetail'],
            args=[self.ruta_entrante.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['inboundRoute']['id'], self.ruta_entrante.pk)
        self.assertEqual(
            response_json['inboundRoute']['nombre'],
            self.ruta_entrante.nombre)
        self.assertEqual(
            response_json['inboundRoute']['telefono'],
            self.ruta_entrante.telefono)
        self.assertEqual(
            response_json['inboundRoute']['prefijo_caller_id'],
            self.ruta_entrante.prefijo_caller_id)
        self.assertEqual(
            response_json['inboundRoute']['idioma'],
            self.ruta_entrante.idioma)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion de la '
              'ruta entrante de forma exitosa'))

    @patch('configuracion_telefonia_app.views.base'
           '.escribir_ruta_entrante_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionRutaEntranteAsterisk'
           '.regenerar_asterisk')
    def crear_ruta_entrante(
            self, regenerar_asterisk, escribir_ruta_entrante_config):
        URL = reverse(self.urls_api['InboundRoutesCreate'])
        numBefore = RutaEntrante.objects.all().count()
        response = self.client.post(
            URL, json.dumps(self.dataForm),
            format='json', content_type='application/json')
        numAfter = RutaEntrante.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la ruta entrante '
              'de forma exitosa'))

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionRutaEntranteAsterisk'
           '.eliminar_y_regenerar_asterisk')
    def elimina_ruta_entrante(self, eliminar_y_regenerar_asterisks):
        pk = self.ruta_entrante.pk
        URL = reverse(
            self.urls_api['InboundRoutesDelete'],
            args=[pk, ])
        numBefore = RutaEntrante.objects.all().count()
        response = self.client.delete(URL, follow=True)
        numAfter = RutaEntrante.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore - 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la ruta entrante '
              'de forma exitosa'))

    @patch('configuracion_telefonia_app.views.base'
           '.eliminar_ruta_entrante_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionRutaEntranteAsterisk'
           '.eliminar_y_regenerar_asterisk')
    @patch('configuracion_telefonia_app.views.base'
           '.escribir_ruta_entrante_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia'
           '.SincronizadorDeConfiguracionRutaEntranteAsterisk'
           '.regenerar_asterisk')
    def actualiza_ruta_entrante(
            self, regenerar_asterisk, escribir_ruta_entrante_config,
            eliminar_y_regenerar_asterisk, eliminar_ruta_entrante_config):
        pk = self.ruta_entrante.pk
        URL = reverse(
            self.urls_api['InboundRoutesUpdate'],
            args=[pk, ])
        request_data = {
            'nombre': 'RutaEntrante Edit',
            'telefono': '1234123412',
            'idioma': RutaEntrante.ES,
            'prefijo_caller_id': None,
            'destino': {
                'id': self.destino_campana_entrante.id,
                'nombre': self.destino_campana_entrante.nombre,
                'tipo': self.destino_campana_entrante.tipo,
            }
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        ruta_entrante = RutaEntrante.objects.get(pk=pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ruta_entrante.nombre, request_data['nombre'])
        self.assertEqual(ruta_entrante.telefono, request_data['telefono'])
        self.assertEqual(ruta_entrante.idioma, request_data['idioma'])
        self.assertEqual(
            ruta_entrante.prefijo_caller_id,
            request_data['prefijo_caller_id'])
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo la ruta entrante '
              'de forma exitosa'))
