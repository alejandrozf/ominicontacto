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

"""
Tests relacionados al Blacklist
"""
from __future__ import unicode_literals
from mock import patch
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import BlackListFactory


class TestsBlacklist (OMLBaseTest):
    PWD = u'admin123'

    def setUp(self, *args, **kwargs):
        super(TestsBlacklist, self).setUp(*args, **kwargs)
        self.admin = self.crear_administrador()
        self.agente = self.crear_user_agente()
        self.agente.set_password(self.PWD)
        self.admin.set_password(self.PWD)
        self.blacklist = BlackListFactory()
        self.client.login(username=self.admin.username, password=self.PWD)

    def _post_blacklist_contact(self):
        return {
            'telefono': '12341234',
        }

    def test_mostrar_ultima_blacklist_cargada(self):
        url = reverse('black_list_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.blacklist.nombre)

    def test_get_blacklist(self):
        url = reverse('black_list_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    @patch('ominicontacto_app.services.asterisk.redis_database.BlacklistFamily.delete_family')
    def test_delete_blacklist(self, delete_family):
        url = reverse('eliminar_blacklist', args=[self.blacklist.pk])
        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 200)

    @patch('ominicontacto_app.services.asterisk.redis_database.BlacklistFamily.regenerar_families')
    def test_add_contact_to_blacklist(self, regenerar_families):
        url = reverse('nuevo_contacto_blacklist', args=[self.blacklist.pk])
        post_data = self._post_blacklist_contact()
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
