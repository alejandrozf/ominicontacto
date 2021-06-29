#!/bin/bash

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
SRC=/usr/src
PATH_DEPLOY=install/onpremise/deploy/ansible

COMPONENT_RELEASE=${omnileads_release}

STAGE=${stage}
#STAGE=digitalocean
#STAGE=aws
#STAGE=oraclecloud
#STAGE=digitalocean
#STAGE=linode
#STAGE=vultr
#STAGE=centos7
#STAGE=vagrant

TENANT_NAME=${tenant}

# *********************** BLOCK DEVICE or S3 BUCKET ************************
CALLREC_DIR_DST=/opt/omnileads/asterisk/var/spool/asterisk/monitor
CALLREC_DEVICE_TYPE=${callrec_store} # local, s3, nfs or disk

# if callrec device like DISK BLOCK DEVICE
if [[ $CALLREC_DEVICE_TYPE == "disk" ]]; then
  CALLREC_BLOCK_DEVICE=/dev/disk/by-label/callrec-$TENANT_NAME
fi

# S3 params when you select S3 like store for callrec
if [[ $CALLREC_DEVICE_TYPE == "s3" ]]; then
  S3_ACCESS_KEY=${s3_access_key}
  S3_SECRET_KEY=${s3_secret_key} 
  S3URL=${s3url}
  BUCKET_NAME=${s3_bucket_name}
fi

# NFS host netaddr
if [[ $CALLREC_DEVICE_TYPE == "nfs" ]]; then
  NFS_NETADDR=${nfs_host}
fi

# *********************** persistent data STORE block devices ****************************
# *********************** persistent data STORE block devices ****************************
OPTOML_DEVICE=${optoml_device} #/dev/disk/by-label/optoml-$TENANT_NAME
PGSQL_DEVICE=${pgsql_device} #/dev/disk/by-label/pgsql-$TENANT_NAME

NIC=${NIC}

# *********************** ACD Asterisk VARS
ACD_AMI_USER=${ami_user} #omnileadsami
ACD_AMI_PASS=${ami_password} #098098ZZZ
ACD_HOST=${asterisk_host}

# ***********************  PGSQL Vars
PGSQL_DB=${pgsql_db}
PGSQL_USER=${pgsql_username}
PGSQL_PASS=${pgsql_pass}
PGSQL_HOST=${pgsql_host}
PGSQL_PORT=${pgsql_port}
PGSQL_CLOUD=${pgsql_cloud}

# ***********************  Dialer VARS
DIALER_API_USER=${dialer_user}
DIALER_API_PASS=${dialer_password}
DIALER_HOST=${dialer_host}
DIALER_MYSQL_HOST=${mysql_host}

# ***********************  WebRTC Bridge VARS
RTPENGINE_UDP_INI=20000
RTPENGINE_UDP_END=30000
RTPENGINE_HOST=${rtpengine_host}
KAMAILIO_HOST=${kamailio_host}

# ***********************  tell omlapp web the components HOST addr
REDIS_HOST=${redis_host}
NGINX_HOST=${nginx_host}
WEBSOCKET_HOST=${websocket_host}
WEBSOCKET_PORT=${websocket_port}

# *********************** NAT voip webrtc setting ***************************************************************************************
# External IP. This parameter will set the public IP for SIP and RTP traffic, on environments where calls go through a firewall. 	      #
# auto = The public IP will be obtained from http://ipinfo.io/ip. It depends on the WAN connection that OML is using to go to Internet. #
# X.X.X.X = The public IP is set manually.  												                                                                    #
# none = If the agents are working on a LAN environment, and don't need a public IP.							                                      #
EXTERN_NAT_IP=${extern_ip}

# Tell OMLApp web some params ******************************************************************************
TZ=${omlapp_tz}
# Session Cookie Age (SCA) is the time in seconds that will last the https session when inactivity 
# is detected in the session (by default is 1 hour)                                                
SCA=${omlapp_sca}
# Ephemeral Credentials TTL (ECTTL) is the time in seconds that will last the SIP credentials      
# used to authenticate a SIP user in the telephony system (by default 8 hours)                     
ECCTL=${omlapp_ecctl}
# Login failure limit (LFM) is the attempts a user has to enter an incorrect password in login     
# Decrease it if paranoic reasons                                                                  
OMLAPP_LOGIN_FAILURE_LIMIT=${omlapp_login_fail_limit}

ENVIRONMENT_INIT=${init_env}
RESET_ADMIN_PASS=${reset_admin_pass}
SNGREP=${install_sngrep}

