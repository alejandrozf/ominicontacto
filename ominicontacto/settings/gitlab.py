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

"""
Defaults para ambientes de desarrollo.

Para utilizar estos settings, crear ``fts_web_settings_local``
(en paquete ROOT de Python) con:

    from fts_web_settings_local_dev import *  # @UnusedWildImport
    SECRET_KEY = 'xxx' # Algun valor random

    if 'USE_PG' in os.environ:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'xxxxxxx',
                'USER': 'xxxxxxx',
                'PASSWORD': 'xxxxxxx',
                'CONN_MAX_AGE': 300,
                'ATOMIC_REQUESTS': True,
            }
        }

Y luego de eso, las customizaciones.

"""
import os

from .addons import *
from .defaults import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = False

ALLOWED_HOSTS = [
    "*",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's1+*bfrvb@=k@c&9=pm!0sijjewneu5p5rojil#q+!a2y&as-4'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'plpython',
        'PORT': 5432,
        'NAME': 'omnileads',
        'USER': 'omnileads',
        'PASSWORD': 'omnileadsrw',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    }
}

DEFENDER_BEHIND_REVERSE_PROXY = True
STATIC_ROOT = "/opt/omnileads/static"
MEDIA_ROOT = "/opt/omnileads/media_root"

# Tiempo de session en segundo por ejemplo 10 minutos=600
SESSION_COOKIE_AGE = 600

#  para hacer un include de este archivo
# **** RECORDAR: revisar permisos y que existan los directorios ****
ASTERISK_HOSTNAME = "172.16.20.222"
OML_ASTERISK_REMOTEPATH = "/etc/asterisk/"
OML_SIP_FILENAME = "/opt/omnileads/sip_fts.conf"
OML_QUEUES_FILENAME = "/opt/omnileads/queues_fts.conf"
OML_BACKLIST_REMOTEPATH = "/var/spool/asterisk/"
# parametros de conexion con base de datos mysql de asterisk
DATABASE_MYSQL_ASTERISK = {
    'BASE': 'asterisk',
    'HOST': '172.16.20.222',
    'USER': 'omnileads',
    'PASSWORD': 'admin123',
}

ASTERISK = {
    'AMI_USERNAME': "wombat",  # Usuario para AMI
    'AMI_PASSWORD': "fop222",  # Password para usuario para AMI
}

# 'OML_WOMBAT_URL': url donde se encuentra el discador de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_URL = "http://172.16.20.222:8080/wombat"

# 'OML_WOMBAT_FILENAME': donde se alojara temporalmente los json de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_FILENAME = "/opt/omnileads/"

# 'OML_WOMBAT_USER': user para conectarse con la api de WOMBAT DIALER
# "user_test"

OML_WOMBAT_USER = "demoadmin"

# 'OML_WOMBAT_PASSWORD': password para ingresar con la api de WOMBAT DIALER
# "user123"

OML_WOMBAT_PASSWORD = "demo"

OML_WOMBAT_TIMEOUT = '600'

EPHEMERAL_USER_TTL = 28800
OML_KAMAILIO_HOSTNAME = "root@{{ kamailio_fqdn }}"
OML_KAMAILIO_CMD = "kamcmd -s {{ kamailio_location }}/run/kamailio/kamailio_ct autheph.dump_secrets"

_logging_output_file = os.environ.get("OML_LOGFILE", "django.log")
assert os.path.split(_logging_output_file)[0] == "",\
    "La variable de entorno OML_LOGFILE solo debe contener " +\
    "el nombre del archivo, SIN directorios."
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)-15s [%(levelname)7s] '
                       '%(name)20s - %(message)s')
        },
    },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/opt/omnileads/ominicontacto/{0}'.format(_logging_output_file),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
    'django.security.DisallowedHost': {
        'handlers': ['mail_admins'],
        'level': 'CRITICAL',
        'propagate': False,
    },
}

# Ubuntu (wav -> wav)
TMPL_OML_AUDIO_CONVERSOR = ["sox", "-t", "wav", "<INPUT_FILE>",
                            "-r", "8k", "-c", "1", "-e", "signed-integer",
                            "-t", "wav", "<OUTPUT_FILE>"]

TMPL_OML_AUDIO_CONVERSOR_EXTENSION = ".wav"

MONITORFORMAT = 'mp3'

OML_AUDIO_PATH_ASTERISK = "/var/lib/asterisk/sounds/oml/"

OML_PLAYLIST_PATH_ASTERISK = "var/lib/asterisk/sounds/moh/"

CALIFICACION_REAGENDA = 'Agenda'

LOCAL_APPS = []

OML_QUEUE_FILENAME = ""
OML_BRANCH=""
OML_COMMIT=""
OML_BUILD_DATE=""

OML_RUTAS_SALIENTES_FILENAME = "/opt/omnileads/asterisk/etc/asterisk/oml_extensions_outr.conf"

ASTERISK_AUDIO_PATH = "/var/lib/asterisk/sounds/"

OML_AUDIO_FOLDER = "oml/"
OML_PLAYLIST_FOLDER = "moh/"

DURACION_ASIGNACION_CONTACTO_PREVIEW = 30

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

MIDDLEWARE_PREPPEND = []
MIDDLEWARE_APPEND = []
TEMPLATES_CONTEXT_PROCESORS_APPEND = []

CONSTANCE_REDIS_CONNECTION = {
    'host': 'redis',
    'port': 6379,
    'db': 0,
}

REDIS_HOSTNAME = 'redis'


TOKEN_EXPIRED_AFTER_SECONDS = 600

KAMAILIO_HOSTNAME = 'trash'
NGINX_HOSTNAME = 'trash'
OML_EXTERNAL_PORT = 'trash'

MIDDLEWARE = MIDDLEWARE_CLASSES

INSTALL_PREFIX = '/opt/omnileads/'
# configuraciones de django_sendfile para grabaciones
SENDFILE_ROOT = "/var/spool/asterisk/monitor"
SENDFILE_URL = '/grabaciones'
SENDFILE_BACKEND = 'django_sendfile.backends.nginx'
