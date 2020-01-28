#!/bin/bash
# Script de instalacion de omnileads con docker

# Variables a usar
export COMPOSE_FILE=/home/omnileads/prodenv/docker-compose.yml
DOCKER_COMPOSE=$(which docker-compose)
DOCKER=$(which docker)
PSQL=$(which psql)
MYSQL=$(which mysql)

RTPENGINE=$(which rtpengine)
GREEN='\033[0;32m'
NC='\033[0m' # No Color
os=`awk -F= '/^NAME/{print $2}' /etc/os-release`

printf "$GREEN **************[oml-pbx] Beginning OMniLeads installation***************** $NC\n"
echo ""

printf "$GREEN ** [oml-pbx] Setting the system to raise up OMniLeads with Docker $NC\n"
useradd omnileads > /dev/null 2>&1
cp -a "$(pwd)" /home/omnileads/
source "/home/omnileads/prodenv/.env" 

if [ -z $DOCKER_HOSTNAME ]; then
    printf "$GREEN ** [oml-pbx] Variable \$DOCKER_HOSTNAME not set $NC\n"
    exit 1
elif [ -z $DOCKER_IP ]; then
    printf "$GREEN ** [oml-pbx] Variable \$DOCKER_IP not set $NC\n"
    exit 1
elif [ -z $RELEASE ]; then
    printf "$GREEN ** [oml-pbx] Variable \$RELEASE not set $NC\n"
    exit 1
elif [ -z $DJANGO_PASS ]; then
    printf "$GREEN ** [oml-pbx] Variable \$DJANGO_PASS not set $NC\n"
    exit 1
elif [ -z $MYSQL_HOST ]; then
    printf "$GREEN ** [oml-pbx] Variable \$MYSQL_HOST not set $NC\n"
    exit 1
elif [ -z $PGHOST ]; then
    printf "$GREEN ** [oml-pbx] Variable \$PGHOST not set $NC\n"
    exit 1
elif [ -z $PGPASSWORD ]; then
    printf "$GREEN ** [oml-pbx] Variable \$PGPASSWORD not set $NC\n"
    exit 1
fi

if [ -z $DOCKER ]; then
    printf "$GREEN ** [oml-pbx] Installing docker $NC\n"
    yum install -y yum-utils device-mapper-persistent-data lvm2
    yum-config-manager -y --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
fi

if [ -z $DOCKER_COMPOSE ]; then
    printf "$GREEN ** [oml-pbx] Installing docker-compose $NC\n"
    curl -m 3000 -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

if [ "$os" == '"CentOS Linux"' ]; then
    printf "$GREEN ** [oml-pbx] Stopping and disabling firewalld $NC\n"
    systemctl disable firewalld
    systemctl stop firewalld
    if [ -z $MYSQL ]; then
        printf "$GREEN ** [oml-pbx] Installing mariadb and net-tools $NC\n"
        yum install -y mariadb-server net-tools
        systemctl start mariadb
        systemctl enable mariadb
        mysql_secure_installation
    fi
fi

if [ -z $PSQL ]; then
    printf "$GREEN ** [oml-pbx] Installing postgresql $POSTGRES_VERSION $NC\n"
    yum install -y https://download.postgresql.org/pub/repos/yum/$POSTGRES_VERSION/redhat/rhel-7-x86_64/pgdg-centos11-$POSTGRES_VERSION-2.noarch.rpm
    yum -y install postgresql11-server postgresql11 postgresql11-plperl
    printf "$GREEN ** [oml-pbx] Initializing pg11 cluster $NC\n"
    /usr/pgsql-$POSTGRES_VERSION/bin/postgresql-$POSTGRES_VERSION-setup initdb
    printf "$GREEN ** [oml-pbx] Modifying pg_hba.conf file $NC\n"
    cat > /var/lib/pgsql/$POSTGRES_VERSION/data/pg_hba.conf << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             $SUBNET                 md5
