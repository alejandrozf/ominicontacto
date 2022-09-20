#!/bin/bash

INSTALL_PREFIX="/opt/omnileads"

if [ -f ${INSTALL_PREFIX}/bin/addons_installed.sh ];then
  source ${INSTALL_PREFIX}/bin/addons_installed.sh
else
  echo "There is no addon installed. Exiting."
  exit 0
fi

for Addon in "${ADDONS_INSTALLED[@]}";do
    cd ${INSTALL_PREFIX}/addons/${Addon}
    ./install.sh --accept-eula
done
