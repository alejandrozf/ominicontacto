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

from django.core.urlresolvers import reverse
from ominicontacto_app.models import SitioExterno
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import SitioExternoFactory, CampanaFactory


class TestsSitioExterno(OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsSitioExterno, self).setUp(*args, **kwargs)

        self.admin = self.crear_administrador()
        self.agente = self.crear_user_agente()
        self.agente.set_password(self.PWD)
        self.admin.set_password(self.PWD)

        self.sitio_externo = SitioExternoFactory()

    def _obtener_post_sitio_externo(self):
        return {
            'nombre': 'test_ruta_entrante',
            'tipo': SitioExterno.GET,
            'url': 'http://www.infobae.com/',
            'metodo': SitioExterno.EMBEBIDO,
        }

    def test_crear_sitio_externo(self):
        url = reverse('sitio_externo_create')
        self.client.login(username=self.admin.username, password=self.PWD)
        post_data = self._obtener_post_sitio_externo()
        n_sitio_externo = SitioExterno.objects.count()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(SitioExterno.objects.count(), n_sitio_externo + 1)
        list_url = reverse('sitio_externo_list')
        self.assertRedirects(response, list_url)

    def test_update_sitio_externo(self):
        url = reverse('modificar_sitio_externo', args=[self.sitio_externo.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        nombre_modificado = 'sitio_crm_ventas'
        post_data = self._obtener_post_sitio_externo()
        post_data['nombre'] = nombre_modificado
        response = self.client.post(url, post_data, follow=True)
        self.sitio_externo.refresh_from_db()
        self.assertEqual(self.sitio_externo.nombre, nombre_modificado)
        list_url = reverse('sitio_externo_list')
        self.assertRedirects(response, list_url)

    def test_admin_elimina_sitio_externo(self):
        url = reverse('sitio_externo_delete', args=[self.sitio_externo.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        n_sitio_externo = SitioExterno.objects.count()
        response = self.client.post(url, follow=True)
        self.assertEqual(SitioExterno.objects.count(), n_sitio_externo - 1)
        list_url = reverse('sitio_externo_list')
        self.assertRedirects(response, list_url)

    def test_no_se_permite_eliminar_sitio_externo_asociado_campana(self):
        url = reverse('sitio_externo_delete', args=[self.sitio_externo.pk])
        self.client.login(username=self.admin.username, password=self.PWD)
        CampanaFactory.create(sitio_externo=self.sitio_externo)
        n_sitio_externo = SitioExterno.objects.count()
        self.client.post(url, follow=True)
        self.assertEqual(SitioExterno.objects.count(), n_sitio_externo)

    def usuario_no_admin_no_puede_eliminar_sitio_externo(self):
        self.client.login(username=self.agente.username, password=self.PWD)
        url = reverse('sitio_externo_delete', args=[self.sitio_externo.pk])
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, u'registration/login.html')
