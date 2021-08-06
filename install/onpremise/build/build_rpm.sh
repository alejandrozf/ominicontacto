#!/bin/bash
OMNILEADS_VERSION=$(cat ../../../.omnileads_version)
VIRTUALENV_LOCATION="/opt/omnileads/virtualenv"
INSTALL_PREFIX="/opt/omnileads"
if test -z ${OMNILEADS_VERSION}; then
  echo "${PROGNAME}: OMNILEADS_VERSION required" >&2
  exit 1
fi

# Setting virtualenv
echo "Installing the virtualenv"
python3 -m venv $VIRTUALENV_LOCATION
source $VIRTUALENV_LOCATION/bin/activate
pip3 install setuptools --upgrade
echo "Installing the requirements packages"
pip3 install wheel
pip3 install -r ../../../requirements/requirements.txt --exists-action 'w'
echo "Creating additional folders"
mkdir -p $INSTALL_PREFIX/{wombat-json,backup,bin,media_root/reporte_campana,static,log,run,addons,ominicontacto}
echo "Copying code"
cp -a ../../../{api_app,configuracion_telefonia_app,manage.py,ominicontacto,ominicontacto_app,reciclado_app,reportes_app,requirements,supervision_app,test,tests,utiles_globales.py} $INSTALL_PREFIX/ominicontacto
echo "Copying scripts used by system"
cp -a scripts/bin/* ${INSTALL_PREFIX}/bin
cp -a scripts/oml_uwsgi.ini ${INSTALL_PREFIX}/run
echo "Copying cert of keys server"
cp -a cert ${INSTALL_PREFIX}
echo "Packing the rpm"
fpm -s dir -d cairo -d crontabs -d cronie -d cronie-anacron -d which -d vim \
    -d texinfo -d kernel-headers -d acl -d bind-utils -d sox -d lame -d unzip \
    -d wget -d python3-libs -t rpm -n virtualenv -v ${OMNILEADS_VERSION} \
  --rpm-user omnileads \
  --rpm-group omnileads \
  --before-install scripts/before_install.sh \
  --rpm-posttrans scripts/after_install.sh \
  --after-remove scripts/after_remove.sh \
  -f $INSTALL_PREFIX \
  omnileads.service=/etc/systemd/system/omnileads.service \
  scripts/cron/omnileads=/var/spool/cron/omnileads

mv virtualenv-* /root
cd /root/
echo "Uploading RPM to AWS repository"
aws s3 cp virtualenv* s3://${AWS_BUCKET}/virtualenv/virtualenv-${OMNILEADS_VERSION}.x86_64.rpm
