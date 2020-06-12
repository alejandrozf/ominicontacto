#!/bin/bash
PROGNAME=$(basename $0)
PATH=$PATH:/usr/local/bin
BRANCH={{ virtualenv_version }}
VIRTUALENV_VERSION_INSTALLED=$(cat {{ install_prefix}}/virtualenv_version)
VIRTUALENV_VERSION={{ virtualenv_version }}
SSH_OPTIONS="-o stricthostkeychecking=no -o ConnectTimeout=10"

if test -z ${VIRTUALENV_VERSION}; then
  echo "${PROGNAME}: VIRTUALENV_VERSION required" >&2
  exit 1
fi

set -ex

if [ "$VIRTUALENV_VERSION_INSTALLED" != "$VIRTUALENV_VERSION" ]; then
  yum install -y \
    python3 \
    python3-devel \
    python3-pip.noarch \
    cairo \
    cairo-devel \
    libxslt-devel \
    libxslt-python \
    libxslt \
    libjpeg-turbo-devel \
    libffi-devel \
    libffi \
    libpqxx \
    libpqxx-devel \
    libsass-devel \
    libsass \
    pycairo \
    pycairo-devel \
    python2-psycogreen.noarch \
    python-lxml \
    python-psycopg2.x86_64 \
    python-virtualenv \
    git

  # Setting virtualenv
  virtualenv {{ virtualenv_location }} -p python3.6
  source {{ virtualenv_location }}/bin/activate
  pip3 install setuptools --upgrade
  cd {{ virtualenv_location }}
  pip3 install -r /vagrant/requirements/requirements.txt --exists-action 'w'
  echo "{{ virtualenv_version }}" > {{ install_prefix }}virtualenv_version
fi
echo "Building virtualenv rpm"
cd /vagrant/build/rpms
if [[ $BRANCH == *"release"* ]]; then
  BRANCH=$(echo $BRANCH|awk -F '-' '{print $2}')
elif [[ $BRANCH == *"oml-"* ]]; then
  BRANCH=$(echo $BRANCH|awk -F '-' '{print $1 $2}')
fi
fpm -s dir -t rpm -n virtualenv -v $BRANCH {{ virtualenv_location}} /etc/systemd/system/omnileads.service || true
echo "Uploading rpm to public server"
scp $SSH_OPTIONS -P 40404 -i /vagrant/vps_key.pem virtualenv-$BRANCH* root@www.freetech.com.ar:/var/www/html/omnileads/build
