#!/bin/bash
set -e

PACKAGE_VERSION=$(cat ../../.omnileads_version)
docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
if [ $CI_COMMIT_REF_NAME == "master" ]; then
  docker build -f Dockerfile -t freetechsolutions/omlapp:latest ../..
  docker push freetechsolutions/omlapp:latest
fi
docker build -f Dockerfile -t freetechsolutions/omlapp:$PACKAGE_VERSION ../..
docker push freetechsolutions/omlapp:$PACKAGE_VERSION
docker build -f Dockerfile -t freetechsolutions/omlapp:develop ../..
docker push freetechsolutions/omlapp:develop
