#!/bin/bash

CENTOS_IP="192.168.99.132"

echo "Installing git"
yum install git -y
cd /var/tmp/
git clone https://gitlab.com/omnileads/ominicontacto.git
cd ominicontacto
git fetch
git checkout $BRANCH
python deploy/vagrant/edit_inventory.py --self_hosted=yes
cd deploy/ansible
./deploy.sh -i --iface=eth1
