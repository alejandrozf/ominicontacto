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
    'EXTERNAL_AUTH_TYPE': ('0', 'EXTERNAL_AUTH_TYPE', str),
    'EXTERNAL_AUTH_SERVER': ('', 'EXTERNAL_AUTH_SERVER', str),
    'EXTERNAL_AUTH_DN': ('', 'EXTERNAL_AUTH_DN', str),
    'EXTERNAL_AUTH_ACTIVATION': ('', 'EXTERNAL_AUTH_ACTIVATION', str),

    # Addons configs
    'WEBPHONE_CLIENT_ENABLED': (False, 'WEBPHONE_CLIENT_ENABLED', bool),
    'WEBPHONE_CLIENT_TTL': (1200, 'WEBPHONE_CLIENT_TTL', int),
    'WEBPHONE_VIDEO_DOMAIN': ('meet.jit.si', 'WEBPHONE_VIDEO_DOMAIN', str),
    'LIMIT_USERS_ACTIVE': (False, 'LIMIT_USERS_ACTIVE', bool),
    'LIMIT_USERS_TO': (2, 'LIMIT_USERS_TO', int),
    'LIMIT_AGENTS_CONCURRENT_ACTIVE': (False, 'LIMIT_AGENTS_CONCURRENT_ACTIVE', bool),
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
                   'LIMIT_USERS_ACTIVE', 'LIMIT_USERS_TO',
                   'LIMIT_AGENTS_CONCURRENT_ACTIVE', 'LIMIT_AGENTS_CONCURRENT_NUMBER',
                   ),
        'collapse': False
    },
    'Omnileads': {
        'fields': ('WOMBAT_DIALER_ALLOW_REFRESH', 'WOMBAT_DIALER_STATE', 'WOMBAT_DIALER_UP_SINCE',
                   'EXTERNAL_AUTH_TYPE', 'EXTERNAL_AUTH_SERVER', 'EXTERNAL_AUTH_DN',
                   'EXTERNAL_AUTH_ACTIVATION',
                   ),
        'collapse': True
    },
}

ADDONS_APPS = []
ADDONS_LOCALE_PATHS = ()
MIDDLEWARE_PREPPEND = []
MIDDLEWARE_APPEND = []
TEMPLATES_CONTEXT_PROCESORS_APPEND = []

ADDON_URLPATTERNS = []

if not os.getenv('LIMIT_USERS_VERSION', '') == '':
    ADDONS_APPS.append('limit_users_app.apps.LimitUsersAppConfig')
    MIDDLEWARE_APPEND.append('limit_users_app.middleware.limits.LimitUsersMiddleware')
if not os.getenv('PREMIUM_REPORTS_VERSION', '') == '':
    ADDONS_APPS.append('premium_reports_app.apps.PremiumReportsAppConfig')
    ADDON_URLPATTERNS.append((r'^', 'premium_reports_app.urls'))
    ADDONS_LOCALE_PATHS += (os.path.join(BASE_DIR, 'premium_reports_app/locale'), )
if not os.getenv('SURVEY_VERSION', '') == '':
    ADDONS_APPS.append('survey_app.apps.SurveyAppConfig')
    ADDON_URLPATTERNS.append((r'^', 'survey_app.urls'))
    ADDONS_LOCALE_PATHS += (os.path.join(BASE_DIR, 'survey_app/locale'), )
if not os.getenv('WALLBOARD_VERSION', '') == '':
    ADDONS_APPS.append('wallboard_app.apps.WallboardAppConfig')
    ADDON_URLPATTERNS.append((r'^', 'wallboard_app.urls'))
    ADDONS_LOCALE_PATHS += (os.path.join(BASE_DIR, 'wallboard_app/locale'), )
if not os.getenv('WEBPHONE_CLIENT_VERSION', '') == '':
    ADDONS_APPS.append('webphone_client_app.apps.WebphoneClientAppConfig')
    ADDON_URLPATTERNS.append((r'^', 'webphone_client_app.urls'))
    ADDONS_LOCALE_PATHS += (os.path.join(BASE_DIR, 'webphone_client_app/locale'), )
