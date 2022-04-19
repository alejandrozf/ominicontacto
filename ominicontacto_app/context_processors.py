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

from operator import itemgetter

from django.conf import settings
from django.apps import apps

from ominicontacto_app.permisos import PermisoOML
import os


def global_settings(request):
    return {
        'ALLOW_FEEDBACK': settings.ALLOW_FEEDBACK,
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY'),
        'GOOGLE_MAPS_CENTER': os.getenv('GOOGLE_MAPS_CENTER'),
    }


def addon_menu_items(request):
    """
    Adds items in the supervision menu asking the app configurations.
    """
    menu_items = []
    if request.user.is_authenticated and request.user.get_tiene_permiso_administracion():
        rol = request.user.rol
        permissions = set(PermisoOML.objects.filter(group=rol).values_list('codename', flat=True))
        for app in apps.get_app_configs():
            if hasattr(app, 'supervision_menu_items'):
                app_items = app.supervision_menu_items(request, permissions)
                if app_items:
                    menu_items += app_items
    if menu_items:
        menu_items.sort(key=itemgetter('order'))
        return {
            'ADMIN_MENU_ITEMS': menu_items,
        }
    return {}
