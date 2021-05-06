#!/bin/bash

set -e

echo -e "\n"
echo "##################################################################"
echo "##          Welcome to OMniLeads devenv deploy script           ##"
echo "##################################################################"
echo ""

cd ../../../..
echo "***[OML devenv] Cloning the repositories of modules"
repositories=("acd" "kamailio" "nginx" "pgsql" "redis" "rtpengine")
for i in "${repositories[@]}"; do
  if [ ! -d "oml${i}" ]; then
    git clone --branch develop git@gitlab.com:omnileads/oml$i.git
  else
    echo "***[OML devenv] $i repository already cloned"
  fi
done
if [ ! -d "omlwebsockets" ]; then
  echo "***[OML devenv] Cloning the omlwebsockets module"
  git clone --branch develop git@gitlab.com:omnileads/omnileads-websockets.git omlwebsockets
else
  echo "***[OML devenv] omlwebsockets repository already cloned"
fi
echo "***[OML devenv] All repositories were cloned in $(pwd)"
