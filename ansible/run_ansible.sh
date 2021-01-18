#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
DOCKER=$(which docker)
printf "$GREEN** [OMniLeads] *********************************** $NC\n"
printf "$GREEN** [OMniLeads] Script to run ansible using Docker $NC\n"
printf "$GREEN** [OMniLeads] *********************************** $NC\n"
if [ -z $DOCKER ]; then
  printf "$RED** [OMniLeads] Docker was not found, please install it $NC\n"
fi
printf "$GREEN** [OMniLeads] Pulling the latest image of ansible $NC\n"
docker pull freetechsolutions/ansible:latest

printf "$GREEN** [OMniLeads] Run and exec the container $NC\n"
docker run -it --rm --name ansible \
  --mount type=bind,source="$(pwd)"/..,target=/root/ominicontacto \
  --env-file .env \
  --network=host --workdir=/root/ominicontacto \
  freetechsolutions/ansible:latest bash
