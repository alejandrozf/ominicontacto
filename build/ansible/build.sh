#!/bin/bash

current_directory=`pwd`
PATH=$PATH:~/.local/bin/
PIP=`which pip`
ANSIBLE=`which ansible`
TMP_ANSIBLE='/var/tmp/ansible'
ANSIBLE_VERSION_DESIRED='2.9.2'
ANSIBLE_VERSION_INSTALLED="`~/.local/bin/ansible --version |head -1| awk -F ' ' '{print $2}'`"
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
arg1=$1

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

AnsibleInstall() {
  os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
  if [ "$os" == '"CentOS Linux"' ]; then
    echo "Installing python-pip and epel-release"
    yum install epel-release -y
    sleep 5
    yum install git python-pip -y
  elif [ "$os" == '"Ubuntu"' ] || [ "$os" == '"Debian GNU/Linux"' ]; then
    echo "Installing python-pip"
    apt-get install git python-minimal python-pip -y
  fi
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
}

OmlRelease() {
  REPO_LOCATION="`git rev-parse --show-toplevel`"
  current_tag="`git tag -l --points-at HEAD`"
  release_name=$(git show ${current_tag} |grep "Merge branch" |awk -F " " '{print $3}' |tr -d "'")
  branch_name="`git branch | grep \* | cut -d ' ' -f2`"
  if [ $branch_name == "master" ]; then git pull; fi
  if [ -z "$current_tag" ]
  then
      release_name=$branch_name
  fi
  if [ ! -z ${DOCKER_TAG} ]; then
    release_name=$(echo ${DOCKER_TAG}|awk -F "-" '{print $1"-"$2}')
  fi
}

TagCheck() {
  if [ "$arg1" == "--docker-pe-build" ]; then
    tag="docker_build"
    DEVENV=0
    PRODENV=1
    BUILD_IMAGES=true
  elif [ "$arg1" == "--docker-de-build" ]; then
    tag="docker_build"
    DEVENV=1
    PRODENV=0
    BUILD_IMAGES=true
  elif [ "$arg1" == "--docker-pe-no-build" ]; then
    DEVENV=0
    PRODENV=1
    tag="docker_build"
    BUILD_IMAGES=false
  elif [ "$arg1" == "--docker-de-no-build" ]; then
    DEVENV=1
    PRODENV=0
    tag="docker_build"
    BUILD_IMAGES=false
  elif [ "$arg1" == "--aio-build" ]; then
    tag="aio_build"
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
      --extra-vars "oml_release=$release_name \
                    docker_root=$USER_HOME \
                    repo_location=$REPO_LOCATION \
                    docker_root=$USER_HOME \
                    build_images=$BUILD_IMAGES" \
      --extra-vars "{\"devenv\":$DEVENV,\"prodenv\":$PRODENV }" \
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

for i in "$@"
do
  case $i in
    --docker-pe-build|--docker-pe-no-build|--docker-de-build|--docker-de-no-build|--aio-build)
      TagCheck
      shift
    ;;
    --docker-tag=*)
      DOCKER_TAG="${i#*=}"
      shift
    ;;
    --help|-h)
      echo "
        Omnileads build script
        How to use it:
              --aio-build: build AIO rpms
              --docker-build: build and push Omnileads images to a registry.
              --docker-no-build: execute build images steps without building and pushing the images.
            "
      shift
      exit 1
    ;;
    -v*)
      verbose=$1
      shift
    ;;
    *)
      echo "One or more invalid options, use ./build.sh -h or ./build.sh --help"
      exit 1
    ;;
  esac
done
UserValidation
AnsibleInstall
OmlRelease
AnsibleExec