EOF
    printf "$GREEN ** [oml-pbx] Modifying postgresql.conf listen address $NC\n"
    sed -i "s/#listen_addresses.*/listen_addresses = '*'/g" /var/lib/pgsql/$POSTGRES_VERSION/data/postgresql.conf
    systemctl start postgresql-$POSTGRES_VERSION
    systemctl enable postgresql-$POSTGRES_VERSION
    printf "$GREEN ** [oml-pbx] Creating postgresql user/database for OMniLeads $NC\n"
    su -c 'psql -c "create database '$PGDATABASE';"' postgres
    su -s /bin/bash -c "psql -c \"create user $PGUSER with encrypted password '$PGPASSWORD';\"" postgres
    su -c 'psql -c "grant all privileges on database '$PGDATABASE' to '$PGUSER';"' postgres
    su -c 'psql -c "ALTER USER '$PGUSER' WITH SUPERUSER;;"' postgres
    printf "$GREEN ** [oml-pbx] Add extension plperl $NC\n"
    PGUSER=$PGUSER PGPASSWORD=$PGPASSWORD psql -d $PGDATABASE -h 127.0.0.1 -c  "CREATE EXTENSION plperl"
fi

if [ -z $RTPENGINE ]; then
    printf "$GREEN ** [oml-pbx] Installing rtpengine $NC\n"
    export RTPENGINE_VERSION DOCKER_IP
    /home/omnileads/prodenv/rtpengine_install.sh > /dev/null 2>&1
fi

if [ ! -f /home/omnileads/prodenv/kamailio-local.cfg ];then
    printf "$GREEN ** [oml-pbx] Creating kamailio-local.cfg file for Kamailio  $NC\n"
    cat > /home/omnileads/prodenv/kamailio-local.cfg <<EOF
#!substdef "!MY_IP_ADDR!kamailio!g"
#!substdef "!MY_DOMAIN!kamailio!g"
#!substdef "!MY_ASTERISK!asterisk!g"
#!substdef "!RTPENGINE_HOST!${DOCKER_IP}!g"
#!substdef "!REDIS_URL!redis!g"
#!substdef "!RTPENGINE_PORT!22222!g"
#!substdef "!MY_UDP_PORT!5060!g"
#!substdef "!MY_TCP_PORT!5060!g"
#!substdef "!MY_TLS_PORT!5061!g"
#!substdef "!MY_WS_PORT!1080!g"
#!substdef "!MY_WSS_PORT!14443!g"
#!substdef "!MY_MSRP_PORT!6060!g"
#!substdef "!MY_MSRPTCP_PORT!6061!g"
#!substdef "!MY_ASTERISK_PORT!5160!g"

#!substdef "!MY_UDP_ADDR!udp:MY_IP_ADDR:MY_UDP_PORT!g"
#!substdef "!MY_TCP_ADDR!tcp:MY_IP_ADDR:MY_TCP_PORT!g"
#!substdef "!MY_TLS_ADDR!tls:MY_IP_ADDR:MY_TLS_PORT!g"
#!substdef "!MY_WS_ADDR!tcp:MY_IP_ADDR:MY_WS_PORT!g"
#!substdef "!MY_WSS_ADDR!tls:MY_IP_ADDR:MY_WSS_PORT!g"
#!substdef "!MY_MSRP_ADDR!tls:MY_IP_ADDR:MY_MSRP_PORT!g"
#!substdef "!MY_MSRPTCP_ADDR!tcp:MY_IP_ADDR:MY_MSRPTCP_PORT!g"
#!substdef "!MSRP_MIN_EXPIRES!1800!g"
#!substdef "!MSRP_MAX_EXPIRES!3600!g"
#!substdef "!MODULES_LOCATION!/usr/lib/kamailio/modules/!g"
#!substdef "!PKEY_LOCATION!/etc/kamailio/certs/key.pem!g"
#!substdef "!CERT_LOCATION!/etc/kamailio/certs/cert.pem!g"
#!substdef "!SECRET_KEY!SUp3rS3cr3tK3y!g"
EOF
fi

if [ ! -f /home/omnileads/prodenv/odbc.ini ];then
    printf "$GREEN ** [oml-pbx] Creating odbc.ini file for asterisk connection to postgresql  $NC\n"
    cat > /home/omnileads/prodenv/odbc.ini <<EOF
