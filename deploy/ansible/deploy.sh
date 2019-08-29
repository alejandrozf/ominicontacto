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
current_directory=`pwd`
PIP=`which pip`
TMP_ANSIBLE='/var/tmp/ansible'
TMP_OMINICONTACTO='/var/tmp/ominicontacto-build/ominicontacto'
REPO_LOCATION="`git rev-parse --show-toplevel`"
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
DEBIAN_FRONTEND=noninteractive
IS_ANSIBLE="`find ~/.local -name ansible 2>/dev/null |grep \"/bin/ansible\" |head -1`"
arg1=$1

OSValidation(){
  if [ -z $PIP ]; then
    os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
    if [ "$os" == '"CentOS Linux"' ]; then
      echo "Downloading and installing epel-release repository"
      yum install epel-release -y
      echo "Installing python2-pip"
      yum install python2-pip -y
    elif [ "$os" == '"Debian GNU/Linux"' ]; then
      echo "Installing python2-pip and sudo"
      apt-get install python-pip sudo -y
      apt-get remove python-cryptography -y
    elif [ "$os" == '"Ubuntu"' ]; then
      echo "Adding the universe repository"
      add-apt-repository universe
      echo "Installing python2 and python-pip"
      apt-get install python-minimal python-pip -y
    else
      echo "The OS you are trying to install is not supported to install this software."
      exit 1
    fi
  PIP=`which pip`
  fi
}

UserValidation(){
  echo -e "\n"
  echo "###############################################################"
  echo "##          Welcome to omnileads deployment script           ##"
  echo "###############################################################"
  echo ""
  whoami="`whoami`"
  if [ "$whoami" == "root" ]; then
    echo "You have the permise to run the script, continue"
  else
    echo "You need to be root or have sudo permission to run this script, exiting"
    exit 1
  fi
}

TagCheck() {
  if [ "$arg1" == "--asterisk" ] || [ "$arg1" == "-a" ]; then
    tag="asterisk"
  elif [ "$arg1" == "--install" ] || [ "$arg1" == "-i" ]; then
    tag="all"
  elif [ "$arg1" == "--upgrade" ] || [ "$arg1" == "-u" ]; then
    tag="postinstall"
  elif [ "$arg1" == "--kamailio" ] || [ "$arg1" == "-k" ]; then
    tag="kamailio"
  elif [ "$arg1" == "--omniapp" ] || [ "$arg1" == "-o" ]; then
    tag="omniapp"
  elif [ "$arg1" == "--change-network" ] || [ "$arg1" == "-cnet" ]; then
    tag="changenetwork"
  elif [ "$arg1" == "--change-passwords" ] || [ "$arg1" == "-cp" ]; then
    tag="changepassword"
  elif [ "$arg1" == "--dialer" ] || [ "$arg1" == "-di" ]; then
    tag="dialer"
  elif [ "$arg1" == "--database" ] || [ "$arg1" == "-da" ]; then
    tag="database"
  elif [ "$arg1" == "--docker-build" ]; then
    tag="docker_build"
  elif [ "$arg1" == "--docker-deploy" ]; then
    tag="docker_deploy"
  elif [ "$arg1" == "--integration-tests" ]; then
    tag="all,integration-tests"
  fi
}

