#!/bin/bash

set -e

cp -a ../../../requirements/ .
docker build -t freetechsolutions/omlapp-builder:$1 .
if [ ! -z $DOCKER_USER ] && [ ! -z $DOCKER_PASSWORD ]; then
  docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
  docker push freetechsolutions/omlapp-builder:$1
fi
rm -rf requirements.txt
