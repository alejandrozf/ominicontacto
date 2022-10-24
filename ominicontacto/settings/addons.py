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

# Módulo para configurar settings de addons

import os
from ominicontacto.settings.defaults import BASE_DIR
from django.utils.timezone import datetime, timedelta
from datetime import timezone

# TODO: Ver si es posible Moverlo a defaults.py
CONSTANCE_CONFIG = {
    # Key Server data:
    'KEYS_SERVER_HOST': ('https://keys-server.freetech.com.ar', 'KEYS_SERVER_HOST', str),
    'SSL_CERT_FILE': ('/opt/omnileads/cert', 'SSL_CERT_FILE', str),
    'CLIENT_NAME': ('', 'CLIENT_NAME', str),
    'CLIENT_KEY': ('', 'CLIENT_KEY', str),
    'CLIENT_PASSWORD': ('', 'CLIENT_PASSWORD', str),
    'CLIENT_EMAIL': ('', 'CLIENT_EMAIL', str),
    'CLIENT_PHONE': ('', 'CLIENT_PHONE', str),

    # OMniLeads:
    'WOMBAT_DIALER_ALLOW_REFRESH': (False, 'WOMBAT_DIALER_ALLOW_REFRESH', bool),
    'WOMBAT_DIALER_STATE': ('READY', 'WOMBAT_DIALER_STATE', str),
    'WOMBAT_DIALER_UP_SINCE': (datetime(2022, 2, 2, 22, 2, 22, 2222, timezone(timedelta(0))),
                               'WOMBAT_DIALER_UP_SINCE', datetime),

    # Addons configs
    'WEBPHONE_CLIENT_ENABLED': (False, 'WEBPHONE_CLIENT_ENABLED', bool),
    'WEBPHONE_CLIENT_TTL': (1200, 'WEBPHONE_CLIENT_TTL', int),
    'WEBPHONE_VIDEO_DOMAIN': ('meet.jit.si', 'WEBPHONE_VIDEO_DOMAIN', str),
    'LIMIT_USERS_TO': (2, 'LIMIT_USERS_TO', int),
    'LIMIT_AGENTS_CONCURRENT_NUMBER': (1, 'LIMIT_AGENTS_CONCURRENT_NUMBER', int),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'Registration': {
        'fields': ('KEYS_SERVER_HOST', 'SSL_CERT_FILE', 'CLIENT_NAME',
                   'CLIENT_KEY', 'CLIENT_PASSWORD', 'CLIENT_EMAIL',
                   'CLIENT_PHONE',
                   ),
        'collapse': False,
    },
    'Addons Options': {
        'fields': ('WEBPHONE_CLIENT_ENABLED', 'WEBPHONE_CLIENT_TTL', 'WEBPHONE_VIDEO_DOMAIN',
                   'LIMIT_USERS_TO', 'LIMIT_AGENTS_CONCURRENT_NUMBER',
                   ),
        'collapse': False
    },
    'Omnileads': {
        'fields': ('WOMBAT_DIALER_ALLOW_REFRESH', 'WOMBAT_DIALER_STATE', 'WOMBAT_DIALER_UP_SINCE',
                   ),
        'collapse': True
    },
}

ADDONS_APPS = []
ADDONS_LOCALE_PATHS = ()
MIDDLEWARE_PREPPEND = []
MIDDLEWARE_APPEND = []
TEMPLATES_CONTEXT_PROCESORS_APPEND = []

ADDON_URLPATTERNS = [
    # (r'^', 'my_addon_app.urls'),
]


# A partir de aquí se deben adicionar los settings que necesita cada addon
