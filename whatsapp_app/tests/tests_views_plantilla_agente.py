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
from whatsapp_app.models import PlantillaMensaje
from whatsapp_app.tests.factories import PlantillaAgenteFactory


class ConfiguraciontemplateTest(OMLBaseTest):
    def setUp(self):
        super(ConfiguraciontemplateTest, self).setUp()
        self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_configuaracion_template_forbidden(self):
        url_list = reverse('whatsapp_app:plantilla-mensaje-list')
        response_template_list = self.client.get(url_list)
        response_template_create = self.client.post(url_list)
        configuaracion = PlantillaAgenteFactory()
        url_details = reverse('whatsapp_app:plantilla-mensaje-detail', args=[configuaracion.pk])
        response_template_update = self.client.put(url_details)
        response_template_detail = self.client.get(url_details)
        response_template_delete = self.client.delete(url_details)
        self.assertEqual(response_template_list.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_template_create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_template_update.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_template_detail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_template_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_configuaracion_template_list(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        url = reverse('whatsapp_app:plantilla-mensaje-list')
        response_template_list = self.client.get(url)
        playload = {
            "name": "plantilla",
            "type": PlantillaMensaje.TIPO_TEXT,
            "configuration": {
                "type": "text",
                "text": "Hello World"
            }
        }
        response_template_create = self.client.post(url, playload, content_type="application/json")
        self.assertEqual(response_template_list.status_code, status.HTTP_200_OK)
        self.assertEqual(response_template_create.status_code, status.HTTP_201_CREATED)

    def test_configuaracion_template_detail(self):
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        configuaracion = PlantillaAgenteFactory()
        url = reverse('whatsapp_app:plantilla-mensaje-detail', args=[configuaracion.pk])
        response_template_detail = self.client.get(url)
        playload = {
            "nombre": "plantilla2",
        }
        response_template_update = self.client.put(url, playload,
                                                   content_type="application/json")
        response_template_delete = self.client.delete(url, content_type="application/json")
        self.assertEqual(response_template_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_template_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_template_delete.status_code, status.HTTP_200_OK)
