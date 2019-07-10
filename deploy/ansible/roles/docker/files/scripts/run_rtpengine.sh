#! /bin/sh
set -x
RUNTIME=${1:-rtpengine}

if [ -n "${UNLOAD_MODULE}" ] ; then
  rmmod xt_RTPENGINE
fi
apt-get install lsmod modprobe -y
if lsmod | grep xt_RTPENGINE || modprobe xt_RTPENGINE; then
  echo "rtpengine kernel module already loaded."
else
  if which apt-get ; then
    # Build the kernel module for the docker run host
    apt-get update -y
    export DEBIAN_FRONTEND=noninteractive

    apt-get install -y linux-headers-$(uname -r) linux-image-$(uname -r) debhelper gcc module-assistant
    cd /usr/src
    dpkg -i ngcp-rtpengine-kernel-source_5.5.3.1+0~mr5.5.3.1_all.deb
    module-assistant update
    module-assistant auto-install ngcp-rtpengine-kernel-source
    modprobe xt_RTPENGINE
    apt-get remove -y linux-headers-$(uname -r) linux-image-$(uname -r) debhelper gcc --purge
  else
    if which dnf || which yum ; then
      cd /rtpengine/daemon
      make
      cp -u rtpengine /usr/local/bin/
      cd /rtpengine/iptables-extension
      make
      cp -u libxt_RTPENGINE.so /lib64/xtables
      cd /rtpengine/kernel-module
      make
      cp -u xt_RTPENGINE.ko "/lib/modules/$(uname -r)/extra"
      depmod -a
    else
      echo "This script is not running on debian/ubuntu/centus/fedora, cannot attempt to build kernel module"
      exit 1
    fi
  fi
fi

# Gradually fill the options of the command rtpengine which starts the RTPEngine daemon
# The variables used are sourced from the configuration file rtpengine-conf

if [ -z "$INTERFACES" ]; then

  # Discover public and private IP for this instance
  export PRIVATE_IPV4="$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')"
#  export PUBLIC_IPV4="$(curl --fail -qs http://169.254.169.254/2014-11-05/meta-data/public-ipv4)"

  INTERFACES="${PRIVATE_IPV4}"
fi

for interface in $INTERFACES; do
    OPTIONS="$OPTIONS --interface=$interface"
done

[ -z "$LISTEN_TCP" ] || OPTIONS="$OPTIONS --listen-tcp=$LISTEN_TCP"
[ -z "$LISTEN_UDP" ] || OPTIONS="$OPTIONS --listen-udp=$LISTEN_UDP"
[ -z "$LISTEN_NG" ] || OPTIONS="$OPTIONS --listen-ng=$LISTEN_NG"
[ -z "$LISTEN_CLI" ] || OPTIONS="$OPTIONS --listen-cli=$LISTEN_CLI"
[ -z "$TIMEOUT" ] || OPTIONS="$OPTIONS --timeout=$TIMEOUT"
[ -z "$SILENT_TIMEOUT" ] || OPTIONS="$OPTIONS --silent-timeout=$SILENT_TIMEOUT"
[ -z "$PIDFILE" ] || OPTIONS="$OPTIONS --pidfile=$PIDFILE"
[ -z "$TOS" ] || OPTIONS="$OPTIONS --tos=$TOS"
[ -z "$PORT_MIN" ] || OPTIONS="$OPTIONS --port-min=$PORT_MIN"
[ -z "$PORT_MAX" ] || OPTIONS="$OPTIONS --port-max=$PORT_MAX"
[ -z "$REDIS" ] || OPTIONS="$OPTIONS --redis=$REDIS"
[ -z "$REDIS_DB" ] || OPTIONS="$OPTIONS --redis-db=$REDIS_DB"
[ -z "$REDIS_READ" ] || OPTIONS="$OPTIONS --redis-read=$REDIS_READ"
[ -z "$REDIS_READ_DB" ] || OPTIONS="$OPTIONS --redis-read-db=$REDIS_READ_DB"
[ -z "$REDIS_WRITE" ] || OPTIONS="$OPTIONS --redis-write=$REDIS_WRITE"
[ -z "$REDIS_WRITE_DB" ] || OPTIONS="$OPTIONS --redis-write-db=$REDIS_WRITE_DB"
[ -z "$B2B_URL" ] || OPTIONS="$OPTIONS --b2b-url=$B2B_URL"
[ -z "$NO_FALLBACK" -o \( "$NO_FALLBACK" != "1" -a "$NO_FALLBACK" != "yes" \) ] || OPTIONS="$OPTIONS --no-fallback"
OPTIONS="$OPTIONS --table=$TABLE"
[ -z "$LOG_LEVEL" ] || OPTIONS="$OPTIONS --log-level=$LOG_LEVEL"
[ -z "$LOG_FACILITY" ] || OPTIONS="$OPTIONS --log-facility=$LOG_FACILITY"
[ -z "$LOG_FACILITY_CDR" ] || OPTIONS="$OPTIONS --log-facility-cdr=$LOG_FACILITY_CDR"
[ -z "$LOG_FACILITY_RTCP" ] || OPTIONS="$OPTIONS --log-facility-rtcp=$LOG_FACILITY_RTCP"
[ -z "$NUM_THREADS" ] || OPTIONS="$OPTIONS --num-threads=$NUM_THREADS"
[ -z "$DELETE_DELAY" ] || OPTIONS="$OPTIONS --delete-delay=$DELETE_DELAY"
[ -z "$GRAPHITE" ] || OPTIONS="$OPTIONS --graphite=$GRAPHITE"
[ -z "$GRAPHITE_INTERVAL" ] || OPTIONS="$OPTIONS --graphite-interval=$GRAPHITE_INTERVAL"
[ -z "$GRAPHITE_PREFIX" ] || OPTIONS="$OPTIONS --graphite-prefix=$GRAPHITE_PREFIX"
[ -z "$MAX_SESSIONS" ] || OPTIONS="$OPTIONS --max-sessions=$MAX_SESSIONS"

# Homer Options
[ -z "$HOMER_DEST" ] || OPTIONS="$OPTIONS --homer=${HOMER_DEST}"
[ -z "$HOMER_PROTOCOL" ] || OPTIONS="$OPTIONS --homer-protocol=udp"
[ -z "$HOMER_CAP_ID" ] || OPTIONS="$OPTIONS --homer-id=$HOMER_CAP_ID"

if test "$FORK" = "no" ; then
	OPTIONS="$OPTIONS --foreground"
fi

set +e
if [ -e /proc/rtpengine/control ]; then
	echo "del $TABLE" > /proc/rtpengine/control 2>/dev/null
fi

OPTIONS = "$OPTIONS --log-stderr"

set -x

exec $RUNTIME $OPTIONS
