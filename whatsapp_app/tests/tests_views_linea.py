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

from ominicontacto_app.tests.utiles import OMLBaseTest
from rest_framework import status
from rest_framework.authtoken.models import Token
from ominicontacto_app.models import User
from django.test import RequestFactory
from django.urls import reverse
from ominicontacto_app.tests.utiles import PASSWORD
from whatsapp_app.tests.factories import LineaFactory, ConfiguracionProveedorFactory


class LineaTest(OMLBaseTest):
    def setUp(self):
        super(LineaTest, self).setUp()
        self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_configuaracion_linea_forbidden(self):
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

    def test_configuaracion_linea_list(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('whatsapp_app:linea-list')
        response_linea_list = self.client.get(url)
        proveedor = ConfiguracionProveedorFactory()
        playload = {
            "nombre": "linea",
            "proveedor": proveedor.id,
            "numero": "45665465466456545",
        }
        response_linea_create = self.client.post(url, playload, content_type="application/json")
        self.assertEqual(response_linea_list.status_code, status.HTTP_200_OK)
        self.assertEqual(response_linea_create.status_code, status.HTTP_201_CREATED)

    def test_configuaracion_linea_detail(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        linea = LineaFactory()
        url = reverse('whatsapp_app:linea-detail', args=[linea.pk])
        response_linea_detail = self.client.get(url)
        playload = {
            "nombre": "linea2",
        }
        response_linea_update = self.client.put(url, playload, content_type="application/json")
        response_linea_delete = self.client.delete(url, content_type="application/json")
        self.assertEqual(response_linea_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_linea_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_linea_delete.status_code, status.HTTP_200_OK)
