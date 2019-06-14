#!/bin/bash

#
# Shell script para facilitar el deploy de la aplicación
#
# Autor: Andres Felipe Macias
# Colaborador:  Federico Peker
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
export ANSIBLE_CONFIG=$TMP_ANSIBLE
IS_ANSIBLE="`find ~/.local -name ansible 2>/dev/null |grep \"/bin/ansible\" |head -1`"
SUDO_USER="`who | awk '{print $1}'`"
arg1=$1
arg2=$2
verbose=$3

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
    elif [ "$os" == '"Ubuntu"' ]; then
      echo "Adding the universe repository"
      add-apt-repository universe
      echo "Installing python2 and python-pip"
      apt-get install python-minimal python-pip -y
    else
      echo "The OS you are trying to install is not supported to install this software."
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
  else
    echo "Invalid first option, use ./deploy.sh -h to see valid options"
    exit 1
  fi
}

AnsibleInstall() {
  echo "Detecting if Ansible 2.5 is installed"
  if [ -z "$IS_ANSIBLE" ] ; then
    echo "Ansible 2.5 is not installed"
    echo "Installing Ansible 2.5"
	  echo ""
	  $PIP install 'ansible==2.5' --user
    IS_ANSIBLE="`find ~/.local -name ansible |grep \"/bin/ansible\" |head -1 2> /dev/null`"
	fi
  ANS_VERSION=`"$IS_ANSIBLE" --version |grep ansible |head -1`
	if [ "$ANS_VERSION" = 'ansible 2.5.0' ] ; then
    echo "Ansible is already installed"
  else
    echo "You have an Ansible version different than 2.5.0"
    echo "Installing 2.5.0 version"
    $PIP install 'ansible==2.5' --user
  fi
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
    if ${IS_ANSIBLE} all --list-hosts -i $TMP_ANSIBLE/inventory | grep -q '0'; then
      echo "All hosts in inventory file are commented, please check the file according to documentation"
      exit 1
    fi
    echo "Beginning the Omnileads installation with Ansible, this can take a long time"
    echo ""
    ${IS_ANSIBLE}-playbook $verbose -s $TMP_ANSIBLE/omnileads.yml --extra-vars "build_dir=$TMP_OMINICONTACTO repo_location=$REPO_LOCATION" --tags "$tag" -i $TMP_ANSIBLE/inventory
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
      inventory_copy_location="`cd $current_directory/../../.. && pwd`"
      echo "Creating a copy of inventory file in $inventory_copy_location"
      my_inventory=$current_directory/../../../my_inventory
      cp $current_directory/inventory $my_inventory
      echo "Servers installed:"
      cat /var/tmp/servers_installed
      echo " Remember that you have a copy of your inventory file in $inventory_copy_location/my_inventory with the variables you used for your OML installation"
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
rm -rf $TMP
}
case $arg1 in
  --upgrade|-u|--install|-i|--kamailio|-k|--asterisk|-a|--omniapp|-o|--omnivoip|--dialer|-di|--database|-da|--change-network|-cnet|--change-passwords|-cp)
      UserValidation
      OSValidation
      TagCheck
      AnsibleInstall
      ./keytransfer.sh
      ResultadoKeyTransfer=`echo $?`
        if [ "$ResultadoKeyTransfer" != 0 ]; then
          echo "It seems that you don't have generated keys in the server you are executing this s#cript"
          echo "Try with ssh-keygen or check the ssh port configured in server"
          rm -rf /var/tmp/servers_installed
          exit 1
        fi
      CodeCopy
      VersionGeneration
      AnsibleExec
  ;;
  --docker-build|--docker-deploy)
    UserValidation
    OSValidation
    TagCheck
    AnsibleInstall
    AnsibleExec
  ;;
  *)
  echo "
    Omnileads installation script

    How to use it:
          (First option)
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

          "
  ;;
esac
