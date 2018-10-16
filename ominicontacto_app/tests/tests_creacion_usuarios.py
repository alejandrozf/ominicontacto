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
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

from mock import patch

import logging as _logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import ModuloFactory, GrupoFactory
from ominicontacto_app.models import Grupo, Modulo, User, SupervisorProfile
from ominicontacto_app.services.asterisk_service import ActivacionAgenteService

logger = _logging.getLogger(__name__)


class CreacionUsuariosTest(OMLBaseTest):

    def setUp(self):
        super(CreacionUsuariosTest, self).setUp()
        self.admin = self.crear_administrador(username='admin1')
        self.modulo1 = ModuloFactory(nombre='phone')
        self.grupo1 = GrupoFactory(nombre='grupo1')
        # self.supervisor1

    @patch.object(ActivacionAgenteService, 'activar')
    def test_crear_supervisor(self, activar):
        self.client.login(username=self.admin.username, password=PASSWORD)
        url = reverse('user_nuevo')
        response = self.client.get(url, follow=True)

        data = {
            'custom_user_wizard-current_step': '0',
            '0-username': 'supervisor1',
            '0-first_name': 'supervisor1',
            '0-last_name': 'supervisor1',
            '0-email': 'asd@asd.com',
            '0-password1': PASSWORD,
            '0-password2': PASSWORD,
            '0-is_supervisor': True,
            '0-is_agente': False,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['titulo'], _('Nuevo Usuario: Perfil de Supervisor'))

        data = {
            'custom_user_wizard-current_step': '1',
            '1-rol': SupervisorProfile.ROL_GERENTE,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_supervisor = User.objects.get(username='supervisor1')
        self.assertTrue(user_supervisor.is_supervisor)
        self.assertFalse(user_supervisor.is_agente)
        supervisor = user_supervisor.get_supervisor_profile()
        self.assertFalse(supervisor.is_administrador)
        self.assertFalse(supervisor.is_customer)

    @patch.object(ActivacionAgenteService, 'activar')
    def test_crear_agente(self, activar):
        self.client.login(username=self.admin.username, password=PASSWORD)
        url = reverse('user_nuevo')
        response = self.client.get(url, follow=True)

        data = {
            'custom_user_wizard-current_step': '0',
            '0-username': 'agente1',
            '0-first_name': 'agente1',
            '0-last_name': 'agente1',
            '0-email': 'asd@asd.com',
            '0-password1': PASSWORD,
            '0-password2': PASSWORD,
            '0-is_supervisor': False,
            '0-is_agente': True,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['titulo'], _('Nuevo Usuario: Perfil de Agente'))

        data = {
            'custom_user_wizard-current_step': '2',
            '2-grupo': self.grupo1.id,
            '2-modulos': self.modulo1.id,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_agente = User.objects.get(username='agente1')
        self.assertTrue(user_agente.is_agente)
        self.assertFalse(user_agente.is_supervisor)
        agente = user_agente.get_agente_profile()
        self.assertEqual(agente.grupo, self.grupo1)
        self.assertIn(self.modulo1, agente.modulos.all())

    def test_deshabilitar_is_agente_si_no_hay_modulo_o_grupo(self):
        self.client.login(username=self.admin.username, password=PASSWORD)

        # Sin Modulo
        Modulo.objects.all().delete()
        url = reverse('user_nuevo')
        response = self.client.get(url, follow=True)
        self.assertContains(response, u'Para poder crear un Usuario Agente asegurese de')

        # Manera poco elegante de ver si el campo is_agente esta deshabilitado
        field_is_agente = filtrar_linea(response.content.splitlines(), 'name="0-is_agente"')
        self.assertNotEqual(field_is_agente[0].find('disabled'), 1)

        # Sin Grupo
        self.modulo1 = ModuloFactory(nombre='phone')
        Grupo.objects.all().delete()
        response = self.client.get(url, follow=True)
        self.assertContains(response, u'Para poder crear un Usuario Agente asegurese de')

        self.grupo1 = GrupoFactory(nombre='grupo1')
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, u'Para poder crear un Usuario Agente asegurese de')

        # Manera poco elegante de ver si el campo is_agente no esta deshabilitado
        field_is_agente = filtrar_linea(response.content.splitlines(), 'name="0-is_agente"')
        self.assertEqual(field_is_agente[0].find(u'disabled'), -1)


def filtrar_linea(lineas, texto):
    for x in lineas:
        if x.decode('utf-8').find(texto) != -1:
            return x

    # TODO: Al desarrollar bien los permisos segun el rol del Supervisor/Administrador
    # def test_supervisor solo puede crear agentes (no clientes?)
    # def test_gerente puede crear supervisores y clientes o agentes (no gerentes)
    # def test_gerente solo puede asignar grupos que él mismo creó
    # def test_Supervisor solo puede asignar grupos propios
