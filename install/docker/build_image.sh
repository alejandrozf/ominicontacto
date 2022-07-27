#!/bin/bash
set -e

#PACKAGE_VERSION=$(cat ../../.omnileads_version)
#docker login -u $DOCKER_USER -p $DOCKER_PASSWORD

case $CI_COMMIT_REF_NAME in
  master)
    docker build -f Dockerfile -t freetechsolutions/omlapp:latest ../..
    docker push freetechsolutions/omlapp:latest
    ;;
  develop)
    docker build -f Dockerfile -t freetechsolutions/omlapp:develop ../..
    docker push freetechsolutions/omlapp:develop
    ;;
  *)
    docker build -f Dockerfile -t freetechsolutions/omlapp:$1 ../..
    docker push freetechsolutions/omlapp:$1
    ;;
esac
