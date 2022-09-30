CALLREC_DEVICE={{ callrec_device }}
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
PGHOSTHA={{ postgres_ha }}
PGHOSTRO={{ postgres_ro_host }}
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
#S3 Bucket CALLREC envars
{% if s3_bucket_name is defined %}
S3_STORAGE_ENABLED=true
S3_BUCKET_NAME={{ s3_bucket_name }}
AWS_ACCESS_KEY_ID={{ s3_access_key }}
AWS_SECRET_ACCESS_KEY={{ s3_secret_key }}
S3_REGION_NAME={{ s3_region }}
{% if callrec_device != "s3-aws" %}
S3_ENDPOINT={{ s3url }}
AWS_DEFAULT_REGION=us-east-1
{% endif %}
{% endif %}
# Google maps API
{% if google_maps_api_key is defined %}
GOOGLE_MAPS_API_KEY={{ google_maps_api_key }}
GOOGLE_MAPS_CENTER='{{ google_maps_center }}'
{% endif %}
# OML version envars
OML_BRANCH={{ oml_release }}
OML_COMMIT={{ commit }}
OML_BUILD_DATE="{{ build_date }}"
# SMTP envars

{% if email_backend is defined %}
EMAIL_BACKEND={{ email_backend }}
{% else %}
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend
{% endif %}

{% if email_backend is defined and email_backend == "django.core.mail.backends.smtp.EmailBackend" %}
DEFAULT_FROM_EMAIL={{ email_default_from }}
EMAIL_HOST={{ email_host }}
EMAIL_HOST_PASSWORD={{ email_password }}
EMAIL_HOST_USER={{ email_user }}
EMAIL_PORT={{ email_port }}
{% endif %}
{% if email_ssl_certfile is defined %}
EMAIL_SSL_CERTFILE={{ email_ssl_certfile }}
{% endif %}
{% if email_ssl_keyfile is defined %}
EMAIL_SSL_KEYFILE={{ email_ssl_keyfile }}
{% endif %}
{% if email_use_ssl is defined %}
EMAIL_USE_SSL={{ email_use_ssl }}
{% endif %}
{% if email_use_tls is defined %}
EMAIL_USE_TLS={{ email_use_tls }}
{% endif %}
export CALLREC_DEVICE AMI_USER AMI_PASSWORD ASTERISK_HOSTNAME ASTERISK_LOCATION CALIFICACION_REAGENDA DJANGO_SETTINGS_MODULE EPHEMERAL_USER_TTL {% if extern_ip != "none" and extern_ip != "auto" %} EXTERN_IP {% endif %} INSTALL_PREFIX KAMAILIO_HOSTNAME {% if kamailio_host == omni_fqdn %} KAMAILIO_CERTS_LOCATION SHM_SIZE PKG_SIZE {% endif %} LOGIN_FAILURE_LIMIT MONITORFORMAT OMNILEADS_HOSTNAME PGHOST PGDATABASE PGUSER PGPASSWORD PGPORT PGHOSTRO PGHOSTHA PYTHONPATH REDIS_HOSTNAME RTPENGINE_HOSTNAME SESSION_COOKIE_AGE TZ WOMBAT_HOSTNAME WOMBAT_USER WOMBAT_PASSWORD {% if mysql_host is defined %}MYSQL_HOST{% endif %} OML_BRANCH OML_COMMIT OML_BUILD_DATE WEBSOCKET_HOST WEBSOCKET_PORT {% if callrec_device != "local" %} S3_STORAGE_ENABLED S3_BUCKET_NAME AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY S3_REGION_NAME {% if callrec_device != "s3-aws" %} S3_ENDPOINT AWS_DEFAULT_REGION {% endif %} {% endif %} {% if google_maps_api_key is defined %} GOOGLE_MAPS_API_KEY GOOGLE_MAPS_CENTER {% endif %} EMAIL_BACKEND {% if email_backend is defined and email_backend == "django.core.mail.backends.smtp.EmailBackend" %} DEFAULT_FROM_EMAIL EMAIL_BACKEND EMAIL_HOST EMAIL_HOST_PASSWORD EMAIL_HOST_USER EMAIL_PORT {% endif %} {% if email_use_ssl is defined %} EMAIL_USE_SSL {% endif %} {% if email_use_tls is defined %} EMAIL_USE_TLS {% endif %} {% if email_ssl_keyfile is defined %} EMAIL_SSL_KEYFILE {% endif %} {% if email_ssl_keyfile is defined %} EMAIL_SSL_KEYFILE {% endif %}
