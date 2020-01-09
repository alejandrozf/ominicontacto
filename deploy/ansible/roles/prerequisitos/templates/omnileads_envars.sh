AMI_USER={{ ami_user }}
AMI_PASSWORD={{ ami_password }}
ASTERISK_IP={{ asterisk_ip }}
ASTERISK_HOSTNAME={{ asterisk_fqdn }}
ASTERISK_LOCATION={{ asterisk_location }}
CALIFICACION_REAGENDA={{ schedule }}
DJANGO_PASS={{ admin_pass }}
{% if devenv == 0 %}
DJANGO_SETTINGS_MODULE=ominicontacto.settings.production
{% else %}
DJANGO_SETTINGS_MODULE=ominicontacto.settings.develop
{% endif %}
EPHEMERAL_USER_TTL={{ ECCTL }}
{% if external_port is defined %}
EXTERNAL_PORT={{ external_port }}
{% else %}
EXTERNAL_PORT=443
{% endif %}
INSTALL_PREFIX={{ install_prefix}}
KAMAILIO_IP={{ kamailio_ip }}
KAMAILIO_HOSTNAME={{ kamailio_fqdn }}
KAMAILIO_LOCATION={{ kamailio_location }}
MONITORFORMAT={{ MONITORFORMAT }}
MYSQL_PWD={{ mysql_root_password }}
{% if external_hostname is defined %}
NGINX_HOSTNAME={{ external_hostname }}
{% else %}
NGINX_HOSTNAME={{ omniapp_fqdn }}
{% endif %}
LOGIN_FAILURE_LIMIT={{ LOGIN_FAILURE_LIMIT }}
OMNILEADS_IP={{ omniapp_ip }}
OMNILEADS_HOSTNAME={{ omniapp_fqdn }}
PGHOST={{ database_fqdn }}
PGDATABASE={{ postgres_database }}
PGUSER={{ postgres_user }}
PGPASSWORD={{ postgres_password }}
PYTHONPATH=$INSTALL_PREFIX
REDIS_HOSTNAME=localhost
SESSION_COOKIE_AGE={{ SCA }}
TZ={{ TZ }}
WOMBAT_HOSTNAME={{ dialer_fqdn }}
WOMBAT_USER={{ dialer_user }}
WOMBAT_PASSWORD={{ dialer_password }}

export AMI_USER AMI_PASSWORD ASTERISK_IP ASTERISK_HOSTNAME ASTERISK_LOCATION CALIFICACION_REAGENDA DJANGO_SETTINGS_MODULE DJANGO_PASS EPHEMERAL_USER_TTL EXTERNAL_PORT INSTALL_PREFIX KAMAILIO_IP KAMAILIO_HOSTNAME KAMAILIO_LOCATION LOGIN_FAILURE_LIMIT MONITORFORMAT MYSQL_PWD NGINX_HOSTNAME OMNILEADS_IP OMNILEADS_HOSTNAME PGHOST PGDATABASE PGUSER PGPASSWORD PYTHONPATH REDIS_HOSTNAME SESSION_COOKIE_AGE TZ WOMBAT_HOSTNAME WOMBAT_USER WOMBAT_PASSWORD
