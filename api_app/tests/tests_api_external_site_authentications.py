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
from django.utils.translation import ugettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    AutenticacionSitioExternoFactory,
    SitioExternoFactory)
from ominicontacto_app.models import AutenticacionSitioExterno, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Autenticacion de Sitios Externos"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        self.autenticacion_sitio_externo = AutenticacionSitioExternoFactory()
        self.autenticacion_sitio_externo2 = AutenticacionSitioExternoFactory()
        self.sitio_externo = SitioExternoFactory(autenticacion=self.autenticacion_sitio_externo2)

        self.urls_api = {
            'List': 'api_external_site_authentications_list',
            'Create': 'api_external_site_authentications_create',
            'Detail': 'api_external_site_authentications_detail',
            'Update': 'api_external_site_authentications_update',
            'Delete': 'api_external_site_authentications_delete'
        }


class ExternalSiteAuthenticationTest(APITest):
    def test_list(self):
        URL = reverse(self.urls_api['List'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron las autenticaciones para sitios '
              'externos de forma exitosa'))

    def test_detail(self):
        URL = reverse(
            self.urls_api['Detail'],
            args=[self.autenticacion_sitio_externo.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion de la autenticacion para '
              'sitio externo de forma exitosa'))
        self.assertEqual(
            response_json['externalSiteAuthentication'],
            {
                'id': self.autenticacion_sitio_externo.pk,
                'nombre': self.autenticacion_sitio_externo.nombre,
                'url': self.autenticacion_sitio_externo.url,
                'username': self.autenticacion_sitio_externo.username,
                'password': self.autenticacion_sitio_externo.password,
                'campo_token': self.autenticacion_sitio_externo.campo_token,
                'duracion': self.autenticacion_sitio_externo.duracion,
                'campo_duracion': self.autenticacion_sitio_externo.campo_duracion,
                'token': self.autenticacion_sitio_externo.token,
                'expiracion_token': self.autenticacion_sitio_externo.expiracion_token,
                'ssl_estricto': self.autenticacion_sitio_externo.ssl_estricto
            })

    def test_delete(self):
        pk = self.autenticacion_sitio_externo.pk
        URL = reverse(
            self.urls_api['Delete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            AutenticacionSitioExterno.objects.filter(pk=pk).exists(), False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino la autenticacion para sitio externo '
              'de forma exitosa'))

    def test_delete_with_external_site(self):
        pk = self.autenticacion_sitio_externo2.pk
        URL = reverse(
            self.urls_api['Delete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            AutenticacionSitioExterno.objects.filter(pk=pk).exists(), True)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar una '
              'autenticacion que tiene sitios externos'))

    def test_create(self):
        URL = reverse(self.urls_api['Create'])
        data = {
            'nombre': 'Nueva autenticacion',
            'url': 'https://www.youtube.com/',
            'username': 'newuser',
            'password': 'test123..',
            'campo_token': 'token',
            'duracion': 0,
            'campo_duracion': 'timeToEnd',
            'token': None,
            'expiracion_token': None
        }
        numBefore = AutenticacionSitioExterno.objects.all().count()
        response = self.client.post(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        numAfter = AutenticacionSitioExterno.objects.all().count()
        response_json = json.loads(response.content)
        autenticacion = AutenticacionSitioExterno.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo la autenticacion para sitio externo '
              'de forma exitosa'))
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(autenticacion.nombre, data['nombre'])
        self.assertEqual(autenticacion.url, data['url'])
        self.assertEqual(autenticacion.username, data['username'])
        self.assertEqual(autenticacion.password, data['password'])
        self.assertEqual(autenticacion.campo_token, data['campo_token'])
        self.assertEqual(autenticacion.campo_duracion, data['campo_duracion'])
        self.assertEqual(autenticacion.duracion, data['duracion'])

    def test_update(self):
        pk = self.autenticacion_sitio_externo.pk
        URL = reverse(
            self.urls_api['Update'],
            args=[pk, ])
        data = {
            'nombre': 'Edit autenticacion',
            'url': 'https://www.facebook.com/',
            'username': 'edituser',
            'password': 'test123..',
            'campo_token': 'tokenEdit',
            'duracion': 60,
            'campo_duracion': '',
            'ssl_estricto': False
        }
        response = self.client.put(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        response_json = json.loads(response.content)
        autenticacion = AutenticacionSitioExterno.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(autenticacion.nombre, data['nombre'])
        self.assertEqual(autenticacion.url, data['url'])
        self.assertEqual(autenticacion.username, data['username'])
        self.assertEqual(autenticacion.password, data['password'])
        self.assertEqual(autenticacion.campo_token, data['campo_token'])
        self.assertEqual(autenticacion.campo_duracion, data['campo_duracion'])
        self.assertEqual(autenticacion.duracion, data['duracion'])
        self.assertEqual(autenticacion.ssl_estricto, data['ssl_estricto'])
