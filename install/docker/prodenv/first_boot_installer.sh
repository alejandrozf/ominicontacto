#!/bin/bash

########################## README ############ README ############# README #########################
########################## README ############ README ############# README #########################
# El script first_boot_installer tiene como finalidad desplegar el componente sobre una instancia 
# de linux exclusiva. Las variables que utiliza son "variables de entorno" de la instancia que está
# por lanzar el script como acto seguido al primer boot del sistema operativo.
# Dichas variables podrán ser provisionadas por un archivo .env (ej: Vagrant) o bien utilizando este 
# script como plantilla de terraform. 
#
# En el caso de necesitar ejecutar este script manualmente sobre el user_data de una instancia cloud
# o bien sobre una instancia onpremise a través de una conexión ssh, entonces se deberá copiar
# esta plantilla hacia un archivo ignorado por git: first_boot_installer.sh para luego sobre 
# dicha copia descomentar las líneas que comienzan con la cadena "export" para posteriormente 
# introducir el valor deseado a cada variable.
########################## README ############ README ############# README #########################
########################## README ############ README ############# README #########################

# ************************************************************ SET ENV VARS **********************************************************************
# ************************************************************ SET ENV VARS **********************************************************************

# The infrastructure environment:
# onpremise | digitalocean | linode | vultr
export oml_infras_stage=digitalocean

# Component gitlab branch
export oml_app_release=oml-1972-dev-1st-boot-installer-envvars
export oml_app_img=develop
export oml_acd_img=latest
export oml_kamailio_img=latest
export oml_ws_img=latest
export oml_redis_img=1.0.3
export oml_nginx_img=develop

# OMniLeads tenant NAME
export oml_tenant_name=jade

# BLOCK DEVICE or S3 BUCKET 
# values: local | s3 | nfs | disk
export oml_callrec_device=s3

# S3 params when you select S3 like store for callrec
export s3_access_key=J76I5GYZES5EDG4KZP5B
export s3_secret_key=w4r7H1p1WX+nfPo0/tr/Eme2FjypGYExFVgtxDynrug
export s3url=https://sfo3.digitaloceanspaces.com
export s3_bucket_name=omnileads

# NFS host netaddr
#export nfs_host=

export oml_nic=eth1

# ******* ACD Asterisk VARS *******
# AMI conection from omlapp
export oml_ami_user=omnileadsami
export oml_ami_password=098098ZZZ

# ***********************  PGSQL Vars
# POSTGRESQL netaddr and port
# Values: NULL | IPADDR or FQDN
export oml_pgsql_host=10.10.10.11
export oml_pgsql_port=5432
# POSTGRESQL user, pass & DB params
export oml_pgsql_db=omnileads
export oml_pgsql_user=omnileads
export oml_pgsql_password=098098ZZZ
# IF PGSQL run on cloud cluster set this to true
export oml_pgsql_cloud=NULL

# ***********************  Dialer VARS
export api_dialer_user=demoadmin
export api_dialer_password=demo
# Values: NULL | IPADDR or FQDN
export oml_dialer_host=10.10.10.13

# ***********************  WebRTC Bridge VARS
# Values: NULL | IPADDR or FQDN
export oml_rtpengine_host=10.10.10.10


# Tell OMLApp web some params ******************************************************************************
export oml_tz=America/Argentina/Cordoba
# Session Cookie Age (SCA) is the time in seconds that will last the https session when inactivity 
# is detected in the session (by default is 1 hour)                                                
export oml_app_sca=3600
# Ephemeral Credentials TTL (ECTTL) is the time in seconds that will last the SIP credentials      
# used to authenticate a SIP user in the telephony system (by default 8 hours)                     
export oml_app_ecctl=3600
# Login failure limit (LFM) is the attempts a user has to enter an incorrect password in login     
# Decrease it if paranoic reasons                                                                  
export oml_app_login_fail_limit=10

