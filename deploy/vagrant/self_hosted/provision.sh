#!/bin/bash

echo "Installing git and net-tools"
yum install git net-tools -y
cd /var/tmp/
git clone https://gitlab.com/omnileads/ominicontacto.git
cd ominicontacto
git fetch
git checkout $BRANCH
python deploy/vagrant/edit_inventory.py --self_hosted=yes
cd deploy/ansible
./deploy.sh -i --iface=eth1
