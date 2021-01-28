AMI_USER={{ ami_user }}
AMI_PASSWORD={{ ami_password }}
ASTERISK_HOSTNAME={{ asterisk_host }}
ASTERISK_LOCATION={{ asterisk_location }}
CALIFICACION_REAGENDA={{ schedule }}
DJANGO_SETTINGS_MODULE=ominicontacto.settings.production
EPHEMERAL_USER_TTL={{ ECCTL }}
{% if extern_ip == "auto" %}
EXTERN_IP={{ public_ip }}
{% else %}
EXTERN_IP={{ extern_ip }}
{% endif %}
INSTALL_PREFIX={{ install_prefix }}
MONITORFORMAT={{ MONITORFORMAT }}
{% if mysql_host is defined %}
MYSQL_HOST={{ mysql_host }}
{% endif %}
LOGIN_FAILURE_LIMIT={{ LOGIN_FAILURE_LIMIT }}
OMNILEADS_HOSTNAME=localhost
PGHOST={{ postgres_host }}
PGDATABASE={{ postgres_database }}
PGPORT={{ postgres_port }}
PGUSER={{ postgres_user }}
PGPASSWORD={{ postgres_password }}
PYTHONPATH=$INSTALL_PREFIX
REDIS_HOSTNAME={{ redis_host }}
RTPENGINE_HOSTNAME={{ rtpengine_host }}
SESSION_COOKIE_AGE={{ SCA }}
KAMAILIO_HOSTNAME={{ kamailio_host }}
{% if kamailio_host == omni_fqdn %}
KAMAILIO_CERTS_LOCATION={{ certs_location }}
SHM_SIZE={{ shm_size }}
PKG_SIZE={{ pkg_size }}
{% endif %}
TZ={{ TZ }}
WEBSOCKET_HOST={{ websocket_host }}
WEBSOCKET_PORT={{ websocket_port }}
{% if dialer_host is defined %}
WOMBAT_HOSTNAME={{ dialer_host }}
{% else %}
WOMBAT_HOSTNAME=localhost
{% endif %}
WOMBAT_USER={{ dialer_user }}
WOMBAT_PASSWORD={{ dialer_password }}
# OML version envars
OML_BRANCH={{ oml_release }}
OML_COMMIT={{ commit }}
OML_BUILD_DATE="{{ build_date }}"

export AMI_USER AMI_PASSWORD ASTERISK_HOSTNAME ASTERISK_LOCATION CALIFICACION_REAGENDA DJANGO_SETTINGS_MODULE EPHEMERAL_USER_TTL {% if extern_ip != "none" and extern_ip != "auto" %} EXTERN_IP {% endif %} INSTALL_PREFIX KAMAILIO_HOSTNAME {% if kamailio_host == omni_fqdn %} KAMAILIO_CERTS_LOCATION SHM_SIZE PKG_SIZE {% endif %} LOGIN_FAILURE_LIMIT MONITORFORMAT OMNILEADS_HOSTNAME PGHOST PGDATABASE PGUSER PGPASSWORD PGPORT PYTHONPATH REDIS_HOSTNAME RTPENGINE_HOSTNAME SESSION_COOKIE_AGE TZ WOMBAT_HOSTNAME WOMBAT_USER WOMBAT_PASSWORD {% if mysql_host is defined %}MYSQL_HOST{% endif %} OML_BRANCH OML_COMMIT OML_BUILD_DATE WEBSOCKET_HOST WEBSOCKET_PORT
