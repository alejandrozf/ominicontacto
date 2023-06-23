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

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

from mock import patch

import logging as _logging

from django.urls import reverse
from django.utils.translation import gettext as _

from django.contrib.auth.models import Group
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    GrupoFactory, CampanaFactory, QueueMemberFactory, QueueFactory)
from ominicontacto_app.models import Grupo, User, Campana
from ominicontacto_app.services.asterisk_service import ActivacionAgenteService

logger = _logging.getLogger(__name__)

COMPLEX_PASSWORD = '*FTS*OML1*'


class ABMUsuariosTest(OMLBaseTest):

    def setUp(self):
        super(ABMUsuariosTest, self).setUp()
        self.admin = self.crear_administrador(username='admin1')
        self.gerente = self.crear_supervisor_profile(rol=User.GERENTE, user=None)
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR, user=None)

        self.grupo1 = GrupoFactory(nombre='grupo1')
        self.rol_gerente = Group.objects.get(name=User.GERENTE)
        self.rol_supervisor = Group.objects.get(name=User.SUPERVISOR)
        self.rol_agente = Group.objects.get(name=User.AGENTE)
        self.client.login(username=self.admin.username, password=PASSWORD)

        self.agente = self.crear_agente_profile()
        self.campana = CampanaFactory(estado=Campana.ESTADO_ACTIVA, type=Campana.TYPE_MANUAL)
        QueueFactory(campana=self.campana)
        QueueMemberFactory.create(member=self.agente, queue_name=self.campana.queue_campana)


