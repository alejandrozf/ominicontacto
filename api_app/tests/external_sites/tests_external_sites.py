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
from django.utils.translation import ugettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    CampanaFactory, SitioExternoFactory)
from ominicontacto_app.models import Campana, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Sitios Externos"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        self.sitio_externo = SitioExternoFactory()
        self.sitio_externo2 = SitioExternoFactory()
        self.campana = CampanaFactory(
            type=Campana.TYPE_ENTRANTE,
            tipo_interaccion=Campana.SITIO_EXTERNO,
            sitio_externo=self.sitio_externo)

        self.urls_api = {
            'ExternalSitesList': 'api_external_sites_list',
            'ExternalSiteCreate': 'api_external_sites_create',
            'ExternalSiteDetail': 'api_external_sites_detail',
            'ExternalSiteUpdate': 'api_external_sites_update',
            'ExternalSiteDelete': 'api_external_sites_delete',
            'ExternalSiteHide': 'api_external_sites_hide',
            'ExternalSiteShow': 'api_external_sites_show',
        }


class SitiosExternosTest(APITest):
    def test_lista_sitios_externos(self):
        URL = reverse(self.urls_api['ExternalSitesList'])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los sitios '
              'externos de forma exitosa'))

    def test_sitio_externo_detalle(self):
        URL = reverse(
            self.urls_api['ExternalSiteDetail'],
            args=[self.sitio_externo.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvo la informacion del '
              'sitio externo de forma exitosa'))
        self.assertEqual(
            response_json['externalSiteDetail'],
            {
                "id": self.sitio_externo.pk,
                "nombre": self.sitio_externo.nombre,
                "url": self.sitio_externo.url,
                "oculto": self.sitio_externo.oculto,
                "disparador": self.sitio_externo.disparador,
                "metodo": self.sitio_externo.metodo,
                "formato": self.sitio_externo.formato,
                "objetivo": self.sitio_externo.objetivo
            })

    def test_elimina_sitio_externo(self):
        URL = reverse(
            self.urls_api['ExternalSiteDelete'],
            args=[self.sitio_externo2.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino el sitio externo '
              'de forma exitosa'))

    def test_elimina_sitio_externo_con_campana(self):
        URL = reverse(
            self.urls_api['ExternalSiteDelete'],
            args=[self.sitio_externo.pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar un '
              'sitio externo asociado a una campaña'))

    def test_oculta_sitio_externo(self):
        URL = reverse(
            self.urls_api['ExternalSiteHide'],
            args=[self.sitio_externo.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se oculto el sitio externo '
              'de forma exitosa'))

    def test_desoculta_sitio_externo(self):
        URL = reverse(
            self.urls_api['ExternalSiteShow'],
            args=[self.sitio_externo.pk, ])
        response = self.client.get(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se desoculto el sitio externo '
              'de forma exitosa'))
