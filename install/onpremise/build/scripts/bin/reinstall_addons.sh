#!/bin/bash

INSTALL_PREFIX="/opt/omnileads"

if [ -f ${INSTALL_PREFIX}/bin/addons_installed.sh ];then
  source ${INSTALL_PREFIX}/bin/addons_installed.sh
else
  echo "There is no addon installed. Exiting."
  exit 0
fi

for Addon in "${ADDONS_INSTALLED[@]}";do
    rm -rf ${INSTALL_PREFIX}/addons/${Addon}*
    cd ${INSTALL_PREFIX}/addons/
    wget https://fts-public-packages.s3-sa-east-1.amazonaws.com/${Addon}/${Addon}-latest.tar.gz
    tar -xvzf ${Addon}-latest.tar.gz
    rm -rf ${Addon}-latest.tar.gz
    cd ${Addon}
    ./install.sh --accept-eula
done