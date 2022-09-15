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

from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ominicontacto_app.models import User
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.utiles import PASSWORD


class SubirBaseContactosTest(OMLBaseTest):

    def setUp(self):
        super(SubirBaseContactosTest, self).setUp()
        self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.agente_profile = self.crear_agente_profile()

        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_api_subir_base_contacto_api_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('api_upload_base_contactos')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_api_subir_base_contacto_api_deniega_get(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('api_upload_base_contactos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_api_subir_base_contacto_api_deniega_put(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('api_upload_base_contactos')
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

    def test_api_subir_base_contacto_api_admite_post_admin(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('api_upload_base_contactos')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_api_subir_base_contacto_api_admite_post_admin_via_token(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        response = client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_api_subir_base_contacto_api_no_admite_post_agente_via_token(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('api_upload_base_contactos')
        response = client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_api_subir_base_contacto_api_admite_post_supervisor_via_token(self):
        token_supervisor = Token.objects.get(user=self.supervisor.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_supervisor)
        url = reverse('api_upload_base_contactos')
        response = client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_api_subir_base_contacto_error_falta_parametro_filename(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('falta parámetro filename en request'))

    def test_api_subir_base_contacto_error_falta_parametro_nombre(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.csv", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'campos_telefono': 'abc'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('falta parámetro:') + 'nombre')

    def test_api_subir_base_contacto_error_falta_parametro_campos_telefono(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.csv", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('falta parámetro:') + 'campos_telefono')

    def test_api_subir_base_contacto_error_campos_telefono_no_coincide(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.csv", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test', 'campos_telefono': '1,2,3a'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('campo de teléfono no coincide con nombre de columna'))

    def test_api_subir_base_contacto_error_campo_id_externo_no_coincide(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.csv", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test', 'campos_telefono': 'abc', 'id_externo': '1'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('campo de id externo no coincide con nombre de columna'))

    def test_api_subir_base_contacto_error_archivo_no_csv(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.txt", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test', 'campos_telefono': '1'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('la extensión del archivo no es .CSV'))

    def test_api_subir_base_contacto_no_permite_nombre_mayor_45_caracteres(self):
        LONGITUD_MAXIMA = 45
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.txt", b"abc,cxf", content_type="text/plain")
        payload = {"filename": file, 'nombre': 't' * 46, 'campos_telefono': '1'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('La longitud del nombre no debe exceder los {0} caracteres'.format(
                             LONGITUD_MAXIMA)))

    def test_api_subir_base_contacto_base_guardada_retorna_id(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile("file.csv", b"abc,cxf\n1889988998,pppp\n222222222,lolo",
                                  content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test', 'campos_telefono': 'abc'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        self.assertTrue(str(response.json()['id']).isdigit())

    def test_api_subir_base_contacto_error_columnas_repetidas(self):
        token_admin = Token.objects.get(user=self.admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
        url = reverse('api_upload_base_contactos')
        file = SimpleUploadedFile(
            "file.csv", b"col1,col2,col1\n1,2,3\n1,2,3", content_type="text/plain")
        payload = {"filename": file, 'nombre': 'test', 'campos_telefono': 'col1'}
        response = client.post(url, payload, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _("El archivo a procesar tiene "
                                                       "nombres de columnas repetidos."))
