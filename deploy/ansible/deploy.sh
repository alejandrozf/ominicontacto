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
PATH=$PATH:~/.local/bin/
PIP=`which pip`
ANSIBLE=`which ansible`
TMP_ANSIBLE='/var/tmp/ansible'
TMP_OMINICONTACTO='/var/tmp/ominicontacto-build/ominicontacto'
ANSIBLE_VERSION_DESIRED='2.9.2'
ANSIBLE_VERSION_INSTALLED="`~/.local/bin/ansible --version |head -1| awk -F ' ' '{print $2}'`"
REPO_LOCATION="`git rev-parse --show-toplevel`"
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
arg1=$1

OSValidation(){
  if [ -z $PIP ]; then
    os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
    if [ "$os" == '"CentOS Linux"' ] || [ "$os" == '"Issabel PBX"' ] || [ "$os" == '"Sangoma Linux"' ]; then
      echo "Downloading and installing epel-release repository"
      yum install epel-release -y
      echo "Installing python2-pip"
      yum install python-pip -y
      echo
    elif [ "$os" == '"Amazon Linux"' ]; then
      echo "Habilitating epel repository"
      amazon-linux-extras enable epel
      echo "Installing python2-pip"
      yum install python-pip patch libedit-devel libuuid-devel -y
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
  elif [ "$arg1" == "--dialer" ] || [ "$arg1" == "-di" ]; then
    tag="dialer"
  elif [ "$arg1" == "--database" ] || [ "$arg1" == "-da" ]; then
    tag="database"
  elif [ "$arg1" == "--docker-build" ]; then
    tag="docker_build"
    BUILD_IMAGES=true
  elif [ "$arg1" == "--docker-deploy" ]; then
    tag="docker_deploy"
  elif [ "$arg1" == "--integration-tests" ]; then
    tag="all,integration-tests"
  elif [ "$arg1" == "--docker-no-build" ]; then
    tag="docker_build"
    BUILD_IMAGES=false
  fi
}

AnsibleInstall() {
  echo "Detecting if Ansible $ANSIBLE_VERSION_DESIRED is installed"
  if [ -z "$ANSIBLE" ] || [ "$ANSIBLE_VERSION_INSTALLED" != "$ANSIBLE_VERSION_DESIRED" ]; then
    echo "Ansible $ANSIBLE_VERSION_DESIRED is not installed, installing it"
    echo ""
    $PIP install "ansible==$ANSIBLE_VERSION_DESIRED" --user
    ANSIBLE="`find ~/.local -name ansible |grep \"/bin/ansible\" |head -1 2> /dev/null`"
  else
    echo "Ansible $ANSIBLE_VERSION_DESIRED is already installed"
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
  release_name=$(git show ${current_tag} |grep "Merge branch" |awk -F " " '{print $3}' |tr -d "'")
  branch_name="`git branch | grep \* | cut -d ' ' -f2`"
  if [ $branch_name == "master" ]; then git pull; fi
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
    rm -rf $TMP_OMINICONTACTO
  fi
  mkdir -p $TMP_OMINICONTACTO
  echo "Using temporal directory: $TMP_OMINICONTACTO..."
  sleep 2
  echo "Copying the Omnileads code to temporal directory"
  git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP_OMINICONTACTO
  sleep 2
  CertsValidation
  echo "Deleting unnecesary files..."
  rm -rf $TMP_OMINICONTACTO/docs
  rm -rf $TMP_OMINICONTACTO/deploy/ansible
  rm -rf $TMP_OMINICONTACTO/deploy/certs/README.md
  sleep 2
}

CertsValidation() {
  echo "Checking if you put trusted key/cert pair under deploy/certs folder"
  certs_location="$REPO_LOCATION/deploy/certs"
  if [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -gt 0 ]; then
    TRUSTED_CERTS=true
    if [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -eq 4 ]; then
      rm -rf $certs_location/key.pem $certs_location/cert.pem
    fi
    if [ $(ls -l $certs_location/*key* 2>/dev/null | wc -l) -eq 1 ] && [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -eq 2 ]; then
      if [ ! -f $certs_location/key.pem ]; then
        key=$( basename $certs_location/*key*)
        cp $certs_location/$key $certs_location/key.pem
      fi
      if [ ! -f $certs_location/cert.pem ]; then
        cert=$(ls $certs_location/*.pem |grep -v key)
        cp $cert $certs_location/cert.pem
      fi
    else
      echo "A pair of trusted cert/key pem files weren't recognized in {{ repo_location }}/deploy/certs, maybe:
        1. You didn't include the string "key" in you .pem file related to private key
        2. You put more than two .pem files in the certs folder"; exit 1
    fi
  else
    TRUSTED_CERTS=false
  fi
}

VersionGeneration() {
  echo "Getting release data..."
  commit="$(git rev-parse HEAD)"
  build_date="$(env LC_hosts=C LC_TIME=C date)"
  echo -e "OMniLeads version to install
     Branch: $release_name
     Commit: $commit
     Build date: $build_date"
}

AnsibleExec() {
    if [ -z $INTERFACE ]; then INTERFACE=none; fi
    echo "Checking if there are hosts to deploy from inventory file"
    if ${ANSIBLE} all --list-hosts -i $TMP_ANSIBLE/inventory | grep -q '(0)' 2>/dev/null; then
      echo "All hosts in inventory file are commented, please check the file according to documentation"
      exit 1
    fi
    echo "Beginning the Omnileads installation with Ansible, this installation process can last between 20-25 minutes, depending of your internet connection"
    echo ""
    ${ANSIBLE}-playbook $verbose $TMP_ANSIBLE/omnileads.yml \
      --extra-vars "trusted_certs=$TRUSTED_CERTS \
                    iface=$INTERFACE \
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
if [ $(ls -l $certs_location/*.pem 2>/dev/null | wc -l) -eq 4 ]; then
  rm -rf $certs_location/key.pem $certs_location/cert.pem
fi
}
UserValidation
OSValidation
for i in "$@"
do
  case $i in
    --upgrade|-u|--install|-i|--kamailio|-k|--asterisk|-a|--omniapp|-o|--omnivoip|--dialer|-di|--database|-da|--change-network|-cnet|--change-passwords|-cp|--docker-no-build|--docker-build|--docker-deploy|--integration-tests)
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
              -da --database: execute tasks related to database
              -di --dialer: execute tasks related to dialer (Wombat Dialer)
              --docker-deploy: deploy Omnileads in docker containers using docker-compose.
              --docker-build: build and push Omnileads images to a registry.
              --docker-no-build: execute build images steps without building and pushing the images.
              -i --install: make a fresh install of Omnileads.
              -k --kamailio: execute kamailio related tasks.
              -o --omniapp: execute omniapp related tasks.
              -u --upgrade: make an upgrade of Omnileads version.
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
if [ "$arg1" == "--docker-build" ] || [ "$arg1" == "--docker-no-build" ]; then
  echo ""
else
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
fi
AnsibleInstall
CodeCopy
VersionGeneration
AnsibleExec
