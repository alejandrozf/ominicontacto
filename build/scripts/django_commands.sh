#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

OMNIAPP_USER=${OMNIAPP_USER:-"omnileads"}
OMNIAPP_GROUP=${OMNIAPP_GROUP:-${OMNIAPP_USER}}

set -e

echo "Run ********** django commands"
echo "Run django command migrate"
$COMMAND migrate --noinput
$COMMAND createsuperuser --noinput --username=admin --email=admin@example.com || true
echo "Run django command populate_history"
$COMMAND populate_history
echo "Run django command populate_history"
$COMMAND compilemessages
echo "Run django command colllect_static"
echo 'yes' | $COMMAND collectstatic
$COMMAND collectstatic_js_reverse
echo "Run django command compress"
$COMMAND compress --force
echo "Run plperl"
psql -U $PGUSER -h $PGHOST -d $PGDATABASE -c "\i ${INSTALL_PREFIX}/ominicontacto/reportes_app/sql/plperl/replace_insert_queue_log_ominicontacto_queue_log.sql"
echo "Run actualizar_permisos"
$COMMAND actualizar_permisos
echo "Run adicionar_perfil_supervisor_admin"
$COMMAND adicionar_perfil_supervisor_admin

