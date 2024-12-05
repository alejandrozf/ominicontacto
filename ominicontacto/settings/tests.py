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

INSTALLED_APPS += ADDONS_APPS

ALLOWED_HOSTS = [
    "*",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's1+*bfrvb@=k@c&9=pm!0sijjewneu5p5rojil#q+!a2y&as-4'

POSTGRES_HOST = os.getenv('PGHOST')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': POSTGRES_HOST,
        'PORT': 5432,
        'NAME': 'omnileads',
        'USER': 'omnileads',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': POSTGRES_HOST,
        'PORT': 5432,
        'NAME': 'omnileads',
        'USER': 'omnileads',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
        'SUPPORTS_TRANSACTIONS': True,
        'TEST': {
            'MIRROR': 'default',
        },
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

OML_OMNILEADS_HOSTNAME = os.getenv('OMNILEADS_HOSTNAME')

OML_DIALER_ENGINE = 'wombat'
# 'OML_WOMBAT_URL': url donde se encuentra el discador de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_URL = "trash"

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

OML_PLAYLIST_PATH_ASTERISK = "/var/lib/asterisk/sounds/oml/"

CALIFICACION_REAGENDA = 'Agenda'

LOCAL_APPS = []

OML_QUEUE_FILENAME = ""
OML_BRANCH = ""
OML_COMMIT = ""
OML_BUILD_DATE = ""

OML_RUTAS_SALIENTES_FILENAME = "/opt/omnileads/asterisk/etc/asterisk/oml_extensions_outr.conf"

ASTERISK_AUDIO_PATH = "/var/lib/asterisk/sounds/"

OML_AUDIO_FOLDER = "oml/"
OML_PLAYLIST_FOLDER = 'moh/'

DURACION_ASIGNACION_CONTACTO_PREVIEW = 30

CONSTANCE_CONFIG['KEYS_SERVER_HOST'] = ('https://keys-server.freetech.com.ar:20852',
                                        'KEYS_SERVER_HOST', str)

MIDDLEWARE_PREPPEND = []
MIDDLEWARE_APPEND = []
TEMPLATES_CONTEXT_PROCESORS_APPEND = []

TOKEN_EXPIRED_AFTER_SECONDS = 360

REDIS_HOSTNAME = 'trash'
CONSTANCE_REDIS_CONNECTION = {
    'host': REDIS_HOSTNAME,
    'port': 6379,
    'db': 0,
}

KAMAILIO_HOSTNAME = 'trash'
NGINX_HOSTNAME = 'trash'
OML_EXTERNAL_PORT = 'trash'

MIDDLEWARE = MIDDLEWARE_CLASSES


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()


INSTALL_PREFIX = os.getenv('INSTALL_PREFIX')
# configuraciones de django_sendfile para grabaciones
SENDFILE_ROOT = "/var/spool/asterisk/monitor"
SENDFILE_URL = '/grabaciones'
SENDFILE_BACKEND = 'django_sendfile.backends.nginx'
