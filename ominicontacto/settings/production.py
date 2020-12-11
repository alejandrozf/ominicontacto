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
from .addons import *
from .defaults import *
from .checks import (check_settings_variables, process_middleware_settings,
                    check_asterisk_connect_settings, check_audio_conversor_settings)

COMPRESS_ENABLED = True
TEMPLATE_DEBUG = DEBUG
DJANGO_CORS_HEADERS = False
INTERNAL_IPS = ['127.0.0.1']

TOKEN_EXPIRED_AFTER_SECONDS = 9 * 60 * 60  # 9 horas

INSTALLED_APPS += ADDONS_APPS
LOCALE_PATHS += ADDONS_LOCALE_PATHS

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
    (DEFENDER_LOGIN_FAILURE_LIMIT, 'DEFENDER_LOGIN_FAILURE_LIMIT'),
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
    (OML_BACKLIST_REMOTEPATH, 'OML_BACKLIST_REMOTEPATH'),
    (SENDFILE_ROOT, 'SENDFILE_ROOT'),
    (SENDFILE_URL, 'SENDFILE_URL'),
    (SENDFILE_BACKEND, 'SENDFILE_BACKEND'),    
    (SIP_SECRET_KEY, 'SIP_SECRET_KEY'),
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

MIDDLEWARE = MIDDLEWARE_CLASSES
