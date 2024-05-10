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
from ominicontacto_app.models import User
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.authtoken.models import Token
from ominicontacto_app.tests.utiles import PASSWORD
from whatsapp_app.tests.factories import ConfiguracionProveedorFactory


class ConfiguracionProveedorTest(OMLBaseTest):
    def setUp(self):
        super(ConfiguracionProveedorTest, self).setUp()
        self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_configuracion_proveedor_forbidden(self):
        url_list = reverse('whatsapp_app:proveedor-list')
        response_proveedor_list = self.client.get(url_list)
        response_proveedor_create = self.client.post(url_list)
        configuracion = ConfiguracionProveedorFactory()
        url_details = reverse('whatsapp_app:proveedor-detail', args=[configuracion.pk])
        response_proveedor_update = self.client.put(url_details)
        response_proveedor_detail = self.client.get(url_details)
        response_proveedor_delete = self.client.delete(url_details)
        self.assertEqual(response_proveedor_list.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_proveedor_create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_proveedor_update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_proveedor_detail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_proveedor_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_configuracion_proveedor_list(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('whatsapp_app:proveedor-list')
        response_proveedor_list = self.client.get(url)
        playload = {
            "name": "provedor",
            "provider_type": 1,
            "configuration": {}
        }
        response_proveedor_create = self.client.post(url, playload, content_type="application/json")
        self.assertEqual(response_proveedor_list.status_code, status.HTTP_200_OK)
        self.assertEqual(response_proveedor_create.status_code, status.HTTP_201_CREATED)

    def test_configuracion_proveedor_detail(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        configuracion = ConfiguracionProveedorFactory()
        url = reverse('whatsapp_app:proveedor-detail', args=[configuracion.pk])
        response_proveedor_detail = self.client.get(url)
        playload = {
            "name": "provedor2",
        }
        response_proveedor_update = self.client.put(url, playload,
                                                    content_type="application/json")
        response_proveedor_delete = self.client.delete(url, content_type="application/json")
        self.assertEqual(response_proveedor_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_proveedor_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_proveedor_delete.status_code, status.HTTP_200_OK)
