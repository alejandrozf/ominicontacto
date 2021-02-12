#!/bin/bash
PROGNAME=$(basename $0)

if test -z ${ASTERISK_VERSION}; then
  echo "${PROGNAME}: ASTERISK_VERSION required" >&2
  exit 1
fi

set -ex

useradd --system asterisk

apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --no-install-suggests \
    autoconf \
    binutils-dev \
    build-essential \
    ca-certificates \
    curl \
    file \
    git \
    libcurl4-openssl-dev \
    libedit-dev \
    libgsm1-dev \
    libogg-dev \
    libpopt-dev \
    libresample1-dev \
    libspandsp-dev \
    libspeex-dev \
    libspeexdsp-dev \
    libsqlite3-dev \
    libsrtp2-dev \
    libssl-dev \
    libvorbis-dev \
    libxml2-dev \
    libxslt1-dev \
    procps \
    portaudio19-dev \
    unixodbc \
    unixodbc-bin \
    unixodbc-dev \
    subversion \
    odbcinst \
    uuid \
    uuid-dev \
    xmlstarlet

apt-get purge -y --auto-remove
rm -rf /var/lib/apt/lists/*

mkdir -p /usr/src/asterisk
cd /usr/src/asterisk

curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/releases/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz || \
curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz || \
curl -vsL http://downloads.asterisk.org/pub/telephony/asterisk/old-releases/asterisk-${ASTERISK_VERSION}.tar.gz | tar --strip-components 1 -xz

# 1.5 jobs per core works out okay
: ${JOBS:=$(( $(nproc) + $(nproc) / 2 ))}

# Add res_json install tasks
git clone https://github.com/felipem1210/asterisk-res_json
./asterisk-res_json/install.sh

contrib/scripts/get_mp3_source.sh

./configure --with-jansson-bundled
make menuselect/menuselect menuselect-tree menuselect.makeopts

# disable BUILD_NATIVE to avoid platform issues
menuselect/menuselect --disable BUILD_NATIVE menuselect.makeopts

# enable good things
menuselect/menuselect --enable BETTER_BACKTRACES menuselect.makeopts
menuselect/menuselect --enable chan_ooh323 menuselect.makeopts
menuselect/menuselect --enable BETTER_BACKTRACES menuselect.makeopts
menuselect/menuselect --enable format_mp3 menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-EN-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-ES-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-FR-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-IT-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-RU-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-JA-WAV menuselect.makeopts
#menuselect/menuselect --enable CORE-SOUNDS-SV-WAV menuselect.makeopts
#menuselect/menuselect --enable EXTRA-SOUNDS-EN-WAV menuselect.makeopts
#menuselect/menuselect --enable EXTRA-SOUNDS-FR-WAV menuselect.makeopts
# codecs
menuselect/menuselect --enable codec_opus menuselect.makeopts
menuselect/menuselect --enable codec_gsm menuselect.makeopts
menuselect/menuselect --enable codec_silk menuselect.makeopts

# # download more sounds
# for i in CORE-SOUNDS-EN MOH-OPSOUND EXTRA-SOUNDS-EN; do
#     for j in ULAW ALAW G722 GSM SLN16; do
#         menuselect/menuselect --enable $i-$j menuselect.makeopts
#     done
# done

until make -j ${JOBS} all
do
  >&2 echo "Make of asterisk failed, retrying"
done
  sleep 1
  >&2 echo "Make of asterisk done"
make install

# copy default configs
# cp /usr/src/asterisk/configs/basic-pbx/*.conf /etc/asterisk/
make samples

# set runuser and rungroup
sed -i -E 's/^;(run)(user|group)/\1\2/' /etc/asterisk/asterisk.conf

# Install opus, for some reason menuselect option above does not working
mkdir -p /usr/src/codecs/opus \
  && cd /usr/src/codecs/opus \
  && curl -vsL http://downloads.digium.com/pub/telephony/codec_opus/${OPUS_CODEC}.tar.gz | tar --strip-components 1 -xz \
  && cp *.so /usr/lib/asterisk/modules/ \
  && cp codec_opus_config-en_US.xml /var/lib/asterisk/documentation/

#Install g729 codec
cd /usr/lib/asterisk/modules \
  && wget http://asterisk.hosting.lv/bin/codec_g729-ast160-gcc4-glibc-x86_64-barcelona.so \
  && chmod 755 codec_g729-ast160-gcc4-glibc-x86_64-barcelona.so \
  && mv codec_g729-ast160-gcc4-glibc-x86_64-barcelona.so codec_g729.so

mkdir -p /etc/asterisk/ \
         /var/spool/asterisk/fax

chown -R asterisk:asterisk /etc/asterisk \
                           /var/*/asterisk \
                           /usr/*/asterisk
chmod -R 750 /var/spool/asterisk

cd /
rm -rf /usr/src/asterisk \
       /usr/src/codecs

# remove *-dev packages
devpackages=`dpkg -l|grep '\-dev'|awk '{print $2}'|xargs`
DEBIAN_FRONTEND=noninteractive apt-get --yes purge \
  autoconf \
  build-essential \
  bzip2 \
  cpp \
  m4 \
  make \
  git \
  patch \
  perl \
  perl-modules \
  pkg-config \
  subversion \
  xz-utils \
  ${devpackages}
  
rm -rf /var/lib/apt/lists/*

exec rm -f /build-asterisk.sh
