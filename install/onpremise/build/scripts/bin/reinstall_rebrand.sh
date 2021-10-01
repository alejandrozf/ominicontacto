#!/bin/bash

RepositoryLocation=$1
InstallationPrefix="/opt/omnileads"
ManageScript="${InstallationPrefix}/bin/manage.sh"

# Placing specific rebrand files
unalias cp
cp -rf ${RepositoryLocation}/ominicontacto_app/ ${InstallationPrefix}/ominicontacto/
cp -rf ${RepositoryLocation}/supervision_app/ ${InstallationPrefix}/ominicontacto/
cp -rf ${RepositoryLocation}/configuracion_telefonia_app/ ${InstallationPrefix}/ominicontacto/

# Removing specific logos
rm -rf ${InstallationPrefix}/ominicontacto/ominicontacto_app/static/ominicontacto/Img/ic_logo_full.png

# Applying changes
sudo -u omnileads bash -c "${ManageScript} compilemessages"
sudo -u omnileads bash -c "${ManageScript} collectstatic --noinput"
sudo -u omnileads bash -c "${ManageScript} collectstatic_js_reverse"
sudo -u omnileads bash -c "${ManageScript} compress --force"
sudo -u omnileads bash -c "${ManageScript} actualizar_permisos"

# Replacing certificates
if [ -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/cert.pem ] && [ -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/key.pem ];then
  cp -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/cert.pem ${InstallationPrefix}/nginx_certs/cert.pem
  cp -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/key.pem ${InstallationPrefix}/nginx_certs/key.pem
  cp -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/cert.pem ${InstallationPrefix}/kamailio/etc/certs/cert.pem
  cp -f ${RepositoryLocation}/install/onpremise/deploy/ansible/certs/key.pem ${InstallationPrefix}/kamailio/etc/certs/key.pem
  systemctl restart nginx
  systemctl restart kamailio
fi
