#!/bin/bash

########################## README ############ README ############# README #########################
# El script first_boot_installer, tiene como finalidad desplegar el componente sobre una instancia
# de linux exclusiva. Las variables que utiliza son "variables de entorno" de la instancia que está
# por lanzar el script como acto seguido al primer boot del sistema operativo.
# Dichas variables podrán ser provisionadas por un archivo .env (ej: Vagrant) o bien utilizando este
# script como plantilla de terraform.
#
# En el caso de necesitar ejecutar este script manualmente sobre el user_data de una instancia cloud
# o bien sobre una instancia onpremise a través de una conexión ssh, entonces se deberá copiar
# esta plantilla hacia un archivo ignorado por git (first_boot_installer.sh) para luego sobre
# dicha copia, descomentar las líneas que comienzan con la cadena "export", para posteriormente
# introducir el valor deseado a cada variable.
########################## README ############ README ############# README #########################

# ******************** SET ENV VARS ******************** #

# The infrastructure environment:
# Values: onpremise | digitalocean | linode | vultr | aws
#export oml_infras_stage=onpremise

# The GitLab branch
#export oml_app_release=release-1.16.0

# OMniLeads tenant NAME
#export oml_tenant_name=onpremise

# Device for recordings
# Values: local | s3-do | s3-aws | nfs | disk
#export oml_callrec_device=s3

# Parameters for S3 when s3-do is selected as store for oml_callrec_device
#export s3_access_key=
#export s3_secret_key=
#export s3url=
#export ast_bucket_name=

# Parameters for NFS when nfs is selected as store for oml_callrec_device
#export nfs_host=

# ******* persistent data STORE block devices *******

# Values: /dev/disk/by-label/optoml-${oml_tenant_name}
#export optoml_device=NULL
# Values: /dev/disk/by-label/pgsql-${oml_tenant_name}
#export pgsql_device=NULL

# Set your network interface
#export oml_nic=enp0s3

# ******* Variables for ACD Asterisk *******
# AMI connection from OMLApp
#export oml_ami_user=omnileadsami
#export oml_ami_password=098098ZZZ
# Values: NULL | IP address or FQDN
#export oml_acd_host=NULL

# ******* Variables for PGSQL *******
# POSTGRESQL network address and port
# Values: NULL | IP address or FQDN
#export oml_pgsql_host=NULL
#export oml_pgsql_port=5432
# POSTGRESQL user, password and DB parameters
#export oml_pgsql_db=omnileads
#export oml_pgsql_user=omnileads
#export oml_pgsql_password=098098ZZZ
# If PGSQL runs on cloud cluster, set this parameter to true
#export oml_pgsql_cloud=NULL

# ******* Variables for Dialer *******
#export api_dialer_user=demoadmin
#export api_dialer_password=demo
# Values: NULL | IP address or FQDN
#export oml_dialer_host=NULL

# ******* Variables for WebRTC bridge *******
# Values: NULL | IP address or FQDN
#export oml_rtpengine_host=NULL
# Values: NULL | IP address or FQDN
#export oml_kamailio_host=NULL

# ******* Variables for Redis and Websocket *******
# Values: NULL | IP address or FQDN
#export oml_redis_host=NULL
# Values: NULL | IP address or FQDN
#export oml_websocket_host=NULL
#export oml_websocket_port=NULL

# *********************** NAT voip webrtc setting ***************************************************************************************
# External IP. This parameter will set the public IP for SIP and RTP traffic, on environments where calls go through a firewall.        #
# Values: auto | IP address | none                                                                                                      #
# auto = The public IP will be obtained from http://ipinfo.io/ip. It depends on the WAN connection that OML is using to go to Internet. #
# X.X.X.X = The public IP is set manually.                                                                                              #
# none = If the agents are working on a LAN environment, and don't need a public IP.                                                    #
# ***************************************************************************************************************************************
#export oml_extern_ip=none

# ******* Vaiables for OMLApp web *******
#export oml_tz=America/Argentina/Cordoba
# Session Cookie Age (SCA): It's the time in seconds that will last the https session when inactivity
# is detected in the session (by default is 1 hour)
#export oml_app_sca=3600
# Ephemeral Credentials TTL (ECTTL): It's the time in seconds that will last the SIP credentials
# used to authenticate a SIP user in the telephony system (by default 8 hours)
#export oml_app_ecctl=3600
# Login failure limit (LFM): It's the number of attempts a user has to enter an incorrect password in login
# Decrease it if paranoic reasons
#export oml_app_login_fail_limit=10

# Values: true | false
#export oml_app_init_env=true
#export oml_app_reset_admin_pass=true
#export oml_app_install_sngrep=true

