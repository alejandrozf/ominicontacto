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

        self.back_lists = BlackListFactory()
        self.nueva_blacklist = BlackListFactory()

        self.client.login(username=self.admin.username, password=self.PWD)

    def test_mostrar_ultima_blacklist_cargada(self):
        url = reverse('black_list_list')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.nueva_blacklist.nombre)

    def test_mostrar_una_blacklist(self):
        url = reverse('black_list_list')
        response = self.client.get(url, follow=True)
        data = response.context_data['object_list']
        n_blacklist = data.count()
        self.assertEqual(n_blacklist, 1)
