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

from mock import patch

from django.core.urlresolvers import reverse
from ominicontacto_app.models import SitioExterno
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import SitioExternoFactory


class TestsSitioExterno(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsSitioExterno, self).setUp(*args, **kwargs)

        self.admin = self.crear_administrador()
        self.admin.set_password(self.PWD)

        self.sito_externo = SitioExternoFactory()

    def _obtener_post_sitio_externo(self):
        return {
            'nombre': 'test_ruta_entrante',
            'tipo': SitioExterno.GET,
            'url': 'http://www.infobae.com/',
            'metodo': SitioExterno.EMBEBIDO,
        }

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionSitioExternoAsterisk.regenerar_asterisk')
    def test_crear_sitio_externo(self, regenerar_asterisk):
        url = reverse('sitio_externo_create')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_sitio_externo()
        n_sitio_externo = SitioExterno.objects.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(SitioExterno.objects.count(), n_sitio_externo + 1)

    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionSitioExternoAsterisk.regenerar_asterisk')
    def test_update_sitio_externo(self, regenerar_asterisk):
        url = reverse('modificar_sitio_externo', args=[self.sito_externo.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        nombre_modificado = 'sitio_crm_ventas'
        post_data = self._obtener_post_sitio_externo()
        post_data['nombre'] = nombre_modificado
        self.client.post(url, post_data, follow=True)
        self.sito_externo.refresh_from_db()
        self.assertEqual(self.sito_externo.nombre, nombre_modificado)
