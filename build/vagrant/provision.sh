#!/bin/bash
BRANCH=$BRANCH
cd /vagrant/build/ansible
python /vagrant/build/vagrant/edit_inventory.py --aio_build=yes --release=$BRANCH
./build.sh --aio-build
