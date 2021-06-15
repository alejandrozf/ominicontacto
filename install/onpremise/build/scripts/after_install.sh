#!/bin/bash
set -e
# Script that runs after omnileads install
INSTALL_PREFIX="/opt/omnileads"
STATIC_PATH="${INSTALL_PREFIX}/static"
MANAGE_SCRIPT="${INSTALL_PREFIX}/bin/manage.sh"
if [ -f /etc/profile.d/omnileads_envars.sh ]; then
  echo "Charging omnileads envars"
  source /etc/profile.d/omnileads_envars.sh
  echo "Erase the javascript cache files"
  rm -rf ${STATIC_PATH}/CACHE/js
  rm -rf ${STATIC_PATH}/CACHE/manifest.json
  echo "Execute reinstall_addons.sh script"
  ${INSTALL_PREFIX}/bin/reinstall_addons.sh
  echo " Execute django commands"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT migrate --noinput"
  echo "Create admin superuser"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT createsuperuser --noinput --username=admin --email=admin@example.com" || true
  echo "Set admin superuser default password"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT adicionar_perfil_supervisor_admin"
  #chown -R omnileads. /opt/omnileads/ /var/lib/nginx/tmp/
  sudo -u omnileads bash -c "$MANAGE_SCRIPT populate_history"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT compilemessages"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT collectstatic --noinput"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT collectstatic_js_reverse"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT compress --force"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT actualizar_permisos"
  echo "Running regenerar_asterisk command"
  runuser -l omnileads -c "$MANAGE_SCRIPT regenerar_asterisk"
  echo "Dump information of constance database"
  $MANAGE_SCRIPT constance list > ${INSTALL_PREFIX}/bin/constances_values.txt
  echo "Add queuelog trigger to database"
  psql -c "\i ${INSTALL_PREFIX}/ominicontacto/reportes_app/sql/plperl/replace_insert_queue_log_ominicontacto_queue_log.sql"
  echo "Restarting and enabling omnileads"
  systemctl enable omnileads
else
  echo "OMniLeads envars file not found, exiting"
  exit 1
fi
