#!/bin/bash
set -e
# Script that runs after OMniLeads install
INSTALL_PREFIX="/opt/omnileads"
STATIC_PATH="${INSTALL_PREFIX}/static"
MANAGE_SCRIPT="${INSTALL_PREFIX}/bin/manage.sh"
if [ -f /etc/profile.d/omnileads_envars.sh ];then
  echo "Deleting addons envars..."
  unset LIMIT_USERS_VERSION PREMIUM_REPORTS_VERSION SURVEY_VERSION WALLBOARD_VERSION WEBPHONE_CLIENT_VERSION
  echo "Loading OMniLeads envars..."
  source /etc/profile.d/omnileads_envars.sh
  echo "Erasing the javascript cache files..."
  rm -rf ${STATIC_PATH}/CACHE/js
  rm -rf ${STATIC_PATH}/CACHE/manifest.json
  echo "Executing django commands..."
  sudo -u omnileads bash -c "$MANAGE_SCRIPT migrate --noinput"
  echo "Creating admin superuser..."
  sudo -u omnileads bash -c "$MANAGE_SCRIPT createsuperuser --noinput --username=admin --email=admin@example.com" || true
  echo "Setting admin superuser default password..."
  sudo -u omnileads bash -c "$MANAGE_SCRIPT adicionar_perfil_supervisor_admin"
  chown -R omnileads. /opt/omnileads/ominicontacto/ /opt/omnileads/media_root/ /var/lib/nginx/tmp/
  sudo -u omnileads bash -c "$MANAGE_SCRIPT populate_history"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT compilemessages"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT collectstatic --noinput"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT collectstatic_js_reverse"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT compress --force"
  sudo -u omnileads bash -c "$MANAGE_SCRIPT actualizar_permisos"
  echo "Running regenerar_asterisk command..."
  runuser -l omnileads -c "$MANAGE_SCRIPT regenerar_asterisk"
  echo "Dumping information of constance database..."
  $MANAGE_SCRIPT constance list > ${INSTALL_PREFIX}/bin/constances_values.txt
  echo "Adding queuelog trigger to database..."
  psql -c "\i ${INSTALL_PREFIX}/ominicontacto/reportes_app/sql/plperl/replace_insert_queue_log_ominicontacto_queue_log.sql"
  echo "Executing reinstall_addons.sh script..."
  ${INSTALL_PREFIX}/bin/reinstall_addons.sh
  echo "Enabling OMniLeads service..."
  systemctl enable omnileads
else
  echo "OMniLeads envars file not found. Exiting."
  exit 1
fi
