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
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import CampanaFactory, BaseDatosContactoFactory
from ominicontacto_app.models import User, Campana, BaseDatosContacto
from rest_framework import status


class APITest(OMLBaseTest):
    """Tests para los Endpoints del Base de Contactos"""

    def setUp(self):
        super(APITest, self).setUp()
        self.sup = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=self.sup, rol=User.SUPERVISOR)
        self.db = BaseDatosContactoFactory()
        self.camp = CampanaFactory(
            nombre='Campana 1',
            estado=Campana.ESTADO_ACTIVA,
            bd_contacto=self.db)
        self.camp2 = CampanaFactory(
            nombre='Campana 2',
            estado=Campana.ESTADO_ACTIVA,
            bd_contacto=self.db)


class BaseDeContactosTest(APITest):
    def test_obtener_campanas_activas_asociadas(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        URL = reverse(
            'api_contact_database_campaings',
            args=[self.db.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(response_json['data']['id'], self.db.pk)
        self.assertEqual(response_json['data']['nombre'], self.db.nombre)
        for campana in response_json['data']['campanas']:
            self.assertIn(campana['id'], [self.camp.pk, self.camp2.pk])


class BaseDatosContactoCreateTest(APITest):

    def test_validar_nombres(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        post_data = {
            'name': 'test-3',
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
        }
        URL = reverse('api_database_create_view',)

        # Nombres de campos repetidos
        post_data['external_id_field'] = 'tel'
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

        post_data.pop('external_id_field')
        # Data fields debe tener al menos un campo
        post_data['data_fields'] = []
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Data fields inválido
        post_data['data_fields'] = 'nolista'
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

        post_data['data_fields'] = ['si', 'lista']
        # El nombre debe ser único
        post_data['name'] = self.db.nombre
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_crea_db_ok(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        nombre = 'test-db' if self.db.nombre != 'test-db' else 'otro-nombre'
        post_data = {
            'name': nombre,
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
            'external_id_field': 'dni'
        }
        URL = reverse('api_database_create_view',)
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        id = response_json['data']['id']
        bd = BaseDatosContacto.objects.get(id=id)
        metadata = bd.get_metadata()
        self.assertEqual(nombre, bd.nombre)
        self.assertEqual('tel', metadata.nombre_campo_telefono)
        self.assertEqual(set(post_data['phone_fields']),
                         set(metadata.nombres_de_columnas_de_telefonos))
        data_fields = post_data['data_fields'] + ['cel']
        self.assertEqual(set(data_fields), set(metadata.nombres_de_columnas_de_datos))
        self.assertEqual(post_data['external_id_field'], metadata.nombre_campo_id_externo)
        todos = post_data['phone_fields'] + post_data['data_fields'] + ['dni']
        self.assertEqual(set(todos), set(metadata.nombres_de_columnas))

    def test_crea_contacto_ok(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        nombre = 'test-db' if self.db.nombre != 'test-db' else 'otro-nombre'
        post_data = {
            'name': nombre,
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
            'external_id_field': 'dni'
        }
        URL = reverse('api_database_create_view',)
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        id = response_json['data']['id']
        db = BaseDatosContacto.objects.get(id=id)
        post_data = [
            {
                "tel": "09090900",
                "cel": "09889900",
                "nombre": "contacto1",
                "apellido": "contacto1",
                "dni": "35353530"
            },
            {
                "tel": "09090901",
                "cel": "09889900",
                "nombre": "contacto2",
                "apellido": "contacto2",
                "dni": "35353531"
            }
        ]
        URL = reverse('api_database_create_contact_view', args=[db.pk, ])
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_crea_contacto_nombre_de_campo_erroneo(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        nombre = 'test-db' if self.db.nombre != 'test-db' else 'otro-nombre'
        post_data = {
            'name': nombre,
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
            'external_id_field': 'dni'
        }
        URL = reverse('api_database_create_view',)
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        id = response_json['data']['id']
        db = BaseDatosContacto.objects.get(id=id)
        post_data = [
            {
                "telefono": "09090900",  # nombre de campo erroneo
                "cel": "09889900",
                "nombre": "contacto1",
                "apellido": "contacto1",
                "dni": "35353530"
            },
        ]
        URL = reverse('api_database_create_contact_view', args=[db.pk, ])
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crea_contacto_sin_campo_requerido(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        nombre = 'test-db' if self.db.nombre != 'test-db' else 'otro-nombre'
        post_data = {
            'name': nombre,
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
            'external_id_field': 'dni'
        }
        URL = reverse('api_database_create_view',)
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        id = response_json['data']['id']
        db = BaseDatosContacto.objects.get(id=id)
        post_data = [
            {
                "cel": "09889900",
                "nombre": "contacto1",
                "apellido": "contacto1",
                "dni": "35353530"
            },
        ]
        URL = reverse('api_database_create_contact_view', args=[db.pk, ])
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crea_contacto_id_externo_repetido(self):
        self.client.login(username=self.sup.username, password=PASSWORD)
        nombre = 'test-db' if self.db.nombre != 'test-db' else 'otro-nombre'
        post_data = {
            'name': nombre,
            'phone_fields': ['tel', 'cel'],
            'data_fields': ['nombre', 'apellido'],
            'external_id_field': 'dni'
        }
        URL = reverse('api_database_create_view',)
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        id = response_json['data']['id']
        db = BaseDatosContacto.objects.get(id=id)
        post_data = [
            {
                "telefono": "09090900",
                "cel": "09889900",
                "nombre": "contacto1",
                "apellido": "contacto1",
                "dni": "35353530"
            },
            {
                "telefono": "09090900",
                "cel": "09889900",
                "nombre": "contacto1",
                "apellido": "contacto1",
                "dni": "35353530"
            },
        ]
        URL = reverse('api_database_create_contact_view', args=[db.pk, ])
        response = self.client.post(URL, json.dumps(post_data),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
