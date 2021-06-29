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

Init() {
  if [[ $DJANGO_SETTINGS_MODULE == *"develop"* ]]; then
    echo "Iniciando Django Server"
    exec $COMMAND runserver 0.0.0.0:8099
  else
    echo "Iniciando Django uWSGI"
    exec /usr/local/bin/uwsgi --ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini
  fi
}


if [ "$1" = "" ]; then
  if [ ! -f /etc/localtime ]; then
    ln -s /usr/share/zoneinfo/$TZ /etc/localtime
  fi
  if ! crontab -l | grep -q 'conversor.sh'; then
  touch /var/spool/cron/crontabs/omnileads
  cat > /var/spool/cron/crontabs/omnileads << EOF
SHELL=/bin/bash
0 1 * * * ${INSTALL_PREFIX}bin/conversor.sh 1 0  >> ${INSTALL_PREFIX}log/conversor.log
EOF
  fi
  printenv > /etc/profile.d/omnileads_envars.sh

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
  /usr/sbin/crond -l 0 -L /opt/omnileads/log/crond.log
  chown -R $OMNIAPP_USER. ${INSTALL_PREFIX} /var/spool/cron/crontabs/omnileads
  Init
else
  $COMMAND migrate --noinput
  $COMMAND compilemessages
  echo 'yes' | $COMMAND collectstatic
  $COMMAND collectstatic_js_reverse
  $COMMAND compress --force
  $COMMAND regenerar_asterisk
  Init
fi