echo "***************** STAGE = STAGE -- NIC **********************************"
echo "***************** STAGE = STAGE -- NIC **********************************"
echo "***************** OML RELEASE = $COMPONENT_RELEASE **********************"
echo "***************** OML RELEASE = $COMPONENT_RELEASE **********************"

sleep 20

echo "******************************* block_device mount ********************************"
echo "******************************* block_device mount ********************************"
echo "******************************* block_device mount ********************************"
echo "******************************* block_device mount ********************************"
echo "******************************* block_device mount ********************************"
echo "******************************* block_device mount ********************************"

if [[ $OPTOML_DEVICE != "NULL" ]]; then
  mkdir /opt/omnileads
  echo "$OPTOML_DEVICE /opt/omnileads ext4 defaults,nofail,discard 0 0" >> /etc/fstab
fi

if [[ $PGSQL_DEVICE != "NULL" ]]; then
  mkdir /var/lib/pgsql
  echo "$PGSQL_DEVICE /var/lib/pgsql ext4 defaults,nofail,discard 0 0" >> /etc/fstab
fi

mount -a
sleep 10

mount


echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"

case $STAGE in
  digitalocean)
    echo -n "DigitalOcean"
    export PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    export PRIVATE_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)
    ;;
  linode)
    echo -n "Linode"
    export PRIVATE_IPV4=$(ip addr show $NIC |grep "inet 192.168" |awk '{print $2}' | cut -d/ -f1)
    export PUBLIC_IPV4=$(curl checkip.amazonaws.com)
    ;;
  centos7)
    echo -n "Onpremise CentOS7 Minimal"
    export PRIVATE_IPV4=$(ip addr show $PRIVATE_NIC | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    if [ $PUBLIC_NIC ]; then
      export PUBLIC_IPV4=$(ip addr show $PUBLIC_NIC | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    else
      export PUBLIC_IPV4=$(curl ifconfig.co)
    fi
    ;;
  vagrant)
    echo -n "Vagrant CentOS7 Minimal CI/CD"
    PRIVATE_IPV4=$STAGING_IP_CENTOS
    PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    ;;
  *)
    echo -n "you must to declare STAGE variable\n"
    ;;
esac

echo "************************ STAGE fix /etc/hosts *******************************"
echo "************************ STAGE fix /etc/hosts *******************************"
echo "************************ STAGE fix /etc/hosts *******************************"
echo "************************ STAGE fix /etc/hosts *******************************"
echo "************************ STAGE fix /etc/hosts *******************************"
echo "************************ STAGE fix /etc/hosts *******************************"

case $STAGE in

  digitalocean)
    echo -n "DigitalOcean"
    sed -i 's/127.0.0.1 '$(hostname)'/#127.0.0.1 '$(hostname)'/' /etc/hosts
    sed -i 's/::1 '$(hostname)'/#::1 '$(hostname)'/' /etc/hosts
    ;;
  vultr)
    echo -n "Linode"
    TEMP_HOSTNAME=$(hostname)
    sed -i 's/127.0.0.1 '$TEMP_HOSTNAME'/#127.0.0.1 '$TEMP_HOSTNAME'/' /etc/hosts
    sed -i 's/::1       '$TEMP_HOSTNAME'/#::1 '$TEMP_HOSTNAME'/' /etc/hosts
    ;;
  *)
    echo -n "your stage is clean\n"
    ;;
esac

echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"

setenforce 0
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
systemctl disable firewalld > /dev/null 2>&1
systemctl stop firewalld > /dev/null 2>&1

echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
yum -y install git python3 python3-pip kernel-devel

echo "***************************** install ansible **********************************"
echo "***************************** install ansible **********************************"
echo "***************************** install ansible **********************************"
echo "***************************** install ansible **********************************"
echo "***************************** install ansible **********************************"
echo "***************************** install ansible **********************************"

sleep 5
pip3 install --upgrade pip
pip3 install --user 'ansible==2.9.2'
export PATH="$HOME/.local/bin/:$PATH"

echo "************************** git clone omnileads repo ******************************"
echo "************************** git clone omnileads repo ******************************"
echo "************************** git clone omnileads repo ******************************"
echo "************************** git clone omnileads repo ******************************"
echo "************************** git clone omnileads repo ******************************"
echo "************************** git clone omnileads repo ******************************"

cd $SRC
git clone --recurse-submodules --branch $COMPONENT_RELEASE $COMPONENT_REPO
cd ominicontacto
git submodule update --remote

echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"

sed -i "s/#localhost ansible/localhost ansible/g" $PATH_DEPLOY/inventory  

# PGSQL edit inventory params **************************************************
# PGSQL edit inventory params **************************************************
if [[ "$PGSQL_CLOUD"  == "true" ]]; then
  sed -i "s/postgres_cloud=false/postgres_cloud=true/g" $PATH_DEPLOY/inventory
