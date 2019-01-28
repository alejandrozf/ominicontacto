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
TMP_ANSIBLE='/var/tmp/ansible'
export ANSIBLE_CONFIG=$TMP_ANSIBLE
IS_ANSIBLE="`find ~/.local -name ansible 2>/dev/null |grep \"/bin/ansible\" |head -1`"
DESARROLLO=0
arg1=$1
arg2=$2
desarrollo=$3
verbose=$4

OSValidation(){
  os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
  if [ "$os" == '"CentOS Linux"' ]; then
    echo "Downloading and installing epel-release repository"
    yum install epel-release -y
    echo "Installing python2-pip"
    yum install python2-pip -y
  elif [ "$os" == '"Debian GNU/Linux"' ]; then
    echo "Installing python2-pip and sudo"
    apt-get install python-pip sudo -y
  fi
  PIP=`which pip`
}

Rama() {
    if [ "$arg1" == "--install" ] || [ "$arg1" == "-i" ]; then
      tag="all"
    elif [ "$arg1" == "--upgrade" ] || [ "$arg1" == "-u" ]; then
      tag="postinstall"
    else
      tag=$arg1
    fi
    echo -e "\n"
    echo "###############################################################"
    echo "##          Welcome to omnileads deployment script           ##"
    echo "###############################################################"
    echo ""
    OSValidation
    sleep 2
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
    #sleep 2
    branch_name="`git branch | grep \* | cut -d ' ' -f2`"
    cd ../..
    echo "Checking the release to install"
    set -e
    echo ""
    echo "      Version: $branch_name"
    echo ""
    TMP=/var/tmp/ominicontacto-build
    if [ -e $TMP ] ; then
        rm -rf $TMP
    fi
    mkdir -p $TMP/ominicontacto
    echo "Using temporal directory: $TMP/ominicontacto..."
    sleep 2
    echo "Copying the Omnileads code to temporal directory"
    git archive --format=tar $(git rev-parse HEAD) | tar x -f - -C $TMP/ominicontacto
    sleep 2
    echo "Deleting unnecesary files..."
    rm -rf $TMP/ominicontacto/docs
    rm -rf $TMP/ominicontacto/ansible
    sleep 2
    echo "Getting release data..."
    commit="$(git rev-parse HEAD)"
    author="$(id -un)@$(hostname)"
    echo -e "Creating version file
       Branch: $branch_name
       Commit: $commit
       Autor: $author"
    cat > $TMP/ominicontacto/ominicontacto_app/version.py <<EOF

# -*- coding: utf-8 -*-

##############################
#### Archivo autogenerado ####
##############################

OML_BRANCH="${branch_name}"
OML_COMMIT="${commit}"
OML_BUILD_DATE="$(env LC_hosts=C LC_TIME=C date)"
OML_AUTHOR="${author}"

if __name__ == '__main__':
    print OML_COMMIT

EOF

    #echo "Validando version.py - Commit:"
    python $TMP/ominicontacto/ominicontacto_app/version.py > /dev/null 2>&1

    # ----------
    export DO_CHECKS="${DO_CHECKS:-no}"
    if [ -z $desarrollo ] && ([ "$arg1" == "--install" ] || [ "$arg1" == "-i" ]); then
      echo "Do you want to install dahdi linux driver? (type yes or no)"; read dahdi_install
      if [ "$dahdi_install" == "yes" ] && ( [ "$arg1" == "--install" ] || [ "$arg1" == "-i" ]); then
        sed -i "s/\(^dahdi_install\).*/dahdi_install: 1/" $TMP_ANSIBLE/group_vars/all
      elif [ "$dahdi_install" == "no" ]; then
        echo ""
      else
        echo "Wrong, type yes or no, exiting"
        exit 1
      fi
    fi
}

Desarrollo() {
    echo ""
    echo "#############################################################################"
    echo "##   You chose -d option, that means you are installing a develop server   ##"
    echo "#############################################################################"
    echo ""
    sed -i "s/\(^desarrollo\).*/desarrollo: 1/" $TMP_ANSIBLE/group_vars/all
    DESARROLLO=1
}

Tag() {
    echo "Beginning the Omnileads installation with Ansible, this can take a long time"
    echo ""
    if [ $CLUSTER -eq 1 ]; then
      sed -i "s/\(^cluster\).*/cluster: 1/" $TMP_ANSIBLE/group_vars/all
      ${IS_ANSIBLE}-playbook $verbose -s $TMP_ANSIBLE/omnileads-cluster.yml --extra-vars "BUILD_DIR=$TMP/ominicontacto rama=$branch_name" --tags "$tag"
    elif [ $CLUSTER -eq 0 ]; then
      ${IS_ANSIBLE}-playbook $verbose -s $TMP_ANSIBLE/omnileads.yml --extra-vars "BUILD_DIR=$TMP/ominicontacto rama=$branch_name" --tags "$tag"
    fi
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
      if [ $CLUSTER -eq 1 ]; then
        servidor="`sed -n -e 2p $inventory_copy_location/my_inventory |awk -F \" \" '{print $1}'`"
      elif [ $CLUSTER -eq 0 ]; then
        servidor="`cat $inventory_copy_location/my_inventory |grep \"omnileads-aio\" -A1 |sed -n -e 2p |awk -F \" \" '{print $1}'`"
      fi
      echo " You can access the web interface https://$servidor"
      echo " Remember that you have a copy of your inventory file in $inventory_copy_location/my_inventory with the variables you used for your OML installation"
      echo ""
      git checkout $current_directory/inventory
    else
      echo ""
      echo "###################################################################################"
      echo "##        Omnileads installation failed, check what happened and try again       ##"
      echo "###################################################################################"
      echo ""
    fi

echo "Deleting temporal files created"
rm -rf /var/tmp/ansible
rm -rf /var/tmp/ominicontacto-build
}

case $arg1 in
  --upgrade|-u|--install|-i|kamailio|asterisk|omniapp|omnivoip|dialer|database|changeip)
    case $arg2 in
      --aio|-a)
          ./keytransfer.sh --aio
          ResultadoKeyTransfer=`echo $?`
          if [ "$ResultadoKeyTransfer" != 0 ]; then
            echo "It seems that you don't have generated keys in the server you are executing this script"
            echo "Try with ssh-keygen or check the ssh port configured in server"
            exit 1
          fi
          CLUSTER=0
      ;;
      --cluster|-c)
          ./keytransfer.sh --cluster
          ResultadoKeyTransfer=`echo $?`
          if [ "$ResultadoKeyTransfer" != 0 ]; then
            exit 1
          fi
          CLUSTER=1
      ;;
      *)
        echo "Invalid second option, options available: --aio, --cluster"
        exit 1
      ;;
    esac
    Rama
    if [ "$desarrollo" == "-d" ]; then
      Desarrollo
    fi
    Tag
  ;;
  *)
  echo " How to use it:
          (First options)
            -u --upgrade: make an upgrade of Omnileads version
            -i --install: make a fresh install of Omnileads
          (Second options)
          -a --aio: install all in one server
          -c --cluster: install cluster mode
          Both options are mandatory
          Also you can use -d options as second argument to install a development server (just if you are developer)"
  ;;
esac
