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
from django.utils.translation import ugettext as _
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Group
from ominicontacto_app.errors import OmlError
from ominicontacto_app.models import User
from ominicontacto_app.permisos import PermisoOML, DESCRIPCIONES


class Command(BaseCommand):

    def actualizar_permisos(self):
        nombres_de_permisos = []
        gestor_de_permisos = GestorDePermisos()

        # TODO: Asegurarse que sea atómico: todo o nada!

        # Iterar por todas las apps instaladas.
        for app in apps.get_app_configs():
            if hasattr(app, 'configuraciones_de_permisos'):
                configuraciones_de_permisos = app.configuraciones_de_permisos()
                for configuracion in configuraciones_de_permisos:
                    configuracion_de_permiso = ConfiguracionDePermiso(
                        app.name, configuracion, gestor_de_permisos.roles_predefinidos)
                    if configuracion_de_permiso.nombre in nombres_de_permisos:
                        raise ConfiguracionDePermisoError(
                            nombre=app.name,
                            mensaje=_('El nombre del permiso esta repetido: {0}').format(
                                configuracion_de_permiso.nombre))
                    gestor_de_permisos.gestionar_permiso(configuracion_de_permiso)
                    nombres_de_permisos.append(configuracion_de_permiso.nombre)
        # TODO: Discutir
        # Borrar permisos viejos que ya no están en nombres_de_permisos.
        #     (que pasa con addons? si se olvidan de configurarla se borraran los permisos de
        #      roles no predefinidos)
        # Borrar solo permisos viejos que esten en una lista de borrados en cada app?

    def handle(self, *args, **options):
        try:
            self.actualizar_permisos()
        except Exception as e:
            raise CommandError('Fallo del comando: {0}'.format(e))


class GestorDePermisos(object):

    def __init__(self, *args, **kwargs):
        super(GestorDePermisos, self).__init__(*args, **kwargs)
        self.roles_predefinidos = {
            User.ADMINISTRADOR: Group.objects.get(name=User.ADMINISTRADOR),
            User.GERENTE: Group.objects.get(name=User.GERENTE),
            User.SUPERVISOR: Group.objects.get(name=User.SUPERVISOR),
            User.REFERENTE: Group.objects.get(name=User.REFERENTE),
            User.AGENTE: Group.objects.get(name=User.AGENTE),
        }

    def _obtener_permiso(self, nombre):
        permiso, created = PermisoOML.objects.get_or_create(codename=nombre)
        return permiso

    def gestionar_permiso(self, configuracion_de_permiso):
        permiso = self._obtener_permiso(configuracion_de_permiso.nombre)
        for nombre_rol, rol in self.roles_predefinidos.items():
            if rol in configuracion_de_permiso.roles:
                rol.permissions.add(permiso)
            else:
                rol.permissions.remove(permiso)


class ConfiguracionDePermiso(object):
    def __init__(self, app_name, configuracion, roles_predefinidos):
        self.app_name = app_name
        if 'nombre' not in configuracion:
            raise ConfiguracionDePermisoError(
                app_name=self.app_name,
                nombre=app_name, mensaje=_('Campo "nombre" no definido'))
        self.nombre = configuracion['nombre']
        if self.nombre not in DESCRIPCIONES:
            raise ConfiguracionDePermisoError(
                app_name=app_name,
                mensaje=_('No se definió una descripción para el permiso: {0}').format(
                    self.nombre))
        if 'roles' not in configuracion:
            raise ConfiguracionDePermisoError(
                app_name=app_name, mensaje=_('Campo "roles" no definido'))
        if type(configuracion['roles']) not in [list, tuple, ]:
            raise ConfiguracionDePermisoError(
                app_name=app_name,
                mensaje=_('Campo "roles" debe ser lista o tupla para permiso: {0}').format(
                    self.nombre))
        self.nombre = configuracion['nombre']
        self.roles = []
        for rol in configuracion['roles']:
            if rol not in roles_predefinidos:
                raise ConfiguracionDePermisoError(
                    app_name=app_name,
                    mensaje=_('Rol predefinido inexistente: {0}, para permiso: {1}').format(
                        rol, self.nombre))
            self.roles.append(roles_predefinidos[rol])


class ConfiguracionDePermisoError(OmlError):
    def __init__(self, app_name, mensaje, *args, **kwargs):
        super(ConfiguracionDePermisoError, self).__init__(message=mensaje, *args, **kwargs)
