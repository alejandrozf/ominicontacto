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

from operator import itemgetter

from django.conf import settings
from django.apps import apps

from constance import config
from ominicontacto_app.permisos import PermisoOML
import os

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage


def global_settings(request):
    if config.FAVICON == settings.CONSTANCE_CONFIG['FAVICON'][0]:
        FAVICON = staticfiles_storage.url(config.FAVICON)
    else:
        FAVICON = default_storage.url(config.FAVICON)
    if config.IC_LOGO == settings.CONSTANCE_CONFIG['IC_LOGO'][0]:
        IC_LOGO = staticfiles_storage.url(config.IC_LOGO)
    else:
        IC_LOGO = default_storage.url(config.IC_LOGO)
    if config.IC_LOGO_FULL == settings.CONSTANCE_CONFIG['IC_LOGO_FULL'][0]:
        IC_LOGO_FULL = staticfiles_storage.url(config.IC_LOGO_FULL)
    else:
        IC_LOGO_FULL = default_storage.url(config.IC_LOGO_FULL)
    if config.IC_LOGO_SYMBOL == settings.CONSTANCE_CONFIG['IC_LOGO_SYMBOL'][0]:
        IC_LOGO_SYMBOL = staticfiles_storage.url(config.IC_LOGO_SYMBOL)
    else:
        IC_LOGO_SYMBOL = default_storage.url(config.IC_LOGO_SYMBOL)
    return {
        'ASTERISK_TM': config.ASTERISK_TM,
        'OMNILEADS_TM': config.OMNILEADS_TM,
        'PRIMARY_COLOR': config.PRIMARY_COLOR,
        'PRIMARY_LIGHT_COLOR': config.PRIMARY_LIGHT_COLOR,
        'SECONDARY_COLOR': config.SECONDARY_COLOR,
        'FAVICON': FAVICON,
        'IC_LOGO': IC_LOGO,
        'IC_LOGO_FULL': IC_LOGO_FULL,
        'IC_LOGO_SYMBOL': IC_LOGO_SYMBOL,
        'ALLOW_FEEDBACK': settings.ALLOW_FEEDBACK,
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY'),
        'GOOGLE_MAPS_CENTER': os.getenv('GOOGLE_MAPS_CENTER'),
        'ENTERPRISE': os.getenv('ENTERPRISE'),
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
