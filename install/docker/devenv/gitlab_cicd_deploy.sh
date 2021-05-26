#!/bin/bash

PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
PRIVATE_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
COMPONENT_RELEASE=${omnileads_release}
SRC=/usr/src

cd /tmp
git clone $COMPONENT_REPO
cd ominicontacto
git checkout $COMPONENT_RELEASE

cd install/docker/devenv
cp .env.gitlab .env
sed -i "s/10.10.10.10/$PUBLIC_IPV4/g" .env

bash get_modules.sh True

echo "***[OML devenv] Pulling the latest images of services"
services=("acd" "app" "dialer" "kam" "nginx" "pgsql" "pbxemulator" "websockets")
for i in "${services[@]}"; do
  docker pull freetechsolutions/oml$i:develop
done

docker-compose up -d
docker-compose down
sleep 30
docker-compose up -d