fi
if [[ "$PGSQL_DB"  != "NULL" ]]; then
  sed -i "s/postgres_database=omnileads/postgres_database=$PGSQL_DB/g" $PATH_DEPLOY/inventory
fi
if [[ "$PGSQL_USER"  != "NULL" ]]; then
  sed -i "s/#postgres_user=omnileads/postgres_user=$PGSQL_USER/g" $PATH_DEPLOY/inventory
fi
if [[ "$PGSQL_PASS"  != "NULL" ]]; then
  sed -i "s/#postgres_password=my_very_strong_pass/postgres_password=$PGSQL_PASS/g" $PATH_DEPLOY/inventory
fi
if [[ "$PGSQL_HOST"  != "NULL" ]]; then
  sed -i "s/#postgres_host=/postgres_host=$PGSQL_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$PGSQL_PORT"  != "NULL" ]]; then
  sed -i "s/#postgres_port=/postgres_port=$PGSQL_PORT/g" $PATH_DEPLOY/inventory
fi

# Asterisk ACD parameters *********************************************************
# Asterisk ACD parameters *********************************************************
if [[ "$ACD_AMI_USER"  != "NULL" ]]; then
  sed -i "s/#ami_user=omnileadsami/ami_user=$ACD_AMI_USER/g" $PATH_DEPLOY/inventory
fi
if [[ "$ACD_AMI_PASS"  != "NULL" ]]; then
  sed -i "s/#ami_password=5_MeO_DMT/ami_password=$ACD_AMI_PASS/g" $PATH_DEPLOY/inventory
fi
if [[ "$ACD_HOST"  != "NULL" ]]; then
  sed -i "s/#asterisk_host=/asterisk_host=$ACD_HOST/g" $PATH_DEPLOY/inventory
fi

# Wombat Dialer parameters ******************************************************
# Wombat Dialer parameters ******************************************************
if [[ "$DIALER_API_USER"  != "NULL" ]]; then
  sed -i "s/#dialer_user=/dialer_user=$DIALER_API_USER/g" $PATH_DEPLOY/inventory
fi
if [[ "$DIALER_API_PASS"  != "NULL" ]]; then
  sed -i "s/#dialer_password=/dialer_password=$DIALER_API_PASS/g" $PATH_DEPLOY/inventory
fi
if [[ "$DIALER_HOST" != "NULL" ]]; then
  sed -i "s/#dialer_host=/dialer_host=$DIALER_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$DIALER_MYSQL_HOST" != "NULL" ]]; then
  sed -i "s/#mysql_host=/mysql_host=$DIALER_MYSQL_HOST/g" $PATH_DEPLOY/inventory
fi

# WebRTC kamailio & rtpengine params **********************************************
# WebRTC kamailio & rtpengine params **********************************************
if [[ "$KAMAILIO_HOST"  != "NULL" ]]; then
  sed -i "s/#kamailio_host=/kamailio_host=$KAMAILIO_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$RTPENGINE_HOST" != "NULL" ]]; then
  sed -i "s/#rtpengine_host=/rtpengine_host=$RTPENGINE_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$EXTERN_NAT_IP" != "NULL" ]]; then
  sed -i "s/#extern_ip=auto/extern_ip=$EXTERN_NAT_IP/g" $PATH_DEPLOY/inventory
fi

# Redis, Nginx and Websockets params *******************************************************
# Redis, Nginx and Websockets params *******************************************************
if [[ "$REDIS_HOST" != "NULL" ]]; then
  sed -i "s/#redis_host=/redis_host=$REDIS_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$NGINX_HOST" != "NULL" ]]; then
  sed -i "s/#nginx_host=/nginx_host=$NGINX_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$WEBSOCKET_HOST" != "NULL" ]]; then
  sed -i "s/#websocket_host=/websocket_host=$WEBSOCKET_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$WEBSOCKET_PORT" != "NULL" ]]; then
  sed -i "s/#websocket_port=/websocket_port=$WEBSOCKET_PORT/g" $PATH_DEPLOY/inventory
fi

# Others App params *************************************************************************
# Others App params *************************************************************************
sed -i "s%\#TZ=%TZ=$TZ%g" $PATH_DEPLOY/inventory

if [[ "$OMLAPP_SCA" != "NULL" ]]; then
  sed -i "s/sca=3600/sca=$OMLAPP_SCA/g" $PATH_DEPLOY/inventory
fi
if [[ "$OMLAPP_ECCTL" != "NULL" ]]; then
  sed -i "s/sca=28800/sca=$OMLAPP_ECCTL/g" $PATH_DEPLOY/inventory