[asteriskara]
Description         = PostgreSQL connection to 'asterisk' database
Driver              = PostgreSQL
Database            = $PGDATABASE
Servername          = $PGHOST
UserName            = $PGUSER
Port                = 5432
#Protocol            = 8.1
ReadOnly            = No
RowVersioning       = No
ShowSystemTables    = No
ShowOidColumn       = No
FakeOidIndex        = No
ConnSettings        =
EOF
fi

if [ ! -f /etc/systemd/system/omnileads-pbx.service ];then
    printf "$GREEN ** [oml-pbx] Creating systemd service for OMniLeads [omnileads-pbx] $NC\n"
    cat > /etc/systemd/system/omnileads-pbx.service <<EOF
[Unit]
Description=OMniLeads on PBX Application Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
EnvironmentFile=/home/omnileads/prodenv/.env
Environment=COMPOSE_FILE=/home/omnileads/prodenv/docker-compose.yml
RemainAfterExit=yes
WorkingDirectory=/home/omnileads/prodenv/
ExecReload=/usr/local/bin/docker-compose up -d
ExecStart=/usr/local/bin/docker-compose up -d
ExecStartPost=/bin/bash /home/omnileads/prodenv/postinstall.sh
ExecStop=/usr/local/bin/docker-compose down
ExecStopPost=/usr/sbin/iptables -D DOCKER -p udp -m udp -d $CIP/32 ! -i docker0 -o docker0 --dport $RTP_START:$RTP_FINISH -j ACCEPT
ExecStopPost=/usr/sbin/iptables -D INPUT -p udp -j RTPENGINE --id 0
TimeoutStartSec=0
TimeoutStopSec=0

[Install]
WantedBy=multi-user.target
EOF
systemctl enable omnileads-pbx
fi   

printf "$GREEN ** [oml-pbx] Raising up OMniLeads for first time, this can take a long time, be patient $NC\n"
service docker restart
usermod -aG docker omnileads
git checkout "$(pwd)"/.env
systemctl enable omnileads-pbx
systemctl start omnileads-pbx
printf "$GREEN ** [oml-pbx] Executing post installation tasks $NC\n"
export RTP_START RTP_FINISH
printf "$GREEN ** [oml-pbx] Running mysql configuration steps $NC\n"
MYSQL_PWD=$MYSQL_ROOT_PASS mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '$MYSQL_ROOT_PASS' WITH GRANT OPTION;"
MYSQL_PWD=$MYSQL_ROOT_PASS mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO '$WOMBAT_DB_USER'@'%' IDENTIFIED BY '$WOMBAT_DB_PASS' WITH GRANT OPTION;"
/home/omnileads/prodenv/postinstall.sh

printf "$GREEN **************[oml-pbx] Installation completed ***************** $NC\n"

echo "
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@/@/@////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@/@@@/@@@/@@@@@@@/@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@
  @@@@@@/@@@/@@@/@@@@@@@/@@@@/@@@@@@@//@@@@@/@@@///@@@@@&//@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@
  @@@@@@@@/@/@@@&/@@//@@@(@/@@@@@@@@/@@@@@@@@/@@////@@@@/@/@@@//@@@/@@@/@@@/@@@@@@@//@@@/@@@/@@@/@@@//@@@///@@/@@@/@@@@@@
  @@@@@@@@/@@/&//%//@/@//@@/@@@@@@@@/@@@@@@@@/%@//@//@@/@@/@@@/@@@@//@@/@@@/@@@@@@/@@@//@@@@@/////@/@@@@@@#/@@///@@@@@@@@
  @@@@@@@////@/@@////@@/@///@@@@@@@@//@@@@@@//@@//@@/@/@@@/@@@/@@@@//@@/@@@/@@@@@@///@@@@/@/@@@@@/@@/@@@@@//@@@@@@/@@@@@@
  @@@@@@/@@@//@//@@@@/@@/@@@@/@@@@@@@@//////@@@@//@@@/@@@@/@@@/@@@@//@@/@@@///////@@////@@@@////@/@@@/////@/@@/////@@@@@@
  @@@@@@/@@@//@@@@@@/@@@//@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@//@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                                          The Open Source Contact Center Solution
                                           Copyright (C) 2018 Freetech Solutions"
echo ""