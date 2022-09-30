#!/bin/bash

set -e

echo -e "\n"
echo "##################################################################"
echo "##          Welcome to OMniLeads devenv deploy script           ##"
echo "##################################################################"
echo ""

CICD=$1



cd ../../../..
echo "***[OML devenv] Cloning the repositories of modules"
repositories=("acd" "kamailio" "nginx" "pgsql" "redis" "rtpengine" "hap")
for i in "${repositories[@]}"; do
  if [ ! -d "oml${i}" ]; then
    if [ "$CICD" == "True" ]; then
      git clone https://gitlab.com/omnileads/oml$i.git
    else
      git clone git@gitlab.com:omnileads/oml$i.git
    fi
  else
    echo "***[OML devenv] $i repository already cloned"
  fi
done
if [ ! -d "omlwebsockets" ]; then
  echo "***[OML devenv] Cloning the omlwebsockets module"
  if [ "$CICD" == "True" ]; then
    git clone \
    https://gitlab.com/omnileads/omnileads-websockets.git omlwebsockets
  else
    git clone \
    git@gitlab.com:omnileads/omnileads-websockets.git omlwebsockets
  fi
else
  echo "***[OML devenv] omlwebsockets repository already cloned"
fi
echo "***[OML devenv] All repositories were cloned in $(pwd)"
