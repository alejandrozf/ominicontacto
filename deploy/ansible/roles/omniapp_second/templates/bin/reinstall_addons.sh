#!/bin/bash

OML_PATH="/opt/omnileads"

source $OML_PATH/bin/addons_installed.sh

for addon in "${ADDONS_INSTALLED[@]}"; do
    cd /var/tmp/$addon_releases
    MANUAL=0 ./install.sh --last-release
done