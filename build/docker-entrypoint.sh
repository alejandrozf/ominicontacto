#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"
INTERFACE=$(ip route show | awk '/^default/ {print $5}');
# run as user OMNIAPP by default
OMNIAPP_USER=${OMNIAPP_USER:-"omnileads"}
OMNIAPP_GROUP=${OMNIAPP_GROUP:-${OMNIAPP_USER}}

set -e
#until psql -h $PGHOST -U $PGUSER -c '\q'; do
#  >&2 echo "Postgres is unavailable - sleeping"
#  sleep 1
#done
#>&2 echo "Postgres is up - executing command"
#sleep 5

Init_UWSGI() {
  if [[ $CRON_ENABLE == "false" ]]; then
    echo "crontab disabled"
    cat /dev/null > /var/spool/cron/crontabs/root
  else
    echo "write crontab omnileads"
    chown omnileads.omnileads /opt/omnileads/bin/callrec_converter.sh
    touch /var/spool/cron/crontabs/omnileads
    cat > /var/spool/cron/crontabs/omnileads << EOF
SHELL=/bin/bash
* * * * * flock -n /opt/omnileads/actualizar_campanas_preview.lock /usr/local/bin/python3 /opt/omnileads/ominicontacto/manage.py actualizar_campanas_preview
0 1 * * * flock -n /opt/omnileads/callrec_converter.lock /opt/omnileads/bin/callrec_converter.sh
EOF
    exec crond &
  fi

  if [[ $DJANGO_SETTINGS_MODULE == *"develop"* ]]; then
    echo "Iniciando Django Server"
    exec $COMMAND runserver 0.0.0.0:8099
  else
    echo "Iniciando uWSGI"
    
    if [[ $LOGS_FILE == "True" ]]; then
    echo "Logs to file"
    exec /usr/local/bin/uwsgi --ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini --logger file:/opt/omnileads/log/django.log --http-socket ${DJANGO_HOSTNAME}:${UWSGI_PORT}
    else
    exec /usr/local/bin/uwsgi --ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini --http-socket ${DJANGO_HOSTNAME}:${UWSGI_PORT}
    fi
  fi
}

Init_ASGI() {
    cat /dev/null > /var/spool/cron/crontabs/root
    echo "Iniciando Daphne ASGI"
    exec /usr/local/bin/daphne -p ${DAPHNE_PORT} -b ${DJANGO_HOSTNAME} --proxy-headers --verbosity=3 ominicontacto.asgi:application
}

DB_Restore(){
if [ -z ${SSL_SELFSIGNED} ]; then  
  if [ -z ${S3_ENDPOINT_AWS} ]; then
    aws --endpoint ${S3_ENDPOINT} s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  else 
    aws s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  fi  
else
  aws --endpoint ${S3_ENDPOINT} --no-verify-ssl s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/    
fi
pg_restore -d ${PGDATABASE} /tmp/${BACKUP_FILENAME}
}

DB_Backup(){
pg_dump -h ${PGHOST} -p ${PGPORT} -U ${PGUSER} -Fc -b -v -f /tmp/${BACKUP_FILENAME} -d ${PGDATABASE}
if [ -z ${SSL_SELFSIGNED} ]; then
  if [ -z ${S3_ENDPOINT_AWS} ]; then
    aws --endpoint ${S3_ENDPOINT} s3 mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/
  else
    aws s3 mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/
  fi  
else    
  aws --endpoint ${S3_ENDPOINT} s3 --no-verify-ssl mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/
fi
}

if [ "$1" = "" ]; then
  if [ ! -f /etc/localtime ]; then
    ln -s /usr/share/zoneinfo/$TZ /etc/localtime
  fi

  if [[ $DJANGO_HOSTNAME == "app" ]]; then
      DJANGO_HOSTNAME=0.0.0.0
  fi

  if [[ $DAPHNE_ENABLE == "True" ]]; then
    Init_ASGI
    exit 0
  fi

  if [[ $POSTGRES_RESTORE == "True" ]]; then
    DB_Restore
    exit 0
  fi

  if [[ $POSTGRES_BACKUP == "True" ]]; then
    DB_Backup
    exit 0
  fi

  #printenv > /etc/default/omnileads_django.env
  printenv > /etc/profile.d/omnileads_envars.sh

  if [[ $CRON_ENABLE == "false" ]]; then
    $COMMAND migrate --noinput
    $COMMAND createsuperuser --noinput --username=admin --email=admin@example.com || true
    $COMMAND populate_history
    $COMMAND compilemessages
    echo 'yes' | $COMMAND collectstatic
    $COMMAND collectstatic_js_reverse
    $COMMAND compress --force
    #$COMMAND actualizar_configuracion

    psql -U $PGUSER -h $PGHOST -d $PGDATABASE -c "\i ${INSTALL_PREFIX}/ominicontacto/reportes_app/sql/plperl/replace_insert_queue_log_ominicontacto_queue_log.sql"
    $COMMAND regenerar_asterisk
    $COMMAND actualizar_permisos
    $COMMAND adicionar_perfil_supervisor_admin
    chown -R $OMNIAPP_USER. ${INSTALL_PREFIX}
  else
    $COMMAND regenerar_asterisk
    chown -R $OMNIAPP_USER. ${INSTALL_PREFIX}
    echo "direct to Init_UWSGI"
  fi
    Init_UWSGI

else
  $COMMAND migrate --noinput
  $COMMAND compilemessages
  echo 'yes' | $COMMAND collectstatic
  $COMMAND collectstatic_js_reverse
  $COMMAND compress --force
  $COMMAND regenerar_asterisk
  Init_UWSGI
fi
