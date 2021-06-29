#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
DOCKER=$(which docker)
printf "$GREEN** [OMniLeads] *********************************************** $NC\n"
printf "$GREEN** [OMniLeads] Script to run fpm container using Docker $NC\n"
printf "$GREEN** [OMniLeads] *********************************************** $NC\n"
if [ -z $DOCKER ]; then
  printf "$RED** [OMniLeads] Docker was not found, please install it $NC\n"
fi
printf "$GREEN** [OMniLeads] Pulling the latest image of fpm $NC\n"
docker pull freetechsolutions/fpm-ansible:latest

printf "$GREEN** [OMniLeads] Run and exec the container $NC\n"
docker run -it --rm --name omnileads-fpm \
  --mount type=bind,source="$(pwd)"/../../../..,target=/builds/omnileads/ominicontacto \
  --env-file .env \
  --network=host --workdir=/builds/omnileads/ominicontacto \
  freetechsolutions/fpm-ansible:latest bash
