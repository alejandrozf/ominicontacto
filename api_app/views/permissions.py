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

from rest_framework.permissions import BasePermission


class EsSupervisorPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores"""

    def has_permission(self, request, view):
        super(EsSupervisorPermiso, self).has_permission(request, view)
        superv_profile = request.user.get_supervisor_profile()
        return superv_profile is not None


class EsAdminPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para administradores"""

    def has_permission(self, request, view):
        super(EsAdminPermiso, self).has_permission(request, view)
        return request.user.get_is_administrador()


class EsAgentePermiso(BasePermission):
    """Permiso para aplicar a vistas solo para agentes"""

    def has_permission(self, request, view):
        super(EsAgentePermiso, self).has_permission(request, view)
        return request.user.get_is_agente()


class EsSupervisorOAgentePermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores normales o agentes"""

    def has_permission(self, request, view):
        super(EsSupervisorOAgentePermiso, self).has_permission(request, view)
        return request.user.get_is_agente() or request.user.get_is_supervisor_normal()
