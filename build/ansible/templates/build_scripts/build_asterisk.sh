#!/bin/bash
PROGNAME=$(basename $0)
PATH=$PATH:/usr/local/bin

ASTERISK_VERSION_INSTALLED=$({{ asterisk_location }}/sbin/asterisk -V |awk -F " " '{print $2}')
ASTERISK_VERSION={{ asterisk_version }}
SSH_OPTIONS="-o stricthostkeychecking=no -o ConnectTimeout=10"

if test -z ${ASTERISK_VERSION}; then
  echo "${PROGNAME}: ASTERISK_VERSION required" >&2
  exit 1
fi

set -ex

if [ "$ASTERISK_VERSION_INSTALLED" != "$ASTERISK_VERSION" ]; then
  yum install -y  \
    dh-autoreconf \
    sqlite-devel \
    subversion \
    unixODBC \
    unzip

  mkdir -p /usr/src/asterisk
  cd /usr/src/asterisk

  curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/releases/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz
  curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz || \
  curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/old-releases/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz

  # 1.5 jobs per core works out okay
  : ${JOBS:=$(( $(nproc) + $(nproc) / 2 ))}

  # Execute asterisk prerequisites packages installation script
  contrib/scripts/install_prereq install

  # Add res_json install tasks
  git clone https://github.com/felipem1210/asterisk-res_json
  ./asterisk-res_json/install.sh

  # Add mp3 codec
  contrib/scripts/get_mp3_source.sh

  # Configure
  ./configure --with-jansson-bundled --libdir={{ asterisk_location }}/lib64 --prefix={{ asterisk_location }}
  make menuselect/menuselect menuselect-tree menuselect.makeopts

  # disable BUILD_NATIVE to avoid platform issues
  menuselect/menuselect --disable BUILD_NATIVE menuselect.makeopts

  # enable good things
  menuselect/menuselect --enable BETTER_BACKTRACES menuselect.makeopts
  menuselect/menuselect --enable chan_ooh323 menuselect.makeopts
  menuselect/menuselect --enable BETTER_BACKTRACES menuselect.makeopts
  menuselect/menuselect --enable format_mp3 menuselect.makeopts
  menuselect/menuselect --enable codec_opus menuselect.makeopts

  until make -j ${JOBS} all
  do
    >&2 echo "Make of asterisk failed, retrying"
  done
    sleep 1
    >&2 echo "Make of asterisk done"
  make install
  make config
  ldconfig
  make samples

  # set runuser and rungroup
  sed -i -E 's/^;(run)(user|group)/\1\2/' {{ asterisk_location }}/etc/asterisk/asterisk.conf

  # Install opus, for some reason menuselect option above does not working
  mkdir -p /usr/src/codecs/opus \
    && cd /usr/src/codecs/opus \
    && curl -vsL http://downloads.digium.com/pub/telephony/codec_opus/${OPUS_CODEC}.tar.gz | tar --strip-components 1 -xz \
    && cp *.so {{ asterisk_location }}/usr/lib64/asterisk/modules/ \
    && cp codec_opus_config-en_US.xml {{ asterisk_location }}/var/lib/asterisk/documentation/

  cd /
  rm -rf /usr/src/asterisk \
         /usr/src/codecs
fi
  # Build of rpm using fpm
  echo "Build asterisk rpm"
  cd /vagrant/build/rpms
  fpm -s dir -t rpm -n asterisk -v {{ asterisk_version }} {{ asterisk_location}} /etc/systemd/system/asterisk.service || true
  # Upload of rpm to VPS fts server
  echo "Uploading rpm to public server"
  scp $SSH_OPTIONS -P 40404 -i /vagrant/vps_key.pem asterisk-{{ asterisk_version }}* root@www.freetech.com.ar:/var/www/html/omnileads/build
