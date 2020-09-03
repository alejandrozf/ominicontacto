#!/bin/bash
PROGNAME=$(basename $0)
PATH=$PATH:/usr/local/bin
RTPENGINE_VERSION_INSTALLED=$(rtpengine -v 2>&1 |awk -F "~" '{print $2}'|cut -c 3-)
RTPENGINE_VERSION={{ rtpengine_version }}
SSH_OPTIONS="-o stricthostkeychecking=no -o ConnectTimeout=10"

if test -z ${RTPENGINE_VERSION}; then
  echo "${PROGNAME}: RTPENGINE_VERSION required" >&2
  exit 1
fi

set -ex

if [ "$RTPENGINE_VERSION_INSTALLED" != "$RTPENGINE_VERSION" ]; then
  yum install -y \
    iptables-devel \
    xmlrpc-c-devel \
    xmlrpc-c \
    glib2-devel \
    glib2 \
    pcre \
    pcre-devel \
    libevent-devel \
    json-glib-devel \
    libpcap-devel \
    hiredis \
    hiredis-devel

  mkdir -p /usr/src/rtpengine
  cd /usr/src/rtpengine

  curl -vsL https://github.com/sipwise/rtpengine/archive/mr$RTPENGINE_VERSION.tar.gz | tar --strip-components 1 -xz

  # 1.5 jobs per core works out okay
  : ${JOBS:=$(( $(nproc) + $(nproc) / 2 ))}

  # Install ffmpeg
  rpm -v --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
  rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm ||true
  yum install ffmpeg ffmpeg-devel -y

  # Build of daemon
  cd daemon && make && cp rtpengine /usr/local/bin && cd ..

  # Modify kernel source in kernel rtpengine module Makefile and make of this module
  KERNEL_SOURCE="\/usr\/src\/kernels\/\$(shell uname -r)"
  sed -i "2s/.*/KSRC   ?= $KERNEL_SOURCE/g" kernel-module/Makefile
  cd kernel-module && make && cp xt_RTPENGINE.ko /root/ && cd ..

  # Make of iptables-extension
  cd iptables-extension && make && cp libxt_RTPENGINE.so /lib64/xtables && cd ..

  rm -rf /usr/src/rtpengine
fi
echo "Building rtpengine rpm"
cd /vagrant/build/rpms
fpm -s dir -t rpm -n rtpengine -v {{ rtpengine_version }} -f /usr/local/bin/rtpengine /root/xt_RTPENGINE.ko /lib64/xtables/libxt_RTPENGINE.so /etc/systemd/system/rtpengine.service || true
echo "Uploading rpm to public server"
scp $SSH_OPTIONS -P 40404 -i /vagrant/vps_key.pem rtpengine-{{ rtpengine_version }}* root@www.freetech.com.ar:/var/www/html/omnileads/build