class CreacionUsuariosTest(ABMUsuariosTest):

    @patch.object(ActivacionAgenteService, 'activar')
    @patch('ominicontacto_app.services.kamailio_service.KamailioService.generar_sip_password')
    def test_crear_supervisor(self, generar_secret_key, activar):
        url = reverse('user_nuevo')
        response = self.client.get(url, follow=True)

        data = {
            'custom_user_wizard-current_step': '0',
            '0-username': 'supervisor1',
            '0-first_name': 'supervisor1',
            '0-last_name': 'supervisor1',
            '0-email': 'asd@asd.com',
            '0-password1': COMPLEX_PASSWORD,
            '0-password2': COMPLEX_PASSWORD,
            '0-rol': self.rol_supervisor.id
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

    @patch.object(ActivacionAgenteService, 'activar_agente')
    def test_crear_agente(self, activar_agente):
        url = reverse('user_nuevo')
        response = self.client.get(url, follow=True)

        data = {
            'custom_user_wizard-current_step': '0',
            '0-username': 'agente1',
            '0-first_name': 'agente1',
            '0-last_name': 'agente1',
            '0-email': 'asd@asd.com',
            '0-password1': COMPLEX_PASSWORD,
            '0-password2': COMPLEX_PASSWORD,
            '0-rol': self.rol_agente.id,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['titulo'], _('Nuevo Usuario: Perfil de Agente'))

        data = {
            'custom_user_wizard-current_step': '1',
            '1-grupo': self.grupo1.id,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_agente = User.objects.get(username='agente1')
        self.assertTrue(user_agente.is_agente)
        self.assertFalse(user_agente.is_supervisor)
        agente = user_agente.get_agente_profile()
        self.assertEqual(agente.grupo, self.grupo1)

    def test_deshabilitar_is_agente_si_no_hay_grupo(self):
        url = reverse('user_nuevo')

        # Sin Grupo
        Grupo.objects.all().delete()
        response = self.client.get(url, follow=True)
        self.assertContains(response, u'Para poder crear un Usuario Agente asegurese de')

        # No debe aparecer la opcion de rol Agente
        choices = response.context_data['form'].fields['rol'].choices
        roles_disponibles = [choice[1] for choice in choices]
        self.assertNotIn(User.AGENTE, roles_disponibles)

        self.grupo1 = GrupoFactory(nombre='grupo1')
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, u'Para poder crear un Usuario Agente asegurese de')

        # Debe aparecer la opcion de rol Agente
        choices = response.context_data['form'].fields['rol'].choices
        roles_disponibles = [choice[1] for choice in choices]
        self.assertIn(User.AGENTE, roles_disponibles)


def filtrar_linea(lineas, texto):
    for x in lineas:
        if x.decode('utf-8').find(texto) != -1:
            return x

    # TODO: Al desarrollar bien los permisos segun el rol del Supervisor/Administrador
    # def test_supervisor solo puede crear agentes (no clientes?)
    # def test_gerente puede crear supervisores y clientes o agentes (no gerentes)
    # def test_gerente solo puede asignar grupos que él mismo creó
    # def test_Supervisor solo puede asignar grupos propios


class ListaUsuariosTest(ABMUsuariosTest):

    def setUp(self):
        super(ListaUsuariosTest, self).setUp()
        self.admin2 = self.crear_administrador(username='admin2')

    def test_admin_ve_links_para_editar_y_borrar_todos(self):
        url = reverse('user_list', kwargs={"page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('user_delete', kwargs={'pk': self.admin2.id}))
        self.assertContains(
            response, reverse('user_delete', kwargs={'pk': self.gerente.user.id}))
        self.assertContains(
            response, reverse('user_delete', kwargs={'pk': self.supervisor.user.id}))
        self.assertContains(response, reverse('agent_delete', kwargs={'pk': self.agente.user.id}))

        self.assertContains(response, reverse('user_update', kwargs={'pk': self.admin2.id}))
        self.assertContains(
            response, reverse('user_update', kwargs={'pk': self.gerente.user.id}))
        self.assertContains(
            response, reverse('user_update', kwargs={'pk': self.supervisor.user.id}))
        self.assertContains(response, reverse('agent_update', kwargs={'pk': self.agente.user.id}))

    def test_supervisor_solo_ve_links_para_editar_o_borrar_agentes(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        url = reverse('user_list', kwargs={"page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('user_delete', kwargs={'pk': self.admin.id}))
        self.assertNotContains(
            response, reverse('user_delete', kwargs={'pk': self.gerente.user.id}))
        self.assertNotContains(
            response, reverse('user_delete', kwargs={'pk': self.supervisor.user.id}))
        self.assertContains(
            response, reverse('agent_delete', kwargs={'pk': self.agente.user.id}))

        self.assertNotContains(response, reverse('user_update', kwargs={'pk': self.admin.id}))
        self.assertNotContains(
            response, reverse('user_update', kwargs={'pk': self.gerente.user.id}))
        self.assertNotContains(
            response, reverse('user_update', kwargs={'pk': self.supervisor.user.id}))
        self.assertContains(
            response, reverse('agent_update', kwargs={'pk': self.agente.user.id}))


class BorrarUsuariosTest(ABMUsuariosTest):

    def setUp(self):
        super(BorrarUsuariosTest, self).setUp()

    def test_admin_puede_borrar_admin(self):
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_delete', kwargs={'pk': admin2.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        admin2.refresh_from_db()
        self.assertTrue(admin2.borrado)

    def test_gerente_no_puede_borrar_admin(self):
        self.client.login(username=self.gerente.user.username, password=PASSWORD)
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_delete', kwargs={'pk': admin2.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        admin2.refresh_from_db()
        self.assertFalse(admin2.borrado)

        message = _('No tiene permiso para eliminar al usuario {}'.format(
            admin2.get_full_name()))
        self.assertContains(response, message)

    def test_supevisor_no_puede_borrar_users(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_delete', kwargs={'pk': admin2.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_supevisor_no_puede_borrar_agentes_no_asignados_a_sus_campanas(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        user_agente = self.agente.user
        url = reverse('agent_delete', kwargs={'pk': user_agente.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_agente.refresh_from_db()
        self.assertFalse(user_agente.borrado)

        message = _('No tiene permiso para eliminar al usuario {}'.format(
            user_agente.get_full_name()))
        self.assertContains(response, message)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    @patch('ominicontacto_app.services.creacion_queue.ActivacionQueueService.activar')
    @patch('ominicontacto_app.views_user_profiles.remover_agente_cola_asterisk')
    def test_supervisor_puede_borrar_agentes_asignados_a_sus_campanas(
            self, remover_agente_cola_asterisk, activar, connect):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        self.campana.supervisors.add(self.supervisor.user)
        user_agente = self.agente.user
        url = reverse('agent_delete', kwargs={'pk': user_agente.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        remover_agente_cola_asterisk.assert_called()
        activar.assert_called()
        connect.assert_called()
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_agente.refresh_from_db()
        self.assertTrue(user_agente.borrado)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    @patch('ominicontacto_app.services.creacion_queue.ActivacionQueueService.activar')
    @patch('ominicontacto_app.views_user_profiles.remover_agente_cola_asterisk')
    def test_supervisor_puede_borrar_agentes_propios_no_asignados_a_sus_campanas(
            self, remover_agente_cola_asterisk, activar, connect):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        user_agente = self.agente.user
        self.agente.reported_by = self.supervisor.user
        self.agente.save()
        url = reverse('agent_delete', kwargs={'pk': user_agente.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        remover_agente_cola_asterisk.assert_called()
        activar.assert_called()
        connect.assert_called()
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        user_agente.refresh_from_db()
        self.assertTrue(user_agente.borrado)


class EditarUsuariosTest(ABMUsuariosTest):

    def setUp(self):
        super(EditarUsuariosTest, self).setUp()

    def test_admin_puede_editar_admin(self):
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_update', kwargs={'pk': admin2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_gerente_no_puede_editar_admin(self):
        self.client.login(username=self.gerente.user.username, password=PASSWORD)
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_update', kwargs={'pk': admin2.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))

        message = _('No tiene permiso para editar al usuario {}'.format(
            admin2.get_full_name()))
        self.assertContains(response, message)

    def test_supevisor_no_puede_editar_users(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        admin2 = self.crear_administrador(username='admin2')
        url = reverse('user_update', kwargs={'pk': admin2.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_supevisor_no_puede_editar_agentes_no_asignados_a_sus_campanas(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        user_agente = self.agente.user
        url = reverse('agent_update', kwargs={'pk': user_agente.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list', kwargs={"page": 1}))
        message = _('No tiene permiso para editar al usuario {}'.format(
            user_agente.get_full_name()))
        self.assertContains(response, message)

    def test_supevisor_puede_editar_agentes_asignados_a_sus_campanas(self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        self.campana.supervisors.add(self.supervisor.user)
        user_agente = self.agente.user
        url = reverse('agent_update', kwargs={'pk': user_agente.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
