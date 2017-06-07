# -*- coding: utf-8 -*-

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
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'NAME': 'kamailio',
        'USER': 'kamailio',
        'PASSWORD': 'kamailiorw',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT = os.path.join(BASE_DIR, '/home/freetech/media_root')

OML_OMNILEADS_IP = "172.16.20.241"

# Tiempo de session en segundo por ejemplo 10 minutos=600
SESSION_COOKIE_AGE = 600

#  para hacer un include de este archivo
# **** RECORDAR: revisar permisos y que existan los directorios ****
OML_QUEUE_FILENAME = "/home/freetech/extensions_fts_queues.conf"
OML_ASTERISK_HOSTNAME = "root@172.16.20.222"
OML_ASTERISK_REMOTEPATH = "/etc/asterisk/"
OML_SIP_FILENAME = "/home/freetech/sip_fts.conf"
OML_QUEUES_FILENAME = "/home/freetech/queues_fts.conf"
OML_BACKLIST_REMOTEPATH  = "/var/spool/asterisk/"
# parametros de conexion con base de datos mysql de asterisk
DATABASE_MYSQL_ASTERISK = {
    'BASE': 'asterisk',
    'HOST': '172.16.20.222',
    'USER': 'omnileads',
    'PASSWORD': 'admin123',
}

ASTERISK = {
    'USERNAME': "wombat",  # Usuario para AMI
    'PASSWORD': "fop222",  # Password para usuario para AMI
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


# 'OML_KAMAILIO_IP': ip donde se encuentra kamailio
# ejemplo "172.16.20.219/255.255.255.255"
OML_KAMAILIO_IP = "172.16.20.14/255.255.255.255"

# 'OML_WOMBAT_URL': url donde se encuentra el discador de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_URL = "http://172.16.20.222:8080/wombat"

# 'OML_WOMBAT_FILENAME': donde se alojara temporalmente los json de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_FILENAME = "/home/freetech/"

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
            'filename': '/home/freetech/ominicontacto/{0}'.format(_logging_output_file),
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
