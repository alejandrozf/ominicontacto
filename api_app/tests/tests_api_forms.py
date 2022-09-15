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
from django.utils.translation import gettext as _
from django.urls import reverse
from ominicontacto_app.tests.factories import OpcionCalificacionFactory
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import User, Formulario, FieldFormulario


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Formularios"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.formulario = Formulario.objects.create(
            nombre="Formulario", descripcion="Un test del formulario"
        )
        self.formularioConCalificacion = Formulario.objects.create(
            nombre="Formulario con calificacion",
            descripcion="Un test del formulario"
        )
        OpcionCalificacionFactory(formulario=self.formularioConCalificacion)
        self.campoTexto = FieldFormulario.objects.create(
            nombre_campo="Texto", orden=1, tipo=1,
            values_select=None, is_required=False,
            formulario=self.formulario
        )
        self.campoFecha = FieldFormulario.objects.create(
            nombre_campo="Fecha", orden=2, tipo=2,
            values_select=None, is_required=True,
            formulario=self.formulario
        )
        self.campoCajaTexto = FieldFormulario.objects.create(
            nombre_campo="Caja de texto", orden=3, tipo=4,
            values_select=None, is_required=False,
            formulario=self.formulario
        )
        self.dataToCreateForm = {
            "nombre": "Nuevo Formulario",
            "descripcion": "Nuevo test del formulario",
            "campos": [
                {
                    "id": None,
                    "nombre_campo": "Texto",
                    "orden": 1,
                    "tipo": 1,
                    "values_select": None,
                    "is_required": False
                },
                {
                    "id": None,
                    "nombre_campo": "Fecha",
                    "orden": 2,
                    "tipo": 2,
                    "values_select": None,
                    "is_required": True
                },
                {
                    "id": None,
                    "nombre_campo": "Caja de texto",
                    "orden": 3,
                    "tipo": 4,
                    "values_select": None,
                    "is_required": False
                }
            ]
        }
        self.urls_api = {
            'FormsList': 'api_forms_list',
            'FormsCreate': 'api_forms_create',
            'FormsDetail': 'api_forms_detail',
            'FormsUpdate': 'api_forms_update',
            'FormsDelete': 'api_forms_delete',
            'FormsHide': 'api_forms_hide',
            'FormsShow': 'api_forms_show',
        }


class FormulariosTest(APITest):
    def test_lista_formularios(self):
        URL = reverse(self.urls_api['FormsList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los formularios '
              'de forma exitosa'))

    def test_detalle_formulario(self):
        URL = reverse(
            self.urls_api['FormsDetail'],
            args=[self.formulario.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['form']['id'], self.formulario.pk)
        self.assertEqual(
            response_json['form']['nombre'],
            self.formulario.nombre)
        self.assertEqual(
            response_json['form']['descripcion'],
            self.formulario.descripcion)
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion del '
              'formulario de forma exitosa'))

    def test_crea_formulario(self):
        URL = reverse(self.urls_api['FormsCreate'])
        numBefore = Formulario.objects.all().count()
        response = self.client.post(
            URL, json.dumps(self.dataToCreateForm),
            format='json', content_type='application/json')
        numAfter = Formulario.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo el formulario '
              'de forma exitosa'))

    def test_elimina_formulario(self):
        pk = self.formulario.pk
        URL = reverse(
            self.urls_api['FormsDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Formulario.objects.filter(pk=pk).exists(), False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino el formulario '
              'de forma exitosa'))

    def test_elimina_formulario_con_calificacion(self):
        pk = self.formularioConCalificacion.pk
        URL = reverse(
            self.urls_api['FormsDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar un '
              'formulario con calificaciones'))

    def test_oculta_formulario(self):
        pk = self.formulario.pk
        URL = reverse(
            self.urls_api['FormsHide'],
            args=[pk, ])
        response = self.client.put(URL, follow=True)
        form = Formulario.objects.get(pk=pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.oculto, True)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se oculto el formulario '
              'de forma exitosa'))

    def test_desoculta_formulario(self):
        pk = self.formulario.pk
        URL = reverse(
            self.urls_api['FormsShow'],
            args=[pk, ])
        response = self.client.put(URL, follow=True)
        form = Formulario.objects.get(pk=pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.oculto, False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se desoculto el formulario '
              'de forma exitosa'))

    def test_actualiza_formulario(self):
        pk = self.formulario.pk
        URL = reverse(
            self.urls_api['FormsUpdate'],
            args=[pk, ])
        request_data = {
            'nombre': 'Form Edit',
            'descripcion': 'Edit Description',
            'campos': [
            ]
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        form = Formulario.objects.get(pk=pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.nombre, request_data['nombre'])
        self.assertEqual(form.descripcion, request_data['descripcion'])
        self.assertEqual(len(form.campos.all()), len(request_data['campos']))
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo el formulario '
              'de forma exitosa'))

    def test_actualiza_formulario_con_calificacion(self):
        pk = self.formularioConCalificacion.pk
        URL = reverse(
            self.urls_api['FormsUpdate'],
            args=[pk, ])
        request_data = {
            'nombre': 'Form Edit',
            'descripcion': 'Edit Description',
            'campos': [
            ]
        }
        response = self.client.put(
            URL, json.dumps(request_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido actualizar un '
              'formulario con calificaciones'))
