#!/bin/bash

OML_PATH="/opt/omnileads"

source $OML_PATH/bin/addons_installed.sh

for addon in "${ADDONS_INSTALLED[@]}"; do
    cd {{ install_prefix }}/addons/${addon}
    ./install.sh
done
