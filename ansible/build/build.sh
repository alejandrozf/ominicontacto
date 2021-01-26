#!/bin/bash

current_directory=`pwd`
PATH=$PATH:~/.local/bin/
ANSIBLE=`which ansible`
TMP_ANSIBLE='/var/tmp/ansible'
USER_HOME=$(eval echo ~${SUDO_USER})
export ANSIBLE_CONFIG=$TMP_ANSIBLE
arg1=$1
FTS_PUBLIC_BUCKET="fts-public-packages"

AnsibleInstall() {
  cd $current_directory
  set -o allexport
  source "$current_directory/../.env"
  set +o allexport
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
      --extra-vars "docker_root=$USER_HOME \
                    repo_location=$REPO_LOCATION \
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
      git checkout $current_directory/inventory
      chown $SUDO_USER. $current_directory/inventory
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
AnsibleInstall
OmlRelease
AnsibleExec
