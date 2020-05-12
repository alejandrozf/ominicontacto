#!/bin/bash

current_directory=`pwd`
PATH=$PATH:~/.local/bin/
PIP=`which pip`
ANSIBLE=`which ansible`
TMP_ANSIBLE='/var/tmp/ansible'
ANSIBLE_VERSION_DESIRED='2.9.2'
ANSIBLE_VERSION_INSTALLED="`~/.local/bin/ansible --version |head -1| awk -F ' ' '{print $2}'`"
REPO_LOCATION="`git rev-parse --show-toplevel`"
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
arg1=$1

AnsibleInstall() {
  echo "Installing python-pip and epel-release"
  yum install epel-release -y
  yum install python-pip -y
  PIP=`which pip`
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
  current_tag="`git tag -l --points-at HEAD`"
  release_name=$(git show ${current_tag} |grep "Merge branch" |awk -F " " '{print $3}' |tr -d "'")
  branch_name="`git branch | grep \* | cut -d ' ' -f2`"
  if [ $branch_name == "master" ]; then git pull; fi
  if [ -z "$current_tag" ]
  then
      release_name=$branch_name
  fi
}

AnsibleExec() {
    echo "Checking if there are hosts to deploy from inventory file"
    if ${ANSIBLE} all --list-hosts -i $TMP_ANSIBLE/inventory | grep -q '(0)' 2>/dev/null; then
      echo "All hosts in inventory file are commented, please check the file according to documentation"
      exit 1
    fi
    echo "Beginning the Omnileads installation with Ansible, this installation process can last between 30-40 minutes"
    echo ""
    ${ANSIBLE}-playbook $verbose $TMP_ANSIBLE/build.yml \
      --extra-vars "oml_release=$release_name" \
      -i $TMP_ANSIBLE/inventory
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
      echo "##          Omnileads build ended successfully        ##"
      echo "###############################################################"
      echo ""
    else
      echo ""
      echo "###################################################################################"
      echo "##        Omnileads build failed, check what happened and try again       ##"
      echo "###################################################################################"
      echo ""
      exit 1
    fi

echo "Deleting temporal files created"
rm -rf $TMP_ANSIBLE
}
AnsibleInstall
AnsibleExec
