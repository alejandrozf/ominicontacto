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

# Módulo para configurar settings de addons

import os
from ominicontacto.settings.defaults import BASE_DIR

CONSTANCE_CONFIG = {
    'KEYS_SERVER_HOST': ('https://keys-server.freetech.com.ar:20852', 'KEYS_SERVER_HOST', str),
    'SSL_CERT_FILE': ('/opt/omnileads/cert', 'SSL_CERT_FILE', str),
    'CLIENT_NAME': ('', 'CLIENT_NAME', str),
    'CLIENT_KEY': ('', 'CLIENT_KEY', str),
    'CLIENT_PASSWORD': ('', 'CLIENT_PASSWORD', str),
    'CLIENT_EMAIL': ('', 'CLIENT_EMAIL', str),
    'CLIENT_PHONE': ('', 'CLIENT_PHONE', str),
    'CLIENT_PHONE': ('', 'CLIENT_PHONE', str),
    'WEBPHONE_CLIENT_ENABLED': (False, 'WEBPHONE_CLIENT_ENABLED', bool),
    'WEBPHONE_CLIENT_TTL': (1200, 'WEBPHONE_CLIENT_TTL', int),
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
