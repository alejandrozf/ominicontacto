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

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG


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

STATIC_ROOT = "/opt/omnileads/static"
MEDIA_ROOT = "/opt/omnileads/media_root"

OML_OMNILEADS_IP = "172.16.20.241"

# Tiempo de session en segundo por ejemplo 10 minutos=600
SESSION_COOKIE_AGE = 600

#  para hacer un include de este archivo
# **** RECORDAR: revisar permisos y que existan los directorios ****
OML_ASTERISK_HOSTNAME = "root@172.16.20.222"
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
    'HTTP_AMI_URL': "http://172.16.20.88:7088",
}

# 'OML_RELOAD_CMD': comando a ejecutar para realizar el reload de la configuracion de Asterisk
# **** RECORDAR: revisar permisos, usuario, etc.
OML_RELOAD_CMD = '["ssh root@172.16.20.222",  "/usr/sbin/asterisk", "-rx", "reload"]'

# 'OML_GRABACIONES_URL': url donde se encuentra las grabaciones en elastix
# ejemplo "http://172.16.20.222/grabaciones"

OML_GRABACIONES_URL = "http://172.16.20.222/grabaciones"

# 'OML_SUPERVISION_URL': url donde se encuentra las grabaciones en elastix
# ejemplo "http://172.16.20.222:8090/Omnisup/index.php"

OML_SUPERVISION_URL = "http://172.16.20.88:8090/Omnisup/index.php?page=Lista_Campanas&supervId="


# 'OML_KAMAILIO_IP': ip donde se encuentra kamailio-debian
# ejemplo "16.20.219/255.255.255.255"
OML_KAMAILIO_IP = "172.16.20.14/255.255.255.255"

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

CALIFICACION_REAGENDA = 'Agendado'

LOCAL_APPS = []

DJANGO_DEBUG_TOOLBAR = False

OML_QUEUE_FILENAME = ""

OML_RUTAS_SALIENTES_FILENAME = "/opt/omnileads/asterisk/etc/asterisk/oml_extensions_outr.conf"

ASTERISK_AUDIO_PATH = "/var/lib/asterisk/sounds/"

OML_AUDIO_FOLDER = "oml/"

DJANGO_CORS_HEADERS = False

DURACION_ASIGNACION_CONTACTO_PREVIEW = 30

CONSTANCE_CONFIG = {}
MIDDLEWARE_PREPPEND = []
MIDDLEWARE_APPEND = []
TEMPLATES_CONTEXT_PROCESORS_APPEND = []
