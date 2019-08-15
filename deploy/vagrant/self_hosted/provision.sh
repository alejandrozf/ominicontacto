#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

CENTOS_IP="172.16.20.132"
DEBIAN_IP="172.16.20.130"
UBUNTU_IP="172.16.20.131"


os=`awk -F= '/^NAME/{print $2}' /etc/os-release`
if [ "$os" == '"CentOS Linux"' ]; then
  echo "Installing git"
  yum install git -y
  cd /var/tmp/
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git fetch
  git checkout $BRANCH
  python /vagrant/edit_ansible.py --remote_host=centos-example.com --internal_ip=$CENTOS_IP --self_hosted=yes --admin_pass=098098ZZZ --databases_pass=admin123
elif [ "$os" == '"Debian GNU/Linux"' ]; then
  echo "Installing git"
  apt-get install git -y
  cd /var/tmp/
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git fetch
  git checkout $BRANCH
  python /vagrant/edit_ansible.py --remote_host=debian-example --internal_ip=$DEBIAN_IP --self_hosted=yes --admin_pass=098098ZZZ --databases_pass=admin123
elif [ "$os" == '"Ubuntu"' ]; then
  echo "Installing git"
  apt-get install git -y
  cd /var/tmp/
  git clone https://gitlab.com/omnileads/ominicontacto.git
  cd ominicontacto
  git fetch
  git checkout $BRANCH
  apt-get update -y
  echo 'yes' | apt-get install python-minimal -y
  python /vagrant/edit_ansible.py --remote_host=ubuntu-example --internal_ip=$UBUNTU_IP --self_hosted=yes --admin_pass=098098ZZZ --databases_pass=admin123
else
  echo "The OS you are trying to install is not supported to install this software."
  exit 1
fi
cd deploy/ansible
./deploy.sh -i
