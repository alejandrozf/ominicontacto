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
from django.conf import settings
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    NombreCalificacionFactory)
from ominicontacto_app.models import NombreCalificacion, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Calificaciones"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        self.calificacion = NombreCalificacionFactory()
        self.urls_api = {
            'CalificacionesList': 'api_call_dispositions_list',
            'CalificacionesCreate': 'api_call_dispositions_create',
            'CalificacionesUpdate': 'api_call_dispositions_update',
            'CalificacionesDelete': 'api_call_dispositions_delete',
            'CalificacionesDetail': 'api_call_dispositions_detail'
        }


class CalificacionesTest(APITest):
    def test_lista_calificaciones(self):
        URL = reverse(self.urls_api['CalificacionesList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron las calificaciones '
              'de forma exitosa'))

    def test_crea_calificacion(self):
        URL = reverse(self.urls_api['CalificacionesCreate'])
        post_data = {
            'nombre': 'Calificacion Test'
        }
        numBefore = NombreCalificacion.objects.all().count()
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        numAfter = NombreCalificacion.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la calificacion '
              'de forma exitosa'))

    def test_crea_calificacion_con_nombre_reservado(self):
        URL = reverse(self.urls_api['CalificacionesCreate'])
        post_data = {
            'nombre': settings.CALIFICACION_REAGENDA
        }
        response = self.client.post(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('Error al hacer la peticion'))

    def test_actualiza_calificacion(self):
        URL = reverse(
            self.urls_api['CalificacionesUpdate'],
            args=[self.calificacion.pk, ])
        new_name = 'Calificacion Editada'
        post_data = {
            'nombre': new_name
        }
        response = self.client.put(
            URL, json.dumps(post_data),
            format='json', content_type='application/json')
        calificacion = NombreCalificacion.objects.get(pk=self.calificacion.pk)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(calificacion.nombre, new_name)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se actualizo la calificacion '
              'de forma exitosa'))

    def test_elimina_calificacion(self):
        pk = self.calificacion.pk
        URL = reverse(
            self.urls_api['CalificacionesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            NombreCalificacion.objects.filter(pk=pk).exists(), False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la calificacion '
              'de forma exitosa'))
