#!/bin/bash
# Enviroment variables 
set -x

DEBIAN_FRONTEND=noninteractive
SUDO_FORCE_REMOVE=yes
PUBLIC_IPV4=$(wget -qO- ipinfo.io/ip)
RTPENGINE_PORT=22222
PORT_MIN=20000
PORT_MAX=30000
KERNEL_RELEASE=$(uname -r)
os=`awk -F= '/^NAME/{print $2}' /etc/os-release`

yum install -y epel-release
yum install -y kernel-devel kernel-headers iptables-devel xmlrpc-c-devel glib glib-devel gcc zlib zlib-devel openssl openssl-devel pcre pcre-devel libcurl libcurl-devel xmlrpc-c xmlrpc-c-devel
yum install -y libevent-devel glib2-devel json-glib-devel gperf libpcap-devel hiredis hiredis-devel
if [ "$os" == '"CentOS Linux"' ]; then
    yum install -y wget
    rpm -v --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
    rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
fi
yum install -y ffmpeg ffmpeg-devel

cd /usr/src
wget https://github.com/sipwise/rtpengine/archive/mr$RTPENGINE_VERSION.tar.gz
tar xzvf mr$RTPENGINE_VERSION.tar.gz 
cd rtpengine-mr$RTPENGINE_VERSION/daemon/ && make
cp rtpengine /usr/local/bin/
cd /usr/src/rtpengine-mr$RTPENGINE_VERSION/iptables-extension && make all
cp libxt_RTPENGINE.so /usr/lib64/xtables/

if [ "$os" == '"Sangoma Linux"' ]; then
    cd /lib/modules/$KERNEL_RELEASE
    ln -s /usr/src/kernels/$KERNEL_RELEASE/ build
fi

cd /usr/src/rtpengine-mr$RTPENGINE_VERSION/kernel-module && make
cp xt_RTPENGINE.ko /lib/modules/$KERNEL_RELEASE/extra/xt_RTPENGINE.ko
depmod -a
cat >  /etc/modules-load.d/rtpengine.conf <<EOF
# load xt_RTPENGINE module
xt_RTPENGINE
EOF
modprobe xt_RTPENGINE
echo 'add 0' > /proc/rtpengine/control

cat > /etc/rtpengine-config.conf <<EOF
OPTIONS="-i internal/$DOCKER_IP -n $DOCKER_IP:$RTPENGINE_PORT -m $PORT_MIN -M $PORT_MAX --table=0 -L 7 --log-stderr"
EOF

cat > /etc/systemd/system/rtpengine.service <<EOF
[Unit]
Description=Kernel based rtp proxy
After=network.target

[Service]
Type=forking
PIDFile=/var/run/rtpengine.pid
EnvironmentFile=-/etc/rtpengine-config.conf
ExecStart=/usr/local/bin/rtpengine -p /var/run/rtpengine.pid \$OPTIONS

Restart=always

[Install]
WantedBy=multi-user.target

EOF

systemctl enable rtpengine
systemctl start rtpengine