# ************************************************************ SET ENV VARS **********************************************************************
# ************************************************************ SET ENV VARS **********************************************************************

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
SRC=/usr/src

CALLREC_DIR_TMP=/opt/omnileads/callrec_tmp
CALLREC_DIR_DST=/opt/callrec

echo "****************************** IPV4 address config *******************************"
echo "****************************** IPV4 address config *******************************"

case ${oml_infras_stage} in
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
    echo -n "Onpremise Ubuntu Server"
    PRIVATE_IPV4=$(ip addr show ${oml_nic} | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    PUBLIC_IPV4=$(curl ifconfig.co)
    ;;
  vagrant)
    echo -n "Vagrant Ubuntu Server"
    PRIVATE_IPV4=$STAGING_IP_CENTOS
    PUBLIC_IPV4=$(curl ifconfig.co)
    ;;
  *)
    echo -n "you must to declare STAGE variable\n"
    ;;
esac

echo "****************************** omnileads user and workdir *******************************"
echo "****************************** omnileads user and workdir *******************************"

echo "Checking if omnileads user/group exists"
existe=$(grep -c '^omnileads:' /etc/passwd)
if [ $existe -eq 0 ]; then
  echo "Creating omnileads group"
  groupadd omnileads
  echo "Creating omnileads user"
  mkdir -p /opt/omnileads
  useradd omnileads -d /opt/omnileads -s /bin/bash -g omnileads
  chown -R omnileads.omnileads /opt/omnileads
else
  echo "The user/group omnileads already exists"
fi

usermod -aG docker omnileads

echo "****************************** git clone & .env config *******************************"
echo "****************************** git clone & .env config *******************************"

cd /opt/omnileads
git clone $COMPONENT_REPO
cd ominicontacto
git checkout ${oml_app_release}
cd install/docker/prodenv
cp .env.template .env

sed -i "s/DOCKER_IP=X.X.X.X/DOCKER_IP=$PUBLIC_IPV4/g" .env
sed -i "s%\TZ=your_timezone_here%TZ=${oml_tz}%g" .env
sed -i "s/PGPASSWORD=my_very_strong_pass/PGPASSWORD=${oml_pgsql_password}/g" .env

if [ "${oml_app_img}" != "NULL" ]; then
  sed -i "s/^OMLAPP_VERSION=.*/OMLAPP_VERSION=${oml_app_img}/g" .env
fi
if [ "${oml_acd_img}" != "NULL" ]; then
  sed -i "s/^OMLACD_VERSION=.*/OMLACD_VERSION=${oml_acd_img}/g" .env
fi
if [ "${oml_redis_img}" != "NULL" ]; then
  sed -i "s/^REDISGEARS_VERSION=.*/REDISGEARS_VERSION=${oml_redis_img}/g" .env
fi
if [ "${oml_kamailio_img}" != "NULL" ]; then
  sed -i "s/^OMLKAM_VERSION=.*/OMLKAM_VERSION=${oml_kamailio_img}/g" .env
fi
if [ "${oml_nginx_img}" != "NULL" ]; then
  sed -i "s/^OMLNGINX_VERSION=.*/OMLNGINX_VERSION=${oml_nginx_img}/g" .env
fi
if [ "${oml_ws_img}" != "NULL" ]; then
  sed -i "s/^OMLWS_VERSION=.*/OMLWS_VERSION=${oml_ws_img}/g" .env
fi

if [[ "${oml_dialer_host}" != "NULL" ]]; then
  sed -i "s/WOMBAT_HOSTNAME=dialer/WOMBAT_HOSTNAME=${oml_dialer_host}/g" .env
fi
if [[ "${oml_pgsql_host}" != "NULL" ]]; then
  sed -i "s/PGHOST=postgresql/PGHOST=${oml_pgsql_host}/g" .env
else
  echo "[ERROR] you must to have a PGSQL isolate host instance \n"  
  echo "[ERROR] you must to have a PGSQL isolate host instance \n"  
