#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

OMNIAPP_USER=${OMNIAPP_USER:-"omnileads"}
OMNIAPP_GROUP=${OMNIAPP_GROUP:-${OMNIAPP_USER}}

set -e

echo "Run django command migrate"
$COMMAND migrate --noinput
echo "Run actualizar_permisos"
$COMMAND actualizar_permisos