{% if is_docker == "false" %}
AMI_USER={{ ami_user }}
AMI_PASSWORD={{ ami_password }}
ASTERISK_IP={{ omni_ip }}
ASTERISK_HOSTNAME=localhost
ASTERISK_LOCATION={{ asterisk_location }}
CALIFICACION_REAGENDA={{ schedule }}
DJANGO_PASS={{ admin_pass }}
DJANGO_SETTINGS_MODULE=ominicontacto.settings.production
EPHEMERAL_USER_TTL={{ ECCTL }}
{% if external_port is defined %}
EXTERNAL_PORT={{ external_port }}
{% else %}
EXTERNAL_PORT=443
{% endif %}
INSTALL_PREFIX={{ install_prefix}}
KAMAILIO_IP={{ omni_ip }}
KAMAILIO_HOSTNAME={{ omni_fqdn }}
KAMAILIO_LOCATION={{ kamailio_location }}
MONITORFORMAT={{ MONITORFORMAT }}
{% if mysql_host is defined %}
MYSQL_HOST={{ mysql_host }}
{% endif %}
MYSQL_PWD={{ mysql_root_password }}
{% if external_hostname is defined %}
NGINX_HOSTNAME={{ external_hostname }}
{% else %}
NGINX_HOSTNAME={{ omni_fqdn }}
{% endif %}
LOGIN_FAILURE_LIMIT={{ LOGIN_FAILURE_LIMIT }}
OMNILEADS_HOSTNAME=localhost
{% if postgres_host is defined %}
PGHOST={{ postgres_host }}
{% else %}
PGHOST=localhost
{% endif %}
PGDATABASE={{ postgres_database }}
PGUSER={{ postgres_user }}
PGPASSWORD={{ postgres_password }}
PYTHONPATH=$INSTALL_PREFIX
REDIS_HOSTNAME=localhost
SESSION_COOKIE_AGE={{ SCA }}
TZ={{ TZ }}
{% if dialer_host is defined %}
WOMBAT_HOSTNAME={{ dialer_host }}
{% else %}
WOMBAT_HOSTNAME=localhost
{% endif %}
WOMBAT_USER={{ dialer_user }}
WOMBAT_PASSWORD={{ dialer_password }}

export AMI_USER AMI_PASSWORD ASTERISK_IP ASTERISK_HOSTNAME ASTERISK_LOCATION CALIFICACION_REAGENDA DJANGO_SETTINGS_MODULE DJANGO_PASS EPHEMERAL_USER_TTL EXTERNAL_PORT INSTALL_PREFIX KAMAILIO_IP KAMAILIO_HOSTNAME KAMAILIO_LOCATION LOGIN_FAILURE_LIMIT MONITORFORMAT MYSQL_PWD NGINX_HOSTNAME OMNILEADS_HOSTNAME PGHOST PGDATABASE PGUSER PGPASSWORD PYTHONPATH REDIS_HOSTNAME SESSION_COOKIE_AGE TZ WOMBAT_HOSTNAME WOMBAT_USER WOMBAT_PASSWORD {% if mysql_host is defined %}MYSQL_HOST{% endif %}
{% else %}
DJANGO_PASS={{ admin_pass }}
MYSQL_PWD={{ mysql_root_password }}
PGPASSWORD={{ postgres_password }}
TZ={{ TZ }}
DOCKER_USER={{ registry_username }}

export DJANGO_PASS MYSQL_PWD PGPASSWORD TZ DOCKER_USER
{% endif %}
