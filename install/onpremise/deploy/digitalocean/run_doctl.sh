#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
DOCKER=$(which docker)
printf "$GREEN** [OMniLeads] *********************************** $NC\n"
printf "$GREEN** [OMniLeads] Script to run doctl using Docker $NC\n"
printf "$GREEN** [OMniLeads] *********************************** $NC\n"
if [ -z $DOCKER ]; then
  printf "$RED** [OMniLeads] Docker was not found, please install it $NC\n"
fi
printf "$GREEN** [OMniLeads] Pulling the latest image of ansible $NC\n"
docker pull digitalocean/doctl
printf "$GREEN** [OMniLeads] Run and exec the container $NC\n"
docker run -it --rm --name doctl \
  --mount type=bind,source="$(pwd)"/,target=/root/deploy/omnileads_droplet \
  --network=host --workdir=/root/deploy/omnileads_droplet \
  --env=DIGITALOCEAN_ACCESS_TOKEN=------------ \
  digitalocean/doctl $1


  #--mount type=bind,source="$(pwd)"/..,target=/root/ominicontacto \