# ******************** SET ENV VARS ******************** #

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
SRC=/usr/src
PATH_DEPLOY=install/onpremise/deploy/ansible
CALLREC_DIR_DST=/opt/omnileads/asterisk/var/spool/asterisk/monitor
SSM_AGENT_URL="https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm"
S3FS="/bin/s3fs"
PATH_CERTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)/certs"

# if callrec device like DISK BLOCK DEVICE
if [[ ${oml_callrec_device} == "disk" ]];then
  CALLREC_BLOCK_DEVICE=/dev/disk/by-label/callrec-${oml_tenant_name}
fi

echo "******************** OML RELEASE = ${oml_app_release} ********************"

sleep 20

echo "******************** block_device mount ********************"

if [[ ${optoml_device} != "NULL" ]];then
  mkdir /opt/omnileads
  echo "${optoml_device} /opt/omnileads ext4 defaults,nofail,discard 0 0" >> /etc/fstab
fi

if [[ ${pgsql_device} != "NULL" ]];then
  mkdir /var/lib/pgsql
  echo "${pgsql_device} /var/lib/pgsql ext4 defaults,nofail,discard 0 0" >> /etc/fstab
fi

mount -a
sleep 10
mount

echo "******************** IPV4 address config ********************"

case ${oml_infras_stage} in
  aws)
    echo -n "AWS"
    PRIVATE_IPV4=$(ip addr show ${oml_nic} | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    PUBLIC_IPV4=$(curl ifconfig.co)
    ;;
  digitalocean)
    echo -n "DigitalOcean"
    PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    PRIVATE_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)
    ;;
  linode)
    echo -n "Linode"
    PRIVATE_IPV4=$(ip addr show ${oml_nic} |grep "inet 192.168" |awk '{print $2}' | cut -d/ -f1)
    PUBLIC_IPV4=$(curl checkip.amazonaws.com)
    ;;
  onpremise)
    echo -n "Onpremise CentOS7 Minimal"
    PRIVATE_IPV4=$(ip addr show ${oml_nic} | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    PUBLIC_IPV4=$(curl ifconfig.co)
    ;;
  vagrant)
    echo -n "Vagrant CentOS7 Minimal CI/CD"
    PRIVATE_IPV4=$STAGING_IP_CENTOS
    PUBLIC_IPV4=$(curl ifconfig.co)
    ;;
  *)
    echo -n "You must to set STAGE variable\n"
    ;;
esac

echo "******************** STAGE fix /etc/hosts ********************"

case ${oml_infras_stage} in
  digitalocean)
    echo -n "DigitalOcean"
    sed -i 's/127.0.0.1 '$(hostname)'/#127.0.0.1 '$(hostname)'/' /etc/hosts
    sed -i 's/::1 '$(hostname)'/#::1 '$(hostname)'/' /etc/hosts
    ;;
  vultr)
    echo -n "Vultr"
    TEMP_HOSTNAME=$(hostname)
    sed -i 's/127.0.0.1 '$TEMP_HOSTNAME'/#127.0.0.1 '$TEMP_HOSTNAME'/' /etc/hosts
    sed -i 's/::1       '$TEMP_HOSTNAME'/#::1 '$TEMP_HOSTNAME'/' /etc/hosts
    ;;
  *)
    echo -n "Your stage is clean.\n"
    ;;
esac

echo "******************** SELinux and firewalld disable ********************"

setenforce 0
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
systemctl disable firewalld > /dev/null 2>&1
systemctl stop firewalld > /dev/null 2>&1

echo "******************** yum update and install packages ********************"

case ${oml_infras_stage} in
  aws)
    amazon-linux-extras install epel
    yum install -y $SSM_AGENT_URL kernel-devel git
    yum install -y python3-pip patch libedit-devel libuuid-devel
    systemctl start amazon-ssm-agent
    systemctl enable amazon-ssm-agent
    ;;
  *)
    yum update -y
    yum -y install git python3 python3-pip kernel-devel
    ;;
esac

echo "******************** Ansible installation ********************"

sleep 5
pip3 install --upgrade pip
pip3 install --user 'ansible==2.9.2'
export PATH="$HOME/.local/bin/:$PATH"

echo "******************** git clone omnileads repo ********************"

cd $SRC
git clone --recurse-submodules --branch ${oml_app_release} $COMPONENT_REPO
cd ominicontacto
git submodule update --remote

echo "******************** inventory setting ********************"

sed -i "s/#localhost ansible/localhost ansible/g" $PATH_DEPLOY/inventory

# PGSQL edit inventory params **************************************************

