#!/bin/bash
PROGNAME=$(basename $0)
PATH=$PATH:/usr/local/bin

KAMAILIO_VERSION_INSTALLED=$({{ kamailio_location }}/sbin/kamailio -v |head -1 |awk -F " " '{print $3}')
KAMAILIO_VERSION={{ kamailio_version }}
SSH_OPTIONS="-o stricthostkeychecking=no -o ConnectTimeout=10"

if test -z ${KAMAILIO_VERSION}; then
  echo "${PROGNAME}: KAMAILIO_VERSION required" >&2
  exit 1
fi

set -ex

if [ "$KAMAILIO_VERSION_INSTALLED" != "$KAMAILIO_VERSION" ]; then
  yum install -y \
    bison \
    bison-devel \
    expat \
    expat-devel \
    flex \
    iptables-services \
    libtool-ltdl-devel \
    libunistring-devel.x86_64 \
    libuuid \
    libuuid-devel \
    lynx \
    redis \
    hiredis \
    hiredis-devel \
    python-devel

  mkdir -p /usr/src/kamailio
  cd /usr/src/kamailio

  curl -vsL https://github.com/kamailio/kamailio/archive/${KAMAILIO_VERSION}.tar.gz | tar --strip-components 1 -xz

  # 1.5 jobs per core works out okay
  : ${JOBS:=$(( $(nproc) + $(nproc) / 2 ))}

  # Make of modules list files
  make PREFIX={{ kamailio_location }} cfg

  # Add desired modules
  MODULES="presence presence_xml app_python auth_ephemeral db_redis outbound tls uuid websocket"
  echo "include_modules= $MODULES" >> src/modules.lst

  until make -j ${JOBS} all
  do
    >&2 echo "Make of kamailio failed, retrying"
  done
    sleep 1
    >&2 echo "Make of kamailio done"
  make install

  rm -rf /usr/src/kamailio

  echo "Building kamailio rpm"
  cd /root/oml_build/rpms
  fpm -s dir -t rpm -n kamailio -v {{ kamailio_version }} {{ kamailio_location}} /etc/systemd/system/kamailio.service || true
  echo "Uploading rpm to public server"
  scp $SSH_OPTIONS -P 40404 -i /vagrant/vps_key.pem kamailio-{{ kamailio_version }}* root@www.freetech.com.ar:/var/www/html/omnileads/build
fi