fi  
if [[ "${oml_pgsql_port}" != "NULL" ]]; then
  sed -i "s/PGPORT=5432/PGPORT=${oml_pgsql_port}/g" .env
fi  
if [[ "${oml_rtpengine_host}" != "NULL" ]]; then
  sed -i "s/RTPENGINE_HOSTNAME=rtpengine/RTPENGINE_HOSTNAME=${oml_rtpengine_host}/g" .env
else
  echo "[ERROR] you must to have a RTPENGINE isolate host instance \n"    
  echo "[ERROR] you must to have a RTPENGINE isolate host instance \n"    
fi

if [[ "${oml_pgsql_cloud}" == "NULL" ]]; then
  sed -i "s/PGCLOUD=yes/PGCLOUD=no/g" .env
fi

cp daemon.json /etc/docker
cp omnileads.service /etc/systemd/system/
systemctl daemon-reload
systemctl restart docker

echo "***************************** block_device mount ******************************"
echo "***************************** block_device mount ******************************"
 
case ${oml_callrec_device} in
  s3)
    echo "s3 callrec device \n"
    apt update 
    apt install -y s3fs
    echo "${s3_access_key}:${s3_secret_key} " > ~/.passwd-s3fs
    chmod 600 ~/.passwd-s3fs
       if [ ! -d $CALLREC_DIR_DST ]; then 
      mkdir -p $CALLREC_DIR_DST
      chown -R omnileads. $CALLREC_DIR_DST
    fi  
    echo "${s3_bucket_name}:/${oml_tenant_name} $CALLREC_DIR_DST fuse.s3fs _netdev,allow_other,use_path_request_style,url=${s3url} 0 0" >> /etc/fstab
    mount -a
    ;;
  nfs)
    echo "NFS callrec device \n"
    apt update && apt install -y nfs-common
        if [ ! -d $CALLREC_DIR_DST ]; then 
      mkdir -p $CALLREC_DIR_DST
      chown -R omnileads. $CALLREC_DIR_DST
    fi  
    echo "${nfs_host}:$CALLREC_DIR_TMP $CALLREC_DIR_DST nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab
    mount -a
    ;;
  *)
    echo "callrec on local filesystem \n"
    ;;
 esac

echo "**************************** write callrec files move script ******************************"
echo "**************************** write callrec files move script ******************************"
cat > /opt/omnileads/mover_audios.sh <<'EOF'
#!/bin/bash

# RAMDISK Watcher
#
# Revisa el contenido del ram0 y lo pasa a disco duro
## Variables

Ano=$(date +%Y -d today)
Mes=$(date +%m -d today)
Dia=$(date +%d -d today)
LSOF="/sbin/lsof"
ALMACEN="/opt/callrec/$Ano-$Mes-$Dia"

if [ ! -d $ALMACEN ]; then
  mkdir -p $ALMACEN;
fi

for i in $(ls /opt/omnileads/callrec_tmp/$Ano-$Mes-$Dia/*.wav) ; do
  $LSOF $i &> /dev/null
  valor=$?
  if [ $valor -ne 0 ] ; then
    mv $i $ALMACEN
  fi
done
EOF

chown -R omnileads.omnileads /opt/omnileads/mover_audios.sh
chmod +x /opt/omnileads/mover_audios.sh

echo "****************************** add cron-line to trigger the call-recording move script **************************"
echo "****************************** add cron-line to trigger the call-recording move script **************************"
cat > /etc/cron.d/MoverGrabaciones <<EOF
 */1 * * * * omnileads /opt/omnileads/mover_audios.sh
EOF

echo "****************************** enable and start omnileads *******************************"
echo "****************************** enable and start omnileads *******************************"

mkdir -p /opt/omnileads/callrec_tmp
chown omnileads. -R /opt/omnileads/callrec_tmp

systemctl enable omnileads
systemctl start omnileads

chown omnileads. -R /opt/omnileads