if [[ "${oml_pgsql_cloud}"  == "true" ]];then
  sed -i "s/postgres_cloud=false/postgres_cloud=true/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_pgsql_db}"  != "NULL" ]];then
  sed -i "s/postgres_database=omnileads/postgres_database=${oml_pgsql_db}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_pgsql_user}"  != "NULL" ]];then
  sed -i "s/#postgres_user=omnileads/postgres_user=${oml_pgsql_user}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_pgsql_password}"  != "NULL" ]];then
  sed -i "s/#postgres_password=my_very_strong_pass/postgres_password=${oml_pgsql_password}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_pgsql_host}"  != "NULL" ]];then
  sed -i "s/#postgres_host=/postgres_host=${oml_pgsql_host}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_pgsql_port}"  != "NULL" ]];then
  sed -i "s/#postgres_port=/postgres_port=${oml_pgsql_port}/g" $PATH_DEPLOY/inventory
fi

# Asterisk ACD parameters *******

if [[ "${oml_ami_user}"  != "NULL" ]];then
  sed -i "s/#ami_user=omnileadsami/ami_user=${oml_ami_user}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_ami_password}"  != "NULL" ]];then
  sed -i "s/#ami_password=5_MeO_DMT/ami_password=${oml_ami_password}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_acd_host}"  != "NULL" ]];then
  sed -i "s/#asterisk_host=/asterisk_host=${oml_acd_host}/g" $PATH_DEPLOY/inventory
fi

# Wombat Dialer parameters *******

if [[ "${api_dialer_user}"  != "NULL" ]];then
  sed -i "s/#dialer_user=demoadmin/dialer_user=${api_dialer_user}/g" $PATH_DEPLOY/inventory
fi
if [[ "${api_dialer_password}"  != "NULL" ]];then
  sed -i "s/#dialer_password=demo/dialer_password=${api_dialer_password}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_dialer_host}" != "NULL" ]];then
  sed -i "s/#dialer_host=/dialer_host=${oml_dialer_host}/g" $PATH_DEPLOY/inventory
fi

# WebRTC kamailio & rtpengine params *******

if [[ "${oml_kamailio_host}"  != "NULL" ]];then
  sed -i "s/#kamailio_host=/kamailio_host=${oml_kamailio_host}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_rtpengine_host}" != "NULL" ]];then
  sed -i "s/#rtpengine_host=/rtpengine_host=${oml_rtpengine_host}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_extern_ip}" != "NULL" ]];then
  sed -i "s/#extern_ip=auto/extern_ip=${oml_extern_ip}/g" $PATH_DEPLOY/inventory
fi

# Redis, Nginx and Websockets params *******

if [[ "${oml_redis_host}" != "NULL" ]];then
  sed -i "s/#redis_host=/redis_host=${oml_redis_host}/g" $PATH_DEPLOY/inventory
fi
if [[ "$NGINX_HOST" != "NULL" ]];then
  sed -i "s/#nginx_host=/nginx_host=$NGINX_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_websocket_host}" != "NULL" ]];then
  sed -i "s/#websocket_host=/websocket_host=${oml_websocket_host}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_websocket_port}" != "NULL" ]];then
  sed -i "s/#websocket_port=/websocket_port=${oml_websocket_port}/g" $PATH_DEPLOY/inventory
fi

# Others App params *******

sed -i "s%\#TZ=%TZ=${oml_tz}%g" $PATH_DEPLOY/inventory

if [[ "$${oml_app_sca}" != "NULL" ]];then
  sed -i "s/sca=3600/sca=$${oml_app_sca}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_app_ecctl}" != "NULL" ]];then
  sed -i "s/sca=28800/sca=${oml_app_ecctl}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_app_login_fail_limit}" != "NULL" ]];then
  sed -i "s/LOGIN_FAILURE_LIMIT=10/LOGIN_FAILURE_LIMIT=${oml_app_login_fail_limit}/g" $PATH_DEPLOY/inventory
fi
if [[ "${oml_app_reset_admin_pass}" == "true" ]];then
  sed -i "s/reset_admin_password=false/reset_admin_password=true/g" $PATH_DEPLOY/inventory
fi

# User certs verification *******

if [ -f $PATH_CERTS/key.pem ] && [ -f $PATH_CERTS/cert.pem ];then
        cp $PATH_CERTS/key.pem $SRC/ominicontacto/install/onpremise/deploy/ansible/certs
        cp $PATH_CERTS/cert.pem $SRC/ominicontacto/install/onpremise/deploy/ansible/certs
fi

sleep 35

echo "******************** deploy.sh execution ********************"

