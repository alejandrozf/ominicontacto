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
echo "Run adicionar_perfil_supervisor_admin"
$COMMAND adicionar_perfil_supervisor_admin
