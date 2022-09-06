#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

$COMMAND migrate --noinput
$COMMAND createsuperuser --noinput --username=admin --email=admin@example.com || true
$COMMAND populate_history
$COMMAND compilemessages
echo 'yes' | $COMMAND collectstatic
$COMMAND collectstatic_js_reverse
$COMMAND compress --force

psql -U $PGUSER -h $PGHOST -d $PGDATABASE -c "\i ${INSTALL_PREFIX}/ominicontacto/reportes_app/sql/plperl/replace_insert_queue_log_ominicontacto_queue_log.sql"
$COMMAND regenerar_asterisk
$COMMAND actualizar_permisos
$COMMAND adicionar_perfil_supervisor_admin

echo "Iniciando Django Server"
exec $COMMAND runserver 0.0.0.0:8099