cd $PATH_DEPLOY
./deploy.sh -i --iface=${oml_nic}

echo "******************** NET File Systen callrec ********************"

case ${oml_callrec_device} in
  s3-do)
    echo "Callrec device: S3-DigitalOcean \n"
    yum install -y s3fs-fuse
    echo "${s3_access_key}:${s3_secret_key} " > ~/.passwd-s3fs
    chmod 600 ~/.passwd-s3fs
    if [ ! -d $CALLREC_DIR_DST ];then
      mkdir -p $CALLREC_DIR_DST
      chown omnileads.omnileads -R $CALLREC_DIR_DST
    fi
    echo "${ast_bucket_name} $CALLREC_DIR_DST fuse.s3fs _netdev,allow_other,use_path_request_style,url=${s3url} 0 0" >> /etc/fstab
    mount -a
    ;;
  s3-aws)
    echo "Callrec device: S3-AWS \n"
    yum install -y s3fs-fuse
    if [ ${aws_region} == "us-east-1" ];then
      URL_OPTION=""
    else
      URL_OPTION="-o url=https://s3-${aws_region}.amazonaws.com"
    fi
    S3FS_OPTIONS="${ast_bucket_name} $CALLREC_DIR_DST -o iam_role=${iam_role_name} $URL_OPTION -o umask=0007 -o allow_other -o nonempty -o uid=$(id -u omnileads) -o gid=$(id -g omnileads) -o kernel_cache -o max_background=1000 -o max_stat_cache_size=100000 -o multipart_size=52 -o parallel_count=30 -o multireq_max=30 -o dbglevel=warn"
    echo "*** Comprobando que se tiene acceso al bucket"
    BUCKETS_LIST=$(aws s3 ls ${ast_bucket_name})
    until [ $? -eq 0 ];do
      >&2  echo "*** No se ha podido acceder al bucket"
      BUCKETS_LIST=$(aws s3 ls ${ast_bucket_name})
    done
    echo "*** Se pudo acceder al bucket!, siguiendo"
    echo "*** Montando bucket ${ast_bucket_name}"
    $S3FS $S3FS_OPTIONS
    echo "$S3FS $S3FS_OPTIONS" >> /etc/rc.local
    ;;
  nfs)
    echo "Callrec device: NFS \n"
    yum install -y nfs-utils nfs-utils-lib
    if [ ! -d $CALLREC_DIR_DST ];then
      mkdir -p $CALLREC_DIR_DST
      chown omnileads.omnileads -R $CALLREC_DIR_DST
    fi
    echo "${nfs_host}:$CALLREC_DIR_DST $CALLREC_DIR_DST nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab
    mount -a
    ;;
  disk)
    echo "Callrec device: Disk \n"
    mkdir -p $CALLREC_DIR_DST
    echo "$CALLREC_BLOCK_DEVICE  $CALLREC_DIR_DST ext4 defaults,nofail,discard 0 0" >> /etc/fstab
    mount -a
    ;;
  *)
    echo "callrec on local filesystem \n"
    ;;
 esac

sleep 30

echo "******************** Exec task if RTP run AIO ********************"

if [[ "${oml_rtpengine_host}" == "NULL" && "${oml_infras_stage}" != "onpremise" ]];then
  echo -n "STAGE rtpengine \n"
  echo "OPTIONS="-i $PUBLIC_IPV4 -o 60 -a 3600 -d 30 -s 120 -n 127.0.0.1:22222 -m 20000 -M 30000 -L 7 --log-facility=local1""  > /etc/rtpengine-config.conf
  systemctl start rtpengine
fi

echo "******************** REDIS accept conection on private NIC ********************"

if [[ "${oml_redis_host}" == "NULL" ]];then
  sed -i "s/bind 127.0.0.1/bind 127.0.0.1 $PRIVATE_IPV4/g" /etc/redis.conf
fi

echo "******************** WA issue #172 ********************"

chown omnileads.omnileads -R /opt/omnileads/media_root

echo "******************** setting demo environment ********************"

if [[ "${oml_app_init_env}" == "true" ]];then
  su -c "/opt/omnileads/bin/manage.sh inicializar_entorno" --login omnileads
fi

echo "******************** sngrep SIP sniffer install ********************"

if [[ "${oml_app_install_sngrep}" == "true" ]];then
  yum install ncurses-devel make libpcap-devel pcre-devel \
      openssl-devel git gcc autoconf automake -y
  cd /root && git clone https://github.com/irontec/sngrep
  cd sngrep && ./bootstrap.sh && ./configure && make && make install
  ln -s /usr/local/bin/sngrep /usr/bin/sngrep
fi

reboot
