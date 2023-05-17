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

from .addons import *
from .defaults import *
from .checks import (check_settings_variables, process_middleware_settings,
                     check_asterisk_connect_settings, check_audio_conversor_settings)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += ['debug_toolbar', 'corsheaders'] + ADDONS_APPS
LOCALE_PATHS += ADDONS_LOCALE_PATHS
MIDDLEWARE_CLASSES = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']
DJANGO_CORS_HEADERS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['*']
CORS_REPLACE_HTTPS_REFERER = True
CORS_ORIGIN_WHITELIST = [
    'http://*'
]
INTERNAL_IPS = ['127.0.0.1']

TOKEN_EXPIRED_AFTER_SECONDS = 6 * 60  # 6 minutos


def show_toolbar(request):
    return False


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

try:
    from .oml_settings_local import *
except ImportError:
    raise Exception("No se pudo importar oml_settings_local")

(MIDDLEWARE_PREPPEND, MIDDLEWARE_APPEND, MIDDLEWARE_CLASSES,
 TEMPLATES_CONTEXT_PROCESORS_APPEND, TEMPLATES) = process_middleware_settings(
     MIDDLEWARE_PREPPEND, MIDDLEWARE_APPEND, MIDDLEWARE_CLASSES,
     TEMPLATES_CONTEXT_PROCESORS_APPEND, TEMPLATES)

VARIABLES_LIST = [
    (DEFENDER_BEHIND_REVERSE_PROXY, 'DEFENDER_BEHIND_REVERSE_PROXY'),
    (OML_ASTERISK_REMOTEPATH, 'OML_ASTERISK_REMOTEPATH'),
    (OML_SIP_FILENAME, 'OML_SIP_FILENAME'),
    (OML_QUEUES_FILENAME, 'OML_QUEUES_FILENAME'),
    (EPHEMERAL_USER_TTL, 'EPHEMERAL_USER_TTL'),
    (OML_KAMAILIO_HOSTNAME, 'OML_KAMAILIO_HOSTNAME'),
    (OML_OMNILEADS_HOSTNAME, 'OML_OMNILEADS_HOSTNAME'),
    (OML_WOMBAT_URL, 'OML_WOMBAT_URL'),
    (OML_WOMBAT_FILENAME, 'OML_WOMBAT_FILENAME'),
    (OML_RUTAS_SALIENTES_FILENAME, 'OML_RUTAS_SALIENTES_FILENAME'),
    (OML_WOMBAT_USER, 'OML_WOMBAT_USER'),
    (OML_WOMBAT_PASSWORD, 'OML_WOMBAT_PASSWORD'),
    (OML_WOMBAT_TIMEOUT, 'OML_WOMBAT_TIMEOUT'),
    (SIP_SECRET_KEY, 'SIP_SECRET_KEY'),
    (SENDFILE_ROOT, 'SENDFILE_ROOT'),
    (SENDFILE_URL, 'SENDFILE_URL'),
    (SENDFILE_BACKEND, 'SENDFILE_BACKEND'),
    (TMPL_OML_AUDIO_CONVERSOR, 'TMPL_OML_AUDIO_CONVERSOR'),
    (CALIFICACION_REAGENDA, 'CALIFICACION_REAGENDA'),
    (DURACION_ASIGNACION_CONTACTO_PREVIEW, 'DURACION_ASIGNACION_CONTACTO_PREVIEW'),
    (ASTERISK_AUDIO_PATH, 'ASTERISK_AUDIO_PATH'),
    (OML_AUDIO_FOLDER, 'OML_AUDIO_FOLDER'),
    (OML_PLAYLIST_FOLDER, 'OML_PLAYLIST_FOLDER'),
    (MONITORFORMAT, 'MONITORFORMAT'),
    (TOKEN_EXPIRED_AFTER_SECONDS, 'TOKEN_EXPIRED_AFTER_SECONDS'),
    (OML_BRANCH, 'OML_BRANCH'),
    (OML_COMMIT, 'OML_COMMIT'),
    (OML_BUILD_DATE, 'OML_BUILD_DATE')
]

check_settings_variables(VARIABLES_LIST)

check_asterisk_connect_settings(ASTERISK)

check_audio_conversor_settings(TMPL_OML_AUDIO_CONVERSOR)

# Una vez que tengo ASTERISK_AUDIO_PATH y OML_AUDIO_FOLDER puedo calcular OML_AUDIO_PATH_ASTERISK
OML_AUDIO_PATH_ASTERISK = ASTERISK_AUDIO_PATH + OML_AUDIO_FOLDER
# Lo mismo con OML_PLAYLIST_PATH_ASTERISK
OML_PLAYLIST_PATH_ASTERISK = ASTERISK_AUDIO_PATH + OML_PLAYLIST_FOLDER

# DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = True

MIDDLEWARE = MIDDLEWARE_CLASSES
