#!/bin/bash

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
#
# Shell script para facilitar el deploy de la aplicación
#
# Que hace este shell script?
# 1. Instala ansible
# 2. Copia toda la carpeta ansible del repo a /var/tmp/ansible y todo el codigo a /var/tmp/ominicontacto-build
# 3. Pregunta si se quiere dockerizar asterisk o no, para pasarle la variable a ansible.
# 4. Ejecuta ansible segun la opcion de Dockerizar o no
set -e
GREEN='\033[0;32m' # Green
RED='\033[0;31m' # Red
YELLOW='\033[1;33m' # Yellow
NC='\033[0m' # No color
current_directory=`pwd`
PATH=$PATH:~/.local/bin/
ANSIBLE=`which ansible`
TMP_ANSIBLE='/var/tmp/ansible'
TMP_OMINICONTACTO='/var/tmp/ominicontacto-build/ominicontacto'
REPO_LOCATION="`git rev-parse --show-toplevel`"
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
arg1=$1

AnsibleValidation() {
  CertsValidation
  if [ -z $INTERFACE ];then INTERFACE=none;fi
  os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
  if [ "$os" == '"Amazon Linux"' ];then
    echo "Habilitating epel repository"
    amazon-linux-extras enable epel
    echo "Installing python2-pip"
    yum install python-pip patch libedit-devel libuuid-devel -y
  fi
  if [ -z $ANSIBLE ];then
    printf "$RED*** [OMniLeads] Ansible is not installed. Please, install it. $NC\n"
    exit 1
  else
    printf "$GREEN*** [OMniLeads] Ansible is installed. Continuing. $NC\n"
    printf "$GREEN*** [OMniLeads] Loading Ansible environment variables. $NC\n"
    set -o allexport
    source "$current_directory/.env"
    set +o allexport
    printf "$GREEN*** [OMniLeads] Creating Ansible temporal directory. $NC\n"
    if [ -e $TMP_ANSIBLE ];then
      rm -rf $TMP_ANSIBLE
    fi
    mkdir -p /var/tmp/ansible
    sleep 2
    printf "$GREEN*** [OMniLeads] Copying Ansible code to temporal directory. $NC\n"
    cp -a $current_directory/* $TMP_ANSIBLE
    cp -a $current_directory/.env $TMP_ANSIBLE
    cp -a $current_directory/../../../../modules $TMP_ANSIBLE
    if [ "$arg1" == "--exclude-kamailio" ] || [ "$arg1" == "-k" ];then
      rm -rf $TMP_ANSIBLE/modules/kamailio
    fi
    sleep 2
    printf "$GREEN*** [OMniLeads] Creating the installation process log file. $NC\n"
    mkdir -p /var/tmp/log
    touch /var/tmp/log/oml_install
  fi
}

UserValidation() {
  echo -e "\n"
  echo "##########################################################"
  echo "#         Welcome to OMniLeads deployment script         #"
  echo "##########################################################"
  echo ""
  WhoAamI="`whoami`"
  if [ "${WhoAamI}" == "root" ];then
  printf "$GREEN*** [OMniLeads] You have permission to run the script. Continuing. $NC\n"
  else
    printf "$RED*** [OMniLeads] You need to be root or have sudo permission to run this script. Exiting. $NC\n"
    exit 1
  fi
}

TagCheck() {
  if [ "$arg1" == "--asterisk" ] || [ "$arg1" == "-a" ];then
    tag="asterisk"
  elif [ "$arg1" == "--install" ] || [ "$arg1" == "-i" ];then
    tag="all"
  elif [ "$arg1" == "--upgrade" ] || [ "$arg1" == "-u" ];then
    tag="postinstall"
  elif [ "$arg1" == "--kamailio" ] || [ "$arg1" == "-k" ];then
    tag="kamailio"
  elif [ "$arg1" == "--omniapp" ] || [ "$arg1" == "-o" ];then
    tag="omniapp"
  elif [ "$arg1" == "--dialer" ] || [ "$arg1" == "-di" ];then
    tag="dialer"
  elif [ "$arg1" == "--database" ] || [ "$arg1" == "-da" ];then
    tag="database"
  elif [ "$arg1" == "--docker-deploy" ];then
    tag="docker_deploy"
  fi
}

CodeCopy() {
  printf "$GREEN*** [OMniLeads] Getting release data. $NC \n"
  commit="$(git rev-parse HEAD)"
  build_date="$(env LC_hosts=C LC_TIME=C date)"
  current_tag="`git tag -l --points-at HEAD`"
  release_name=$(git show ${current_tag} |grep "Merge branch" |awk -F " " '{print $3}' |tr -d "'")
  branch_name="`git branch | grep \* | cut -d ' ' -f2`"
  if [ $branch_name == "master" ];then git pull;fi
  if [ -z "$current_tag" ];then
    release_name=$branch_name
    if [ ! -z ${DOCKER_TAG} ] && [ "$arg1" == "--docker-deploy" ];then
      release_name=${DOCKER_TAG}
    elif [ -z ${DOCKER_TAG} ] && [ "$arg1" == "--docker-deploy" ];then
      if [[ $release_name == *"pre-release"* ]];then
        release_name=$(echo ${branch_name}|awk -F "-" '{print $1"-"$2"-"$3}')
      else
        release_name=$(echo ${branch_name}|awk -F "-" '{print $1"-"$2}')
      fi
    fi
  fi
  cd ../..
  printf "$GREEN*** [OMniLeads] Checking the release to be installed. $NC\n"
  set -e
  echo ""
  echo "      Version: $release_name"
  echo "      Commit: $commit"
  echo "      Deploy date: $build_date"
  echo ""
  if [ -e $TMP_OMINICONTACTO ];then
    rm -rf $TMP_OMINICONTACTO
  fi
  mkdir -p $TMP_OMINICONTACTO
  printf "$GREEN*** [OMniLeads] Using temporal directory: $TMP_OMINICONTACTO... $NC\n"
  sleep 2
  printf "$GREEN*** [OMniLeads] Copying the OMniLeads code to temporal directory. $NC\n"
  git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP_OMINICONTACTO
  sleep 2
  printf "$GREEN*** [OMniLeads] Deleting unnecesary files. $NC\n"
  rm -rf $TMP_OMINICONTACTO/docs
  rm -rf $TMP_OMINICONTACTO/deploy/ansible
  rm -rf $TMP_OMINICONTACTO/deploy/certs/README.md
  sleep 2
}

CertsValidation() {
  certs_location="$REPO_LOCATION/install/onpremise/deploy/ansible/certs"
  if [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -gt 0 ];then
    if [ $(ls -l $certs_location/*key* 2>/dev/null | wc -l) -eq 1 ] && [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -eq 2 ];then
      if [ ! -f $certs_location/key.pem ];then
        key=$(basename $certs_location/*key*)
        cp $certs_location/$key $certs_location/key.pem
      fi
      if [ ! -f $certs_location/cert.pem ];then
        cert=$(ls $certs_location/*.pem |grep -v key)
        cp $cert $certs_location/cert.pem
      fi
      # Copy user certs to Kamailio and Nginx modules
      cp -f $certs_location/key.pem $REPO_LOCATION/modules/kamailio/deploy/certs/key.pem
      cp -f $certs_location/cert.pem $REPO_LOCATION/modules/kamailio/deploy/certs/cert.pem
      cp -f $certs_location/key.pem $REPO_LOCATION/modules/nginx/deploy/certs/key.pem
      cp -f $certs_location/cert.pem $REPO_LOCATION/modules/nginx/deploy/certs/cert.pem
    else
      printf "$RED*** [OMniLeads] A pair of trusted cert/key pem files weren't found on $REPO_LOCATION/install/onpremise/deploy/ansible/certs. Maybe:
1. You didn't include the string "key" in your .pem file related to private key.
2. You put more or less than two .pem files in the certs folder.
Try removing .pem files from certs location to continue with default certs, or try putting both specific files (key.pem and cert.pem) to continue with your certs.$NC\n"
      exit 1
    fi
  fi
}

AnsibleExec() {
  printf "$GREEN*** [OMniLeads] Checking if there are hosts to deploy from inventory file. $NC\n"
  if ${ANSIBLE} all --list-hosts -i $TMP_ANSIBLE/inventory | grep -q '(0)' 2>/dev/null;then
    printf "$RED*** [OMniLeads] All hosts in inventory file are commented. Please check the file according to documentation. $NC\n"
    exit 1
  fi
  printf "$GREEN*** Beginning the OMniLeads installation process with Ansible. This process will normally take 20-25 minutes, depending on your internet connection. $NC\n"
  echo ""
  if [ "$KEY" != "none" ] && [ ! -z $KEY ];then OPTIONS+="--private-key=$current_directory/$KEY";fi
  ${ANSIBLE}-playbook $verbose $TMP_ANSIBLE/omnileads.yml -b \
    $OPTIONS \
    --extra-vars "iface=$INTERFACE \
                  build_dir=$TMP_OMINICONTACTO \
                  repo_location=$REPO_LOCATION \
                  docker_root=$USER_HOME \
                  build_images=$BUILD_IMAGES \
                  oml_release=$release_name \
                  commit=$commit \
                  build_date=\"$build_date\"" \
    --tags "$tag" -i $TMP_ANSIBLE/inventory
  ResultadoAnsible=`echo $?`
  if [ $ResultadoAnsible == 0 ];then
    echo "
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@/@/@////@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@/@@@/@@@/@@@@@@@/@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@
  @@@@@@/@@@/@@@/@@@@@@@/@@@@/@@@@@@@//@@@@@/@@@///@@@@@&//@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/@@@@@@@@@@@@@
  @@@@@@@@/@/@@@&/@@//@@@(@/@@@@@@@@/@@@@@@@@/@@////@@@@/@/@@@//@@@/@@@/@@@/@@@@@@@//@@@/@@@/@@@/@@@//@@@///@@/@@@/@@@@@@
  @@@@@@@@/@@/&//%//@/@//@@/@@@@@@@@/@@@@@@@@/%@//@//@@/@@/@@@/@@@@//@@/@@@/@@@@@@/@@@//@@@@@/////@/@@@@@@#/@@///@@@@@@@@
  @@@@@@@////@/@@////@@/@///@@@@@@@@//@@@@@@//@@//@@/@/@@@/@@@/@@@@//@@/@@@/@@@@@@///@@@@/@/@@@@@/@@/@@@@@//@@@@@@/@@@@@@
  @@@@@@/@@@//@//@@@@/@@/@@@@/@@@@@@@@//////@@@@//@@@/@@@@/@@@/@@@@//@@/@@@///////@@////@@@@////@/@@@/////@/@@/////@@@@@@
  @@@@@@/@@@//@@@@@@/@@@//@@/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@//@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@/@@@@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                                          The Open Source Contact Center Solution
                                           Copyright (C) 2018 Freetech Solutions"
    echo ""
    echo "#############################################################"
    echo "#         OMniLeads installation ended successfully         #"
    echo "#############################################################"
    echo ""
    git checkout $current_directory/inventory
    chown $SUDO_USER. $current_directory/inventory
  else
    echo ""
    echo "#######################################################################################"
    echo "#         OMniLeads installation failed. Check what happened and try it again         #"
    echo "#######################################################################################"
    echo ""
  fi

  printf "$GREEN*** [OMniLeads] Deleting temporal files created. $NC\n"
  rm -rf $TMP_ANSIBLE
  rm -rf $TMP_OMINICONTACTO
  if [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -eq 4 ];then
    rm -rf $certs_location/key.pem $certs_location/cert.pem
  fi
}

for i in "$@"
do
  case $i in
    --upgrade|-u|--install|-i|--exclude-kamailio|-k|--asterisk|-a|--omniapp|-o|--omnivoip|--dialer|-di|--database|-da|--change-network|-cnet|--change-passwords|-cp|--docker-no-build|--docker-build|--docker-deploy)
      TagCheck
      shift
    ;;
    --iface=*|--interface=*)
      INTERFACE="${i#*=}"
      KEY="none"
      shift
    ;;
    --key=*)
      INTERFACE="none"
      KEY="${i#*=}"
      shift
    ;;
    --docker-tag=*)
      DOCKER_TAG="${i#*=}"
      shift
    ;;
    --help|-h)
      echo "
        OMniLeads installation script
        -----------------------------
        How to use it:
              -a, --asterisk: Execute Asterisk related tasks.
              -da, --database: Execute database related tasks.
              -di, --dialer: Execute dialer (WombatDialer) related tasks.
              --docker-deploy: Deploy OMniLeads in docker containers, using docker-compose.
              --docker-build: Build and push OMniLeads images to a registry.
              --docker-no-build: Execute build images steps, without building and pushing the images.
              -i, --install: Perform a fresh install of OMniLeads.
              -k, --kamailio: Execute Kamailio related tasks.
              -o, --omniapp: Execute OmniApp related tasks.
              -u, --upgrade: Execute an upgrade of OMniLeads version.
              --iface, --interface: Set the specific interface where OMniLeads services will be listening (USE THIS OPTION ONLY WHEN INSTALLATION IS SELFHOSTED).
              --key: Set the public key to connect to the OMniLeads instance using SSH, without authentication.
            "
      shift
      exit 1
    ;;
    -v*)
      verbose=$1
      shift
    ;;
    *)
      echo "One or more invalid options. For more information, execute: ./deploy.sh -h or ./deploy.sh --help."
      exit 1
    ;;
  esac
done
./keytransfer.sh $INTERFACE $KEY
ResultadoKeyTransfer=`echo $?`
  if [ "$ResultadoKeyTransfer" == 1 ]; then
    printf "$YELLOW It seems that there was a problem transfering yout public key to OMniLeads instance, it could because: $NC\n"
    printf "$YELLOW 1. You don't have generated keys in the server you are executing this script. Try with ssh-keygen or check the ssh port configured in server $NC\n"
    printf "$YELLOW 2. You need a private key identity file to connect to SSH to OMniLeads instance, place the key in the same folder of this script. $NC\n"
    rm -rf /var/tmp/servers_installed
    exit 1
  elif [ "$ResultadoKeyTransfer" == 2 ]; then
    echo "#######################################################################"
    echo "# The option --interface must be used only in selfhosted installation #"
    echo "#######################################################################"
    exit 1
  elif [ "$ResultadoKeyTransfer" == 3 ]; then
    echo "#######################################"
    echo "# Option --interface must be provided #"
    echo "#######################################"
    exit 1
  elif [ "$ResultadoKeyTransfer" == 4 ]; then
    echo "##############################################################"
    echo "# It seems you typed a wrong interface in --interface option #"
    echo "##############################################################"
    exit 1
  fi
UserValidation
AnsibleValidation
CodeCopy
AnsibleExec