fi
if [[ "$OMLAPP_LOGIN_FAILURE_LIMIT" != "NULL" ]]; then
  sed -i "s/LOGIN_FAILURE_LIMIT=10/LOGIN_FAILURE_LIMIT=$OMLAPP_LOGIN_FAILURE_LIMIT/g" $PATH_DEPLOY/inventory
fi
if [[ "$RESET_ADMIN_PASS" == "true" ]]; then
  sed -i "s/reset_admin_password=false/reset_admin_password=true/g" $PATH_DEPLOY/inventory
fi

sleep 5

echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
sleep 30

cd $PATH_DEPLOY
./deploy.sh -i --iface=$NIC

echo "************************************** NET File Systen callrec *******************************************"
echo "************************************** NET File Systen callrec *******************************************"
echo "************************************** NET File Systen callrec *******************************************"
echo "************************************** NET File Systen callrec *******************************************"
echo "************************************** NET File Systen callrec *******************************************"
echo "************************************** NET File Systen callrec *******************************************"

case $CALLREC_DEVICE_TYPE in
  s3)
    echo "s3 callrec device \n"
    yum install -y epel-release && yum install -y s3fs-fuse
    echo "$S3_ACCESS_KEY:$S3_SECRET_KEY" > ~/.passwd-s3fs
    chmod 600 ~/.passwd-s3fs
    if [ ! -d $CALLREC_DIR_DST ]; then 
      mkdir -p $CALLREC_DIR_DST
      chown omnileads.omnileads -R $CALLREC_DIR_DST
    fi  
    echo "$BUCKET_NAME:/$TENANT_NAME $CALLREC_DIR_DST fuse.s3fs _netdev,allow_other,use_path_request_style,url=$S3URL 0 0" >> /etc/fstab
    mount -a
    ;;
  nfs)
    echo "NFS callrec device \n"
    yum install -y nfs-utils nfs-utils-lib
    if [ ! -d $CALLREC_DIR_DST ]; then 
      mkdir -p $CALLREC_DIR_DST
      chown omnileads.omnileads -R $CALLREC_DIR_DST
    fi  
    echo "$NFS_NETADDR:$CALLREC_DIR_DST $CALLREC_DIR_DST nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab
    mount -a
    ;;
  disk)
    echo "disk callrec device \n"
    mkdir -p $CALLREC_DIR_DST
    echo "$CALLREC_BLOCK_DEVICE  $CALLREC_DIR_DST ext4 defaults,nofail,discard 0 0" >> /etc/fstab
    mount -a
    ;;
  *)
    echo "callrec on local filesystem \n"
    ;;
 esac 

sleep 30

echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"

if [[ "$RTPENGINE_HOST" == "NULL" && "$STAGE" != "centos7" ]]; then
  echo -n "STAGE rtpengine \n"
  echo "OPTIONS="-i $PUBLIC_IPV4 -o 60 -a 3600 -d 30 -s 120 -n 127.0.0.1:22222 -m $RTPENGINE_UDP_INI -M $RTPENGINE_UDP_END -L 7 --log-facility=local1""  > /etc/rtpengine-config.conf
  systemctl start rtpengine
fi

echo "********************************** REDIS accept conection on private NIC *********************************"
echo "********************************** REDIS accept conection on private NIC *********************************"
echo "********************************** REDIS accept conection on private NIC *********************************"
echo "********************************** REDIS accept conection on private NIC *********************************"
echo "********************************** REDIS accept conection on private NIC *********************************"
echo "********************************** REDIS accept conection on private NIC *********************************"

if [[ "$REDIS_HOST" == "NULL" ]]; then
  sed -i "s/bind 127.0.0.1/bind 127.0.0.1 $PRIVATE_IPV4/g" /etc/redis.conf
fi

echo "********************************** WA issue #172 *********************************"
echo "********************************** WA issue #172 *********************************"
echo "********************************** WA issue #172 *********************************"
echo "********************************** WA issue #172 *********************************"
echo "********************************** WA issue #172 *********************************"
echo "********************************** WA issue #172 *********************************"

chown omnileads.omnileads -R /opt/omnileads/media_root

echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"

if [[ "$ENVIRONMENT_INIT" == "true" ]]; then
  /opt/omnileads/bin/manage.sh inicializar_entorno
fi

echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"

if [[ "$SNGREP" == "true" ]]; then
  yum install ncurses-devel make libpcap-devel pcre-devel \
      openssl-devel git gcc autoconf automake -y
  cd /root && git clone https://github.com/irontec/sngrep
  cd sngrep && ./bootstrap.sh && ./configure && make && make install
  ln -s /usr/local/bin/sngrep /usr/bin/sngrep
fi

reboot