AnsibleInstall() {
  echo "Detecting if Ansible 2.5 is installed"
  if [ -z "$IS_ANSIBLE" ] ; then
    echo "Ansible 2.5 is not installed, installing it"
    echo ""
    $PIP install 'ansible==2.5' --user
    IS_ANSIBLE="`find ~/.local -name ansible |grep \"/bin/ansible\" |head -1 2> /dev/null`"
  else
    echo "Ansible 2.5 is already installed"
  fi
  #  echo "Detecting if docker-py is installed"
  #  $PIP install 'docker-py==1.10.6' --user > /dev/null 2>&1
  cd $current_directory
  sleep 2
  echo "Creating ansible temporal directory"
  if [ -e $TMP_ANSIBLE ]; then
    rm -rf $TMP_ANSIBLE
  fi
  mkdir -p /var/tmp/ansible
  sleep 2
  echo "Copying ansible code to temporal directory"
  cp -a $current_directory/* $TMP_ANSIBLE
  sleep 2
  echo "Creating the installation process log file"
  mkdir -p /var/tmp/log
  touch /var/tmp/log/oml_install
}

CodeCopy() {
  current_tag="`git tag -l --points-at HEAD`"
  release_name="`git show ${current_tag} | awk 'FNR == 5 {print}'`"
  branch_name="`git branch | grep \* | cut -d ' ' -f2`"
  if [ -z "$current_tag" ]
  then
      release_name=$branch_name
  fi
  cd ../..
  echo "Checking the release to install"
  set -e
  echo ""
  echo "      Version: $release_name"
  echo ""
  if [ -e $TMP_OMINICONTACTO ] ; then
    rm -rf $TMP
  fi
  mkdir -p $TMP_OMINICONTACTO
  echo "Using temporal directory: $TMP_OMINICONTACTO..."
  sleep 2
  echo "Copying the Omnileads code to temporal directory"
  git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP_OMINICONTACTO
  sleep 2
  echo "Deleting unnecesary files..."
  rm -rf $TMP_OMINICONTACTO/docs
  rm -rf $TMP_OMINICONTACTO/ansible
  sleep 2
}

VersionGeneration() {
  echo "Getting release data..."
  commit="$(git rev-parse HEAD)"
  author="$(id -un)@$(hostname)"
  echo -e "Creating version file
     Branch: $release_name
     Commit: $commit
     Autor: $author"
  cat > $TMP_OMINICONTACTO/ominicontacto_app/version.py <<EOF

# -*- coding: utf-8 -*-

##############################
#### Archivo autogenerado ####
##############################

OML_BRANCH="${release_name}"
OML_COMMIT="${commit}"
OML_BUILD_DATE="$(env LC_hosts=C LC_TIME=C date)"
OML_AUTHOR="${author}"

if __name__ == '__main__':
    print OML_COMMIT

EOF

  #echo "Validando version.py - Commit:"
  python $TMP_OMINICONTACTO/ominicontacto_app/version.py > /dev/null 2>&1
  # ----------
  export DO_CHECKS="${DO_CHECKS:-no}"
}

AnsibleExec() {
    echo "Checking if there are hosts to deploy from inventory file"
    if ${IS_ANSIBLE} all --list-hosts -i $TMP_ANSIBLE/inventory | grep -q '(0)'; then
      echo "All hosts in inventory file are commented, please check the file according to documentation"
      exit 1
    fi
    echo "Beginning the Omnileads installation with Ansible, this installation process can last between 30-40 minutes"
    echo ""
    ${IS_ANSIBLE}-playbook $verbose -s $TMP_ANSIBLE/omnileads.yml --extra-vars "iface=$INTERFACE build_dir=$TMP_OMINICONTACTO repo_location=$REPO_LOCATION docker_root=$USER_HOME" --tags "$tag" -i $TMP_ANSIBLE/inventory
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
      echo "###############################################################"
      echo "##          Omnileads installation ended successfully        ##"
      echo "###############################################################"
      echo ""
      git checkout $current_directory/inventory
      chown $SUDO_USER. $current_directory/inventory
    else
      echo ""
      echo "###################################################################################"
      echo "##        Omnileads installation failed, check what happened and try again       ##"
      echo "###################################################################################"
      echo ""
    fi

echo "Deleting temporal files created"
rm -rf $TMP_ANSIBLE
rm -rf $TMP_OMINICONTACTO
}
UserValidation
OSValidation
for i in "$@"
do
  case $i in
    --upgrade|-u|--install|-i|--kamailio|-k|--asterisk|-a|--omniapp|-o|--omnivoip|--dialer|-di|--database|-da|--change-network|-cnet|--change-passwords|-cp|--docker-build|--docker-deploy|--integration-tests)
      TagCheck
      shift
    ;;
    --iface=*|--interface=*)
      INTERFACE="${i#*=}"
      shift
    ;;
    --help|-h)
      echo "
        Omnileads installation script
        How to use it:
              -a --asterisk: execute asterisk related tasks
              -cnet --change-network: execute tasks needed when you change the network settings of OML system
              -cp --change-passwords: execute tasks needed when you change any of the passwords of your OML system
              -da --database: execute tasks related to database
              -di --dialer: execute tasks related to dialer (Wombat Dialer)
              --docker-deploy: deploy Omnileads in docker containers using docker-compose. See /deploy/docker/README.md
              --docker-build: build Omnileads images. See /deploy/docker/CONTRIBUTING.md
              -i --install: make a fresh install of Omnileads
              -k --kamailio: execute kamailio related tasks
              -o --omniapp: execute omniapp related tasks
              -u --upgrade: make an upgrade of Omnileads version
              --iface --interface: set the iface when you want omnileads services listening (JUST USE THIS OPTION WHEN INSTALLATION IS SELFHOSTED)
            "
      shift
      exit 1
    ;;
    -v*)
      verbose=$1
      shift
    ;;
    *)
      echo "One or more invalid options, use ./deploy.sh -h or ./deploy.sh --help"
      exit 1
    ;;
  esac
done
./keytransfer.sh $INTERFACE
ResultadoKeyTransfer=`echo $?`
  if [ "$ResultadoKeyTransfer" == 1 ]; then
    echo "It seems that you don't have generated keys in the server you are executing this script"
    echo "Try with ssh-keygen or check the ssh port configured in server"
    rm -rf /var/tmp/servers_installed
    exit 1
  elif [ "$ResultadoKeyTransfer" == 2 ]; then
    echo "#######################################################################"
    echo "# The option --interface must be used only in selfhosted installation #"
    echo "#######################################################################"
    exit 1
  elif [ "$ResultadoKeyTransfer" == 3 ]; then
    echo "#####################################"
    echo "# Option --interface must be passed #"
    echo "#####################################"
    exit 1
  elif [ "$ResultadoKeyTransfer" == 4 ]; then
    echo "###############################################################"
    echo "# It seems you typed a wrong interface in --interface option  #"
    echo "###############################################################"
    exit 1
  fi
AnsibleInstall
CodeCopy
VersionGeneration
AnsibleExec
