#!/bin/bash

source /etc/profile.d/omnileads_envars.sh
cd ${INSTALL_PREFIX}/ominicontacto

${INSTALL_PREFIX}/virtualenv/bin/python \
    ${INSTALL_PREFIX}/ominicontacto/manage.py $*
