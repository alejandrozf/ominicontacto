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
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    AutenticacionSitioExternoFactory, CampanaFactory, SitioExternoFactory)
from ominicontacto_app.models import Campana, SitioExterno, User


class APITest(OMLBaseTest):
    """Tests para los Endpoints del API Sitios Externos"""

    def setUp(self):
        super(APITest, self).setUp()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)

        self.autenticacion = AutenticacionSitioExternoFactory()
        self.sitio_externo = SitioExternoFactory()
        self.sitio_externo2 = SitioExternoFactory()
        self.campana = CampanaFactory(
            type=Campana.TYPE_ENTRANTE,
            tipo_interaccion=Campana.SITIO_EXTERNO,
            sitio_externo=self.sitio_externo)

        self.urls_api = {
            'ExternalSitesList': 'api_external_sites_list',
            'ExternalSitesCreate': 'api_external_sites_create',
            'ExternalSitesDetail': 'api_external_sites_detail',
            'ExternalSitesUpdate': 'api_external_sites_update',
            'ExternalSitesDelete': 'api_external_sites_delete',
            'ExternalSitesHide': 'api_external_sites_hide',
            'ExternalSitesShow': 'api_external_sites_show',
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
            self.urls_api['ExternalSitesDetail'],
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
                'id': self.sitio_externo.pk,
                'nombre': self.sitio_externo.nombre,
                'url': self.sitio_externo.url,
                'oculto': self.sitio_externo.oculto,
                'disparador': self.sitio_externo.disparador,
                'metodo': self.sitio_externo.metodo,
                'formato': self.sitio_externo.formato,
                'objetivo': self.sitio_externo.objetivo,
                'autenticacion': self.sitio_externo.autenticacion
            })

    def test_elimina_sitio_externo(self):
        pk = self.sitio_externo2.pk
        URL = reverse(
            self.urls_api['ExternalSitesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            SitioExterno.objects.filter(pk=pk).exists(), False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se elimino el sitio externo '
              'de forma exitosa'))

    def test_elimina_sitio_externo_con_campana(self):
        pk = self.sitio_externo.pk
        URL = reverse(
            self.urls_api['ExternalSitesDelete'],
            args=[pk, ])
        response = self.client.delete(URL, follow=True)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            SitioExterno.objects.filter(pk=pk).exists(), True)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(
            response_json['message'],
            _('No está permitido eliminar un '
              'sitio externo asociado a una campaña'))

    def test_oculta_sitio_externo(self):
        pk = self.sitio_externo2.pk
        URL = reverse(
            self.urls_api['ExternalSitesHide'],
            args=[pk, ])
        response = self.client.put(URL, follow=True)
        response_json = json.loads(response.content)
        sitio = SitioExterno.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sitio.oculto, True)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se oculto el sitio externo '
              'de forma exitosa'))

    def test_desoculta_sitio_externo(self):
        pk = self.sitio_externo2.pk
        URL = reverse(
            self.urls_api['ExternalSitesShow'],
            args=[pk, ])
        response = self.client.put(URL, follow=True)
        response_json = json.loads(response.content)
        sitio = SitioExterno.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sitio.oculto, False)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se desoculto el sitio externo '
              'de forma exitosa'))

    def test_crea_sitio_externo_valido(self):
        URL = reverse(self.urls_api['ExternalSitesCreate'])
        data = {
            'nombre': 'Sitio Nuevo Test',
            'url': 'https://www.youtube.com/',
            'disparador': SitioExterno.AUTOMATICO,
            'metodo': SitioExterno.GET,
            'objetivo': SitioExterno.EMBEBIDO,
            'formato': None,
            'autenticacion': self.autenticacion.pk
        }
        numBefore = SitioExterno.objects.all().count()
        response = self.client.post(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        numAfter = SitioExterno.objects.all().count()
        response_json = json.loads(response.content)
        sitio = SitioExterno.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se creo el sitio externo '
              'de forma exitosa'))
        self.assertEqual(numAfter, numBefore + 1)
        self.assertEqual(sitio.nombre, data['nombre'])
        self.assertEqual(sitio.url, data['url'])
        self.assertEqual(sitio.disparador, data['disparador'])
        self.assertEqual(sitio.metodo, data['metodo'])
        self.assertEqual(sitio.objetivo, data['objetivo'])
        self.assertEqual(sitio.autenticacion.pk, data['autenticacion'])

    def test_crea_sitio_externo_valida_formato(self):
        URL = reverse(self.urls_api['ExternalSitesCreate'])
        data = {
            'nombre': 'Sitio Nuevo Test',
            'url': 'https://www.youtube.com/',
            'disparador': SitioExterno.AUTOMATICO,
            'metodo': SitioExterno.GET,
            'objetivo': SitioExterno.EMBEBIDO,
            'formato': SitioExterno.JSON,
            'autenticacion': self.autenticacion.pk
        }
        numBefore = SitioExterno.objects.all().count()
        response = self.client.post(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        numAfter = SitioExterno.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(numAfter, numBefore)
        self.assertIn('formato', response_json['errors'])
        self.assertEqual(response_json['errors']['formato'],
                         ['Si el método es GET, no debe indicarse formato'])

    def test_crea_sitio_externo_valida_objetivo(self):
        URL = reverse(self.urls_api['ExternalSitesCreate'])
        data = {
            'nombre': 'Sitio Nuevo Test',
            'url': 'https://www.youtube.com/',
            'disparador': SitioExterno.SERVER,
            'metodo': SitioExterno.GET,
            'objetivo': SitioExterno.EMBEBIDO,
            'formato': None,
            'autenticacion': self.autenticacion.pk
        }
        numBefore = SitioExterno.objects.all().count()
        response = self.client.post(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        numAfter = SitioExterno.objects.all().count()
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'ERROR')
        self.assertEqual(numAfter, numBefore)
        self.assertIn('objetivo', response_json['errors'])
        self.assertEqual(response_json['errors']['objetivo'],
                         ['Si el disparador es el servidor, no puede haber un objetivo.'])

    def test_actualiza_sitio_externo_valido(self):
        pk = self.sitio_externo2.pk
        URL = reverse(
            self.urls_api['ExternalSitesUpdate'],
            args=[pk, ])
        data = {
            'nombre': 'Sitio Externo Edit',
            'url': 'https://www.google.com/',
            'disparador': SitioExterno.SERVER,
            'metodo': SitioExterno.GET,
            'objetivo': None,
            'formato': None,
            'autenticacion': None
        }
        response = self.client.put(
            URL, json.dumps(data), format='json',
            content_type='application/json')
        response_json = json.loads(response.content)
        sitio = SitioExterno.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(sitio.nombre, data['nombre'])
        self.assertEqual(sitio.url, data['url'])
        self.assertEqual(sitio.autenticacion, data['autenticacion'])
