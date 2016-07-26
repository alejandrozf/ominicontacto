En el servidor 172.16.20.241

El proyecto se encuentra: /home/freetech/ominicontacto

Ejecucion del sistema desde uWSGI
---------------------------------

Existe un script que lanza la aplicación usando uWSGI.

Para utilizar el sistema con uWSGI:

freetech@fts-omni:~$ cd /home/freetech/ominicontacto

$ ./run_uwsgi.sh

### Armado inicial del entorno ###

Editar oml_settings_local.py para que contenga:


```
#!python
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

STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

# 'OML_QUEUE_FILENAME': donde se genera la config de queues. Asterisk debe estar configurado
#  para hacer un include de este archivo
# en el servidor del elastix debe estar en /etc/asterisk/extensions_fts_queues.conf
# **** RECORDAR: revisar permisos y que existan los directorios ****
OML_QUEUE_FILENAME = "/etc/asterisk/extensions_fts_queues.conf"

```

### Configuracion ssl para desarrollo ###
Generar certificado usando el siguiente el comando
```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
```