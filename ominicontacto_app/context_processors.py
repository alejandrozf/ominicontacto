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

from django.conf import settings
from django.apps import apps

from constance import config


def admin_supervisor(request):
    es_supervisor_o_admin = request.user.is_authenticated
    if es_supervisor_o_admin:
        es_supervisor_o_admin &= request.user.get_is_administrador() or request.user.is_supervisor
    if es_supervisor_o_admin:
        return {
            'WEBPHONE_CLIENT_ENABLED': config.WEBPHONE_CLIENT_ENABLED,
        }
    return {}


def global_settings(request):
    return {
        'ALLOW_FEEDBACK': settings.ALLOW_FEEDBACK,
    }


def addon_menu_items(request):
    """
    Adds items in the supervision menu asking the app configurations.
    """
    menu_items = []
    if request.user.is_authenticated and request.user.get_tiene_permiso_administracion():
        for app in apps.get_app_configs():
            if hasattr(app, 'supervision_menu_items'):
                app_items = app.supervision_menu_items(request)
                if app_items:
                    menu_items += app_items
    if menu_items:
        return {
            'ADMIN_MENU_ITEMS': menu_items,
        }
    return {}
