#!/bin/bash
PROGNAME=$(basename $0)
PATH=$PATH:/usr/local/bin
REDIS_VERSION_INSTALLED=$(cat {{ install_prefix}}redis_version)
REDIS_VERSION={{ redis_version }}
SSH_OPTIONS="-o stricthostkeychecking=no -o ConnectTimeout=10"

if test -z ${REDIS_VERSION}; then
  echo "${PROGNAME}: REDIS_VERSION required" >&2
  exit 1
fi

set -ex

if [ "$REDIS_VERSION_INSTALLED" != "$REDIS_VERSION" ]; then
  yum install -y \
    tcl

  mkdir -p /usr/src/redis
  cd /usr/src/redis

  curl -vsL https://github.com/redis/redis/archive/${REDIS_VERSION}.tar.gz | tar --strip-components 1 -xz
  make USE_SYSTEMD=yes
  make test
  make install
  rm -rf /usr/src/redis
  rm -rf /usr/bin/redis*
  cp -a /usr/local/bin/redis-* /usr/bin/
  echo "{{ redis_version }}" > {{ install_prefix }}redis_version


fi
  echo "Building redis rpm"
  cd /vagrant/build/rpms
  fpm -s dir -t rpm -n redis -v {{ redis_version }} -f \
    /etc/systemd/system/redis-sentinel.service.d \
    /etc/systemd/system/redis.service \
    /etc/logrotate.d/redis \
    /etc/redis-sentinel.conf \
    /etc/redis.conf \
    /var/lib/redis \
    /var/log/redis \
    /usr/bin/redis-benchmark \
    /usr/bin/redis-check-aof \
    /usr/bin/redis-check-rdb \
    /usr/bin/redis-cli \
    /usr/bin/redis-sentinel \
    /usr/bin/redis-server \
    /usr/lib/systemd/system/redis-sentinel.service \
    /usr/libexec/redis-shutdown || true

echo "Uploading rpm to public server"
scp $SSH_OPTIONS -P 40404 -i /vagrant/vps_key.pem redis-{{ redis_version }}* root@www.freetech.com.ar:/var/www/html/omnileads/build
