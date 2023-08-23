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
from ominicontacto_app.models import User, Campana


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
            "api_contact_database_campaings",
            args=[self.db.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(response_json['data']['id'], self.db.pk)
        self.assertEqual(response_json['data']['nombre'], self.db.nombre)
        for campana in response_json['data']['campanas']:
            self.assertIn(campana['id'], [self.camp.pk, self.camp2.pk])
