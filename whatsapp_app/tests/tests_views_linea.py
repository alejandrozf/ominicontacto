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

from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import User
from ominicontacto_app.tests.utiles import PASSWORD
from whatsapp_app.tests.factories import (
    LineaFactory, ConfiguracionProveedorFactory, MenuInteractivoFactory, )
from whatsapp_app.models import (Linea, ConfiguracionProveedor, MenuInteractivoWhatsapp,
                                 OpcionMenuInteractivoWhatsapp, )
from configuracion_telefonia_app.models import DestinoEntrante, OpcionDestino


class LineaTest(OMLBaseTest):
    def setUp(self):
        super(LineaTest, self).setUp()
        # self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        self.campana = self.crear_campana_entrante()
        self.destino_1 = DestinoEntrante.crear_nodo_ruta_entrante(self.campana)
        self.campana_2 = self.crear_campana_entrante()
        self.destino_2 = DestinoEntrante.crear_nodo_ruta_entrante(self.campana_2)
        self.campana_3 = self.crear_campana_entrante()
        self.destino_3 = DestinoEntrante.crear_nodo_ruta_entrante(self.campana_3)
        self.campana.whatsapp_habilitado = True
        self.campana_2.whatsapp_habilitado = True
        self.campana_3.whatsapp_habilitado = True
        self.campana.save()
        self.campana_2.save()
        self.campana_3.save()
        self.proveedor_gupshup = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP)

        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_configuracion_linea_forbidden(self):
        self.client.logout()
        url_list = reverse('whatsapp_app:linea-list')
        response_linea_list = self.client.get(url_list)
        response_linea_create = self.client.post(url_list)
        linea = LineaFactory()
        url_details = reverse('whatsapp_app:linea-detail', args=[linea.pk])
        response_linea_update = self.client.put(url_details)
        response_linea_detail = self.client.get(url_details)
        response_linea_delete = self.client.delete(url_details)
        self.assertEqual(response_linea_list.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_linea_create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_linea_update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_linea_detail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_linea_delete.status_code, status.HTTP_403_FORBIDDEN)

    def crear_linea_a_campana(self):
        self.linea_a_campana = LineaFactory(nombre='Linea1',
                                            proveedor=self.proveedor_gupshup,
                                            destino=self.destino_1)

    def crear_linea_a_menu(self):
        self.menu = MenuInteractivoFactory()
        self.destino_menu = DestinoEntrante.crear_nodo_ruta_entrante(self.menu)
        self.opcion_destino_1 = OpcionDestino.crear_opcion_destino(
            destino_anterior=self.destino_menu, destino_siguiente=self.destino_1,
            valor='Campana 1')
        self.opcion_menu_1 = OpcionMenuInteractivoWhatsapp.objects.create(
            opcion=self.opcion_destino_1, descripcion='Descripcion opcion 1')
        self.opcion_destino_2 = OpcionDestino.crear_opcion_destino(
            destino_anterior=self.destino_menu, destino_siguiente=self.destino_2,
            valor='Campana 2')
        self.opcion_menu_2 = OpcionMenuInteractivoWhatsapp.objects.create(
            opcion=self.opcion_destino_2, descripcion='Descripcion opcion 2')
        self.opcion_destino_3 = OpcionDestino.crear_opcion_destino(
            destino_anterior=self.destino_menu, destino_siguiente=self.destino_3,
            valor='Campana 3')
        self.opcion_menu_3 = OpcionMenuInteractivoWhatsapp.objects.create(
            opcion=self.opcion_destino_3, descripcion='Descripcion opcion 3')

        self.linea_a_menu = LineaFactory(nombre='Linea1',
                                         proveedor=self.proveedor_gupshup,
                                         destino=self.destino_menu)

    def test_configuracion_linea_list(self):
        self.crear_linea_a_campana()
        self.crear_linea_a_menu()
        url = reverse('whatsapp_app:linea-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()['data']
        self.assertEqual(len(response_data), 2)
        expected_data_linea_a_campana = {
            'id': self.linea_a_campana.id,
            'name': self.linea_a_campana.nombre,
            'number': self.linea_a_campana.numero,
            'provider': self.proveedor_gupshup.id,
            'configuration': self.proveedor_gupshup.configuracion,
        }
        expected_data_linea_a_menu = {
            'id': self.linea_a_menu.id,
            'name': self.linea_a_menu.nombre,
            'number': self.linea_a_menu.numero,
            'provider': self.proveedor_gupshup.id,
            'configuration': self.proveedor_gupshup.configuracion,
        }
        self.assertIn(expected_data_linea_a_campana, response_data)
        self.assertIn(expected_data_linea_a_menu, response_data)

    def test_configuracion_linea_a_campana_detail(self):
        self.crear_linea_a_campana()
        self.crear_linea_a_menu()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_campana.id])
        response_linea_detail = self.client.get(url)
        self.assertEqual(response_linea_detail.status_code, status.HTTP_200_OK)
        response_data = response_linea_detail.json()['data']
        self.assertEqual(response_data['id'], self.linea_a_campana.id)
        self.assertEqual(response_data['name'], self.linea_a_campana.nombre)
        self.assertEqual(response_data['number'], self.linea_a_campana.numero)
        self.assertEqual(response_data['provider'], self.linea_a_campana.proveedor.id)
        self.assertEqual(response_data['configuration'], self.linea_a_campana.configuracion)
        self.assertEqual(response_data['destination_type'], DestinoEntrante.CAMPANA)

    def test_creacion_linea_gupshup_con_destino_campana(self):
        num_lineas = Linea.objects.count()
        proveedor = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP)
        url = reverse('whatsapp_app:linea-list')
        data = {
            'name': 'linea1',
            'number': '43332221',
            'provider': proveedor.id,
            'configuration': {'app_name': 'LineaAppName', 'app_id': 'LineaAppId'},
            'destination': {
                'type': DestinoEntrante.CAMPANA,
                'data': self.campana.id,
            }
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(Linea.objects.count(), num_lineas + 1)
        linea = Linea.objects.get(id=response_data['data']['id'])
        self.assertEqual(linea.proveedor, proveedor)
        self.assertEqual(linea.destino.tipo, DestinoEntrante.CAMPANA)
        self.assertEqual(linea.destino, DestinoEntrante.get_nodo_ruta_entrante(self.campana))
        self.assertEqual(response_data['data']['destination']['id'], self.campana.id)

    def get_menu_post_data(self):
        return {
            'name': 'linea1',
            'number': '43332221',
            'provider': self.proveedor_gupshup.id,
            'destination': {
                'type': DestinoEntrante.MENU_INTERACTIVO_WHATSAPP,
                'data': {
                    'text': 'Texto menu. "Dos" para Campana 2 y "Tres" para campana 3',
                    'wrong_answer': 'Opcion incorecta',
                    'success': 'Redirigiendo',
                    'timeout': 300,
                    'options': [{
                        'value': 'Dos',
                        'description': 'A campana 2',
                        'destination': self.campana_2.id,
                    }, {
                        'value': 'Tres',
                        'description': 'A campana 3',
                        'destination': self.campana_3.id,
                    }],
                },
            },
            'configuration': {'app_name': 'LineaAppName', 'app_id': 'LineaAppId'},
        }

    def test_creacion_linea_gupshup_con_destino_menu_interactivo(self):
        num_lineas = Linea.objects.count()
        num_menu = MenuInteractivoWhatsapp.objects.count()
        num_opcion = OpcionMenuInteractivoWhatsapp.objects.count()
        num_opcion_destino = OpcionDestino.objects.count()
        url = reverse('whatsapp_app:linea-list')
        data = self.get_menu_post_data()
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(Linea.objects.count(), num_lineas + 1)
        self.assertEqual(MenuInteractivoWhatsapp.objects.count(), num_menu + 1)
        self.assertEqual(OpcionMenuInteractivoWhatsapp.objects.count(), num_opcion + 2)
        self.assertEqual(OpcionDestino.objects.count(), num_opcion_destino + 2)
        linea = Linea.objects.get(nombre=data['name'])
        self.assertEqual(linea.proveedor, self.proveedor_gupshup)
        self.assertEqual(linea.destino.tipo, DestinoEntrante.MENU_INTERACTIVO_WHATSAPP)
        menu_id = response_data['data']['destination']['id']
        menu = MenuInteractivoWhatsapp.objects.get(id=menu_id)
        self.assertEqual(linea.destino, DestinoEntrante.get_nodo_ruta_entrante(menu))
        self.assertEqual(2, linea.destino.destinos_siguientes.count())
        opcion_2 = linea.destino.get_opcion_destino_por_valor('Dos')
        self.assertEqual(opcion_2.destino_siguiente, self.destino_2)
        opcion_3 = linea.destino.get_opcion_destino_por_valor('Tres')
        self.assertEqual(opcion_3.destino_siguiente, self.destino_3)

    def test_creacion_linea_gupshup_con_menu_interactivo_errors(self):
        num_lineas = Linea.objects.count()
        url = reverse('whatsapp_app:linea-list')

        # Test id campaña destino invalido error
        data = self.get_menu_post_data()
        id_invalido = 999000999
        data['destination']['data']['options'][0]['destination'] = id_invalido
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(Linea.objects.count(), num_lineas)
        self.assertEqual(response_data['status'], 'ERROR')
        errors = response_data['errors']
        destination_error = errors['destination']['data']['options'][0]['destination'][0]
        self.assertIn(str(id_invalido), destination_error)

    def test_update_linea_gupshup_provider_errors(self):
        self.crear_linea_a_campana()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_campana.id])

        # Al cambiar tipo de proveedor debe cambiar la configuracion
        proveedor_meta = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_META)
        data = {
            'name': 'Nuevo Nombre',
            'provider': proveedor_meta.id,
            'destination': {
                'type': DestinoEntrante.CAMPANA,
                'data': self.campana.id,
            }
        }
        response = self.client.put(url, data, content_type="application/json")
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('configuration', response_data['errors'])

        # Al cambiar configuracion de proveedor debe indicar proveedor
        data = {
            'name': 'Nuevo Nombre',
            'configuration': {'app_name': 'NewLineaAppName', 'app_id': 'NewLineaAppId'},
            'destination': {
                'type': DestinoEntrante.CAMPANA,
                'data': self.campana_2.id,
            }
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn('provider', response_data['errors'])

    def test_update_linea_gupshup_con_campana(self):
        self.crear_linea_a_campana()
        num_lineas = Linea.objects.count()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_campana.id])
        proveedor_2 = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP)
        data = {
            'name': 'Nuevo Nombre',
            'provider': proveedor_2.id,
            'configuration': {'app_name': 'NewLineaAppName', 'app_id': 'NewLineaAppId'},
            'destination': {
                'type': DestinoEntrante.CAMPANA,
                'data': self.campana_2.id,
            }
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(Linea.objects.count(), num_lineas)
        linea = Linea.objects.get(id=self.linea_a_campana.id)
        self.assertEqual(linea.nombre, 'Nuevo Nombre')
        self.assertEqual(linea.destino.tipo, DestinoEntrante.CAMPANA)
        self.assertEqual(linea.destino, DestinoEntrante.get_nodo_ruta_entrante(self.campana_2))
        self.assertEqual(response_data['data']['destination']['id'], self.campana_2.id)

    def test_update_linea_gupshup_con_menu_interactivo_a_campana(self):
        self.crear_linea_a_menu()
        num_lineas = Linea.objects.count()
        num_menu = MenuInteractivoWhatsapp.objects.count()
        num_opcion = OpcionMenuInteractivoWhatsapp.objects.count()
        num_opcion_destino = OpcionDestino.objects.count()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_menu.id])
        proveedor_2 = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP)
        data = {
            'name': 'Nuevo Nombre',
            'provider': proveedor_2.id,
            'configuration': {'app_name': 'NewLineaAppName', 'app_id': 'NewLineaAppId'},
            'destination': {
                'type': DestinoEntrante.CAMPANA,
                'data': self.campana_2.id,
            }
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(Linea.objects.count(), num_lineas)
        self.assertEqual(MenuInteractivoWhatsapp.objects.count(), num_menu - 1)
        self.assertEqual(OpcionMenuInteractivoWhatsapp.objects.count(), num_opcion - 3)
        self.assertEqual(OpcionDestino.objects.count(), num_opcion_destino - 3)
        linea = Linea.objects.get(id=self.linea_a_menu.id)
        self.assertEqual(linea.nombre, 'Nuevo Nombre')
        self.assertEqual(linea.destino.tipo, DestinoEntrante.CAMPANA)
        self.assertEqual(linea.destino, DestinoEntrante.get_nodo_ruta_entrante(self.campana_2))
        self.assertEqual(response_data['data']['destination']['id'], self.campana_2.id)

    def test_update_linea_gupshup_con_campana_a_menu_interactivo(self):
        self.crear_linea_a_campana()
        num_lineas = Linea.objects.count()
        num_menu = MenuInteractivoWhatsapp.objects.count()
        num_opcion = OpcionMenuInteractivoWhatsapp.objects.count()
        num_opcion_destino = OpcionDestino.objects.count()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_campana.id])
        proveedor_2 = ConfiguracionProveedorFactory(
            tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP)
        destination_data = self.get_menu_post_data()['destination']
        data = {
            'name': 'Nuevo Nombre',
            'provider': proveedor_2.id,
            'configuration': {'app_name': 'NewLineaAppName', 'app_id': 'NewLineaAppId'},
            'destination': destination_data
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEqual(Linea.objects.count(), num_lineas)
        # Se crean el menu con sus dos opciones
        self.assertEqual(MenuInteractivoWhatsapp.objects.count(), num_menu + 1)
        self.assertEqual(OpcionMenuInteractivoWhatsapp.objects.count(), num_opcion + 2)
        self.assertEqual(OpcionDestino.objects.count(), num_opcion_destino + 2)

        # El destino de la linea es el destino del menu creado
        linea = Linea.objects.get(id=self.linea_a_campana.id)
        self.assertEqual(linea.destino.tipo, DestinoEntrante.MENU_INTERACTIVO_WHATSAPP)
        menu_id = response_data['data']['destination']['id']
        menu = MenuInteractivoWhatsapp.objects.get(id=menu_id)
        self.assertEqual(linea.destino, DestinoEntrante.get_nodo_ruta_entrante(menu))

        self.assertEqual(2, linea.destino.destinos_siguientes.count())
        opcion_2 = linea.destino.get_opcion_destino_por_valor('Dos')
        self.assertEqual(opcion_2.destino_siguiente, self.destino_2)
        opcion_3 = linea.destino.get_opcion_destino_por_valor('Tres')
        self.assertEqual(opcion_3.destino_siguiente, self.destino_3)
        self.assertEqual(linea.nombre, 'Nuevo Nombre')

    def test_update_linea_gupshup_con_menu_interactivo(self):
        self.crear_linea_a_menu()
        num_lineas = Linea.objects.count()
        num_menu = MenuInteractivoWhatsapp.objects.count()
        num_opcion = OpcionMenuInteractivoWhatsapp.objects.count()
        num_opcion_destino = OpcionDestino.objects.count()
        url = reverse('whatsapp_app:linea-detail', args=[self.linea_a_menu.id])

        destination_data = self.get_menu_post_data()['destination']
        destination_data['data']['options'] = [{
            'value': 'Campana 1',
            'description': 'Descripcion opcion 1',
            'destination': self.campana.id,
        }, {
            'value': 'Tres',
            'description': 'A campana 3',
            'destination': self.campana_3.id,
        }]
        data = {
            'name': 'Nuevo Nombre',
            'destination': destination_data
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Linea.objects.count(), num_lineas)
        # Se mantiene el menu con una opción menos
        self.assertEqual(MenuInteractivoWhatsapp.objects.count(), num_menu)
        self.assertEqual(OpcionMenuInteractivoWhatsapp.objects.count(), num_opcion - 1)
        self.assertEqual(OpcionDestino.objects.count(), num_opcion_destino - 1)

        linea = self.linea_a_menu
        linea.refresh_from_db()
        self.assertEqual(2, linea.destino.destinos_siguientes.count())
        opcion_1 = linea.destino.get_opcion_destino_por_valor('Campana 1')
        self.assertEqual(opcion_1.destino_siguiente, self.destino_1)
        opcion_3 = linea.destino.get_opcion_destino_por_valor('Tres')
        self.assertEqual(opcion_3.destino_siguiente, self.destino_3)
        self.assertEqual(linea.nombre, 'Nuevo Nombre')
