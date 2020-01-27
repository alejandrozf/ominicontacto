#!/bin/bash

CENTOS_IP="192.168.99.132"

echo "Installing git"
yum install git -y
cd /var/tmp/
git clone https://gitlab.com/omnileads/ominicontacto.git
cd ominicontacto
git fetch
git checkout $BRANCH
python deploy/vagrant/edit_ansible.py --internal_ip=$CENTOS_IP --self_hosted=yes --admin_pass=098098ZZZ --databases_pass=admin123
cd deploy/ansible
./deploy.sh -i --iface=eth1

