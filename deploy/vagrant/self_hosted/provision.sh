#!/bin/bash

echo "Installing git and net-tools"
yum install git net-tools -y
python /vagrant/deploy/vagrant/edit_inventory.py --self_hosted=yes
cd /vagrant/deploy/ansible
./deploy.sh -i --iface=eth1
