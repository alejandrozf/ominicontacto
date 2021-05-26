#!/bin/bash
set -e

PACKAGE_VERSION=$(cat ../../.omnileads_version)
docker login -u $DOCKER_USER -p $DOCKER_PASSWORD

case $CI_COMMIT_REF_NAME in
  master)
    docker build -f Dockerfile -t freetechsolutions/omlapp:latest ../..
    docker push freetechsolutions/omlapp:latest
    ;;
  *)
    docker build -f Dockerfile -t freetechsolutions/omlapp:$PACKAGE_VERSION ../..
    docker push freetechsolutions/omlapp:$PACKAGE_VERSION
    ;;
esac
