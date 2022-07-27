# -*- coding: utf-8 -*-

import os

AMI_USER = os.getenv('AMI_USER')
AMI_PASSWORD = os.getenv('AMI_PASSWORD')
ASTERISK_HOSTNAME = os.getenv('ASTERISK_HOSTNAME')
ASTERISK_LOCATION = os.getenv('ASTERISK_LOCATION')
DIALER_HOSTNAME = os.getenv('WOMBAT_HOSTNAME')
EPHEMERAL_USER_TTL = int(os.getenv('EPHEMERAL_USER_TTL'))
INSTALL_PREFIX = os.getenv('INSTALL_PREFIX')
KAMAILIO_HOSTNAME = os.getenv('KAMAILIO_HOSTNAME')
OML_OMNILEADS_HOSTNAME = os.getenv('OMNILEADS_HOSTNAME')
POSTGRES_HOST = os.getenv('PGHOST')
POSTGRES_DATABASE = os.getenv('PGDATABASE')
POSTGRES_USER = os.getenv('PGUSER')
POSTGRES_PORT = os.getenv('PGPORT')
REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE'))
TIME_ZONE = os.getenv('TZ')
# Settings para version de OML
OML_BRANCH = os.getenv('OML_BRANCH')
OML_COMMIT = os.getenv('OML_COMMIT')
OML_BUILD_DATE = os.getenv('OML_BUILD_DATE')

# Credenciales para wombat API
OML_WOMBAT_USER = os.getenv('WOMBAT_USER')
OML_WOMBAT_PASSWORD = os.getenv('WOMBAT_PASSWORD')
OML_WOMBAT_TIMEOUT = '600'

ALLOWED_HOSTS = [
    "*",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's1+*bfrvb@=k@c&9=pm!0sijjewneu5p5rojil#q+!a2y&as-4'
SIP_SECRET_KEY = 'SUp3rS3cr3tK3y'

DATABASE_REPLICA_ENABLED = os.getenv("PGHOSTHA") == "True"
DATABASE_REPLICA_HOST = os.getenv("PGHOSTRO")
if DATABASE_REPLICA_ENABLED and DATABASE_REPLICA_HOST is None:
    raise Exception("DATABASE_REPLICA_HOST is required when DATABASE_REPLICA_ENABLED is True")

# Datos de conexión de base db postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
        'NAME': POSTGRES_DATABASE,
        'USER': POSTGRES_USER,
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': DATABASE_REPLICA_HOST if DATABASE_REPLICA_ENABLED else POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
        'NAME': POSTGRES_DATABASE,
        'USER': POSTGRES_USER,
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOSTNAME, 6379)],
        },
    },
}

# Ubicaciones de staticos y media
STATIC_ROOT = "{0}/static".format(INSTALL_PREFIX)
MEDIA_ROOT = "{0}/media_root".format(INSTALL_PREFIX)


# URL externas
OML_WOMBAT_URL = "http://{0}:8080/wombat".format(DIALER_HOSTNAME)

# Ubicaciones de archivos
OML_SIP_FILENAME = "{0}/etc/asterisk/oml_pjsip_agents.conf".format(ASTERISK_LOCATION)
OML_QUEUES_FILENAME = "{0}/etc/asterisk/oml_queues.conf".format(ASTERISK_LOCATION)
OML_RUTAS_SALIENTES_FILENAME = "{0}/etc/asterisk/oml_extensions_outr.conf".format(ASTERISK_LOCATION)
OML_ASTERISK_REMOTEPATH = "{0}/etc/asterisk/".format(ASTERISK_LOCATION)
OML_WOMBAT_FILENAME = "{0}/wombat-json/".format(INSTALL_PREFIX)

OML_KAMAILIO_HOSTNAME = "root@{0}".format(KAMAILIO_HOSTNAME)

# Credenciales de AMI
ASTERISK = {
    'AMI_USERNAME': AMI_USER,  # Usuario para AMI
    'AMI_PASSWORD': AMI_PASSWORD,  # Password para usuario para AMI
}

# Seteo de logging
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
            'filename': '{0}/log/{1}'.format(INSTALL_PREFIX, _logging_output_file),
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

# Defender variables
DEFENDER_BEHIND_REVERSE_PROXY = True
DEFENDER_LOGIN_FAILURE_LIMIT = int(os.getenv('LOGIN_FAILURE_LIMIT'))
DEFENDER_DISABLE_IP_LOCKOUT = True
DURACION_ASIGNACION_CONTACTO_PREVIEW = 30
DEFENDER_REDIS_URL = "redis://{0}:6379/0".format(REDIS_HOSTNAME)

# Comando y paths de audios del sistema
TMPL_OML_AUDIO_CONVERSOR = ["sox", "-t", "wav", "<INPUT_FILE>",
                            "-r", "8k", "-c", "1", "-e", "signed-integer",
                            "-t", "wav", "<OUTPUT_FILE>"]
TMPL_OML_AUDIO_CONVERSOR_EXTENSION = ".wav"
ASTERISK_AUDIO_PATH = "{0}/var/lib/asterisk/sounds/".format(ASTERISK_LOCATION)
OML_AUDIO_FOLDER = "oml/"
OML_PLAYLIST_FOLDER = 'moh/'

# Formato de grabaciones
MONITORFORMAT = os.getenv('MONITORFORMAT')
# Calificacion de agenda
CALIFICACION_REAGENDA = os.getenv('CALIFICACION_REAGENDA')

CONSTANCE_REDIS_CONNECTION = {
    'host': REDIS_HOSTNAME,
    'port': 6379,
    'db': 0,
}

# configuraciones de django_sendfile para grabaciones
SENDFILE_ROOT = "{0}/var/spool/asterisk/monitor".format(ASTERISK_LOCATION)
SENDFILE_URL = '/grabaciones'
SENDFILE_BACKEND = 'django_sendfile.backends.nginx'

# email settings
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@{}".format(OML_OMNILEADS_HOSTNAME))
# EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend
#   Used for development, email gets printed to console. Other EMAIL_ settings are ignored.
# EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
#   Used for real send using SMTP, requires EMAIL_* settings.
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))
EMAIL_SSL_CERTFILE = os.getenv("EMAIL_SSL_CERTFILE", None)
EMAIL_SSL_KEYFILE = os.getenv("EMAIL_SSL_KEYFILE", None)
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", False) == "True"
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", False) == "True"
