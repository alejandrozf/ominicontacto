#!/bin/bash

OML_PATH="/opt/omnileads"

if [ -f $OML_PATH/bin/addons_installed.sh ]; then
  source $OML_PATH/bin/addons_installed.sh
else
  echo "There is no addon installed, exiting"
  echo 0
fi
for addon in "${ADDONS_INSTALLED[@]}"; do
    cd ${OML_PATH}/addons/${addon}
    ./install.sh
done
