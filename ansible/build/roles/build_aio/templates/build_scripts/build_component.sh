#!/bin/bash

PROGNAME=$(basename $0)

CheckRPM() {
  echo "Checking if RPM exists in AWS s3 bucket"
  aws s3 ls s3://{{ fts_public_bucket }}/${COMPONENT}/${COMPONENT}-${VERSION}.x86_64.rpm
  if [[ $? -eq 0 ]]; then
    echo "Component $COMPONENT already builded in version $VERSION, exiting"
    exit 0
  else
    echo "Component $COMPONENT was not found in version $VERSION, proceeding to build"
  fi
}

AsteriskBuild() {
  ASTERISK_VERSION=$VERSION
  if test -z ${ASTERISK_VERSION}; then
    echo "${PROGNAME}: ASTERISK_VERSION required" >&2
    exit 1
  fi

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
  mkdir -p /usr/src/codecs \
    && cd /usr/src/codecs \
    && wget https://{{ fts_public_bucket }}.s3.amazonaws.com/codec_g729.so \
    && chmod 755 codec_g729.so \
    && cp *.so {{ asterisk_location }}/lib64/asterisk/modules/
  cd /
  rm -rf /usr/src/asterisk \
         /usr/src/codecs
}

KamailioBuild() {
  KAMAILIO_VERSION=$VERSION

  if test -z ${KAMAILIO_VERSION}; then
    echo "${PROGNAME}: KAMAILIO_VERSION required" >&2
    exit 1
  fi

  yum install -y \
    bison \
    bison-devel \
    expat \
    expat-devel \
    flex \
    iptables-services \
    libtool-ltdl-devel \
    libxml2-devel \
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
}

VirtualenvBuild() {
  VIRTUALENV_VERSION=$VERSION
  if test -z ${VIRTUALENV_VERSION}; then
    echo "${PROGNAME}: VIRTUALENV_VERSION required" >&2
    exit 1
  fi
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
    git

  # Setting virtualenv
  python3 -m venv {{ virtualenv_location }}
  source {{ virtualenv_location }}/bin/activate
  pip3 install setuptools --upgrade
  cd {{ virtualenv_location }}
  pip3 install wheel
  pip3 install -r {{ repo_location }}/requirements/requirements.txt --exists-action 'w'
}

RtpengineBuild() {
  RTPENGINE_VERSION=$VERSION
  if test -z ${RTPENGINE_VERSION}; then
    echo "${PROGNAME}: RTPENGINE_VERSION required" >&2
    exit 1
  fi

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
}

BuildRPM() {
  # Build of rpm using fpm
  echo "Build $COMPONENT rpm"
  if [ ! -d /root/rpms ]; then mkdir /root/rpms; fi
  cd /root/rpms
  fpm -s dir -t rpm -n $COMPONENT -v $VERSION -f $THINGS_TO_BUILD || true
  # Upload of rpm to VPS fts server
  echo "Uploading rpm to s3 bucket"
  aws s3 cp $COMPONENT* s3://{{ fts_public_bucket }}/${COMPONENT}/${COMPONENT}-${VERSION}.x86_64.rpm
}

for i in "$@"
do
  case $i in
    --component=*)
      COMPONENT="${i#*=}"
      CheckRPM
      set -e
      if [ "$COMPONENT" == "asterisk" ]; then
        THINGS_TO_BUILD="{{ asterisk_location}} /etc/systemd/system/asterisk.service"
        AsteriskBuild
      elif [ "$COMPONENT" == "kamailio" ]; then
        THINGS_TO_BUILD="{{ kamailio_location}} /etc/systemd/system/kamailio.service"
        KamailioBuild
      elif [ "$COMPONENT" == "rtpengine" ]; then
        THINGS_TO_BUILD="/usr/local/bin/rtpengine /root/xt_RTPENGINE.ko /lib64/xtables/libxt_RTPENGINE.so /etc/systemd/system/rtpengine.service"
        RtpengineBuild
      elif [ "$COMPONENT" == "virtualenv" ]; then
        THINGS_TO_BUILD="{{ virtualenv_location}} /etc/systemd/system/omnileads.service"
        VirtualenvBuild
      fi
      BuildRPM
      shift
    ;;
    --version=*)
      VERSION="${i#*=}"
      shift
    ;;
    --help|-h)
      shift
      exit 1
    ;;
    *)
      echo "One or more invalid options, use ./build.sh -h or ./build.sh --help"
      exit 1
    ;;
  esac
done
