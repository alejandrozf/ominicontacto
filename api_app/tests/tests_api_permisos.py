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
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.permisos import PermisoOML
from ominicontacto_app.models import User


class RolesYPermisosAPITest(OMLBaseTest):
    def setUp(self):
        super(RolesYPermisosAPITest, self).setUp()

        self.administrador = self.crear_administrador()
        self.client.login(username=self.administrador.username, password=PASSWORD)

    def test_api_crear_rol_ok(self):
        nombre_rol = 'Rol_1'
        self.assertFalse(Group.objects.filter(name=nombre_rol).exists())
        url = reverse('api_new_role')
        response = self.client.post(url, json.dumps({'name': nombre_rol}),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        self.assertTrue(Group.objects.filter(name=nombre_rol).exists())

    def test_api_crear_rol_no_permite_nombres_ya_existentes(self):
        nombre_rol = 'Rol_1'
        Group.objects.create(name=nombre_rol)
        self.assertTrue(Group.objects.filter(name=nombre_rol).exists())
        url = reverse('api_new_role')
        response = self.client.post(url, json.dumps({'name': nombre_rol}),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Ya existe un rol con ese nombre'))

    def test_api_crear_rol_valida_parametros(self):
        nombre_rol = 'Rol_1'
        self.assertFalse(Group.objects.filter(name=nombre_rol).exists())
        url = reverse('api_new_role')
        response = self.client.post(url, json.dumps({'nombre': nombre_rol}),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Se esperaba el campo "name"'))

    def test_asignar_permisos_a_rol_ok(self):
        nombre_rol = 'Rol_1'
        rol = Group.objects.create(name=nombre_rol)
        nombres_permisos = ['api_new_role', 'api_update_role_permissions']
        id_permisos = list(PermisoOML.objects.filter(
            codename__in=nombres_permisos).values_list('id', flat=True))
        url = reverse('api_update_role_permissions')
        post_data = json.dumps({'role_id': rol.id, 'permissions': id_permisos})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        ids_asignados = list(rol.permissions.values_list('id', flat=True))
        self.assertEqual(set(id_permisos), set(ids_asignados))

    def test_api_asignar_permisos_valida_parametros(self):
        nombre_rol = 'Rol_1'
        self.assertFalse(Group.objects.filter(name=nombre_rol).exists())
        url = reverse('api_update_role_permissions')
        rol = Group.objects.create(name=nombre_rol)
        nombres_permisos = ['api_new_role', 'api_update_role_permissions']
        id_permisos = list(PermisoOML.objects.filter(
            codename__in=nombres_permisos).values_list('id', flat=True))

        # Falta campo role_id
        post_data = json.dumps({'role_': rol.id, 'permissions': id_permisos})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Se esperaba el campo "role_id" (numérico)'))

        # ID Incorrecto
        post_data = json.dumps({'role_id': rol.id + 1, 'permissions': id_permisos})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Id de Rol incorrecto'))

        # No permite editar roles DEFAULT
        rol_inmutable = Group.objects.get(name=User.SUPERVISOR)
        post_data = json.dumps({'role_id': rol_inmutable.id, 'permissions': id_permisos})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Id de Rol incorrecto'))

        # Falta campo permissions
        rol_inmutable = Group.objects.get(name=User.SUPERVISOR)
        post_data = json.dumps({'role_id': rol.id, 'permisos': id_permisos})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('Se esperaba el campo "permissions" (lista)'))

        # Campo permissions no es Lista
        rol_inmutable = Group.objects.get(name=User.SUPERVISOR)
        post_data = json.dumps({'role_id': rol.id, 'permisos': id_permisos[0]})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('Se esperaba el campo "permissions" (lista)'))

        # Campo permissions no es Lista
        rol_inmutable = Group.objects.get(name=User.SUPERVISOR)
        id_inexistente = PermisoOML.objects.all().order_by('id').last().id + 1
        post_data = json.dumps({'role_id': rol.id, 'permissions': [id_inexistente]})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('Lista de permisos incorrecta'))

    def test_api_eliminar_rol_ok(self):
        nombre_rol = 'Rol_1'
        rol = Group.objects.create(name=nombre_rol)
        url = reverse('api_delete_role')
        post_data = json.dumps({'role_id': rol.id})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        self.assertFalse(Group.objects.filter(id=rol.id).exists())

    def test_api_eliminar_rol_no_deja_borrar_rol_asignado(self):
        nombre_rol = 'Rol_1'
        rol = Group.objects.create(name=nombre_rol)
        supervisor = self.crear_supervisor_profile()
        supervisor.user.groups.set([rol])
        url = reverse('api_delete_role')
        post_data = json.dumps({'role_id': rol.id})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'],
                         _('No se puede borrar un rol asignado a usuarios.'))
        self.assertTrue(Group.objects.filter(id=rol.id).exists())

    def test_api_eliminar_rol_no_deja_borrar_rol_predefinido(self):
        url = reverse('api_delete_role')
        post_data = json.dumps({'role_id': Group.objects.get(name=User.SUPERVISOR).id})
        response = self.client.post(url, post_data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(response.json()['message'], _('Id de Rol incorrecto'))
        self.assertTrue(Group.objects.filter(name=User.SUPERVISOR).exists())
