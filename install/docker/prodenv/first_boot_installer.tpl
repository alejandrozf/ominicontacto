#!/bin/bash

PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
PRIVATE_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
COMPONENT_RELEASE=${omnileads_release}
SRC=/usr/src

TZ=${TZ}
sca=${sca}
ami_user=${ami_user}
ami_password=${ami_password}
dialer_user=${dialer_user}
dialer_password=${dialer_password}
pg_database=${pg_database}
pg_username=${pg_username}
pg_password=${pg_password}
extern_ip=none

PG_HOST=${pg_host}
PG_PORT=${pg_port}
RTPENGINE_HOST=${rtpengine_host}
DIALER_HOST=${dialer_host}
MYSQL_HOST=${mysql_host}

OMLAPP_VERSION=${omlapp_version}
OMLACD_VERSION=${omlacd_version}
OMLWS_VERSION=${omlws_version}
OMLREDIS_VERSION=${omlredis_version}
OMLNGINX_VERSION=${omlnginx_version}
OMLKAM_VERSION=${omlkam_version}

ENVIRONMENT_INIT=${init_env}

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

cd /opt/omnileads
git clone $COMPONENT_REPO
cd ominicontacto
git checkout $COMPONENT_RELEASE
cd install/docker/prodenv
cp .env.template .env

sed -i "s/DOCKER_IP=X.X.X.X/DOCKER_IP=$PUBLIC_IPV4/g" .env
sed -i "s/TZ=your_timezone_here/TZ=America\/Argentina\/Cordoba/g" .env
sed -i "s/PGPASSWORD=my_very_strong_pass/PGPASSWORD=$pg_password/g" .env

if [ "$OMLAPP_VERSION" != "" ]; then
  sed -i "s/^OMLAPP_VERSION=.*/OMLAPP_VERSION=$OMLAPP_VERSION/g" .env
else
  OMLAPP_VERSION=$(cat ../../../.omnileads_version)
  sed -i "s/^OMLAPP_VERSION=.*/OMLAPP_VERSION=$OMLAPP_VERSION/g" .env
fi
if [ "$OMLACD_VERSION" != "" ]; then
  sed -i "s/^OMLACD_VERSION=.*/OMLACD_VERSION=$OMLACD_VERSION/g" .env
fi
if [ "$OMLREDIS_VERSION" != "" ]; then
  sed -i "s/^OMLREDIS_VERSION=.*/OMLREDIS_VERSION=$OMLREDIS_VERSION/g" .env
fi
if [ "$OMLKAM_VERSION" != "" ]; then
  sed -i "s/^OMLKAM_VERSION=.*/OMLKAM_VERSION=$OMLKAM_VERSION/g" .env
fi
if [ "$OMLNGINX_VERSION" != "" ]; then
  sed -i "s/^OMLNGINX_VERSION=.*/OMLNGINX_VERSION=$OMLNGINX_VERSION/g" .env
fi
if [ "$OMLWS_VERSION" != "" ]; then
  sed -i "s/^OMLWS_VERSION=.*/OMLWS_VERSION=$OMLWS_VERSION/g" .env
fi

if [[ "$DIALER_HOST" != "NULL" ]]; then
  sed -i "s/WOMBAT_HOSTNAME=dialer/WOMBAT_HOSTNAME=$DIALER_HOST/g" .env
fi
if [[ "$PG_HOST" == "NULL" ]]; then
  sed -i "s/PGHOST=postgresql/PGHOST=$PRIVATE_IPV4/g" .env
else
  sed -i "s/PGHOST=postgresql/PGHOST=$PG_HOST/g" .env
fi
if [[ "$RTPENGINE_HOST" == "NULL" ]]; then
  sed -i "s/RTPENGINE_HOSTNAME=rtpengine/RTPENGINE_HOSTNAME=$PRIVATE_IPV4/g" .env
else
  sed -i "s/RTPENGINE_HOSTNAME=rtpengine/RTPENGINE_HOSTNAME=$RTPENGINE_HOST/g" .env
fi

cp daemon.json /etc/docker
cp omnileads.service /etc/systemd/system/

systemctl restart docker
systemctl daemon-reload
systemctl enable omnileads
systemctl start omnileads

chown omnileads. -R /opt/omnileads
