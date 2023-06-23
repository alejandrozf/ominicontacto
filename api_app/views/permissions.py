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
from rest_framework.permissions import IsAuthenticated
from utiles_globales import request_url_name


class TienePermisoOML(IsAuthenticated):
    """Permiso para aplicar a vistas restringidas por PermisoOML"""

    def has_permission(self, request, view):
        has_permission = super(TienePermisoOML, self).has_permission(request, view)
        if not has_permission:
            return has_permission

        current_url_name = request_url_name(request)
        if hasattr(view, 'basename') and view.basename:
            current_url_name = view.basename
        return request.user.tiene_permiso_oml(current_url_name)
