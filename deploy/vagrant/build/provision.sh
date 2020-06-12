#!/bin/bash
BRANCH=$BRANCH
cd /vagrant/build/ansible
sed -i "s/virtualenv_version=/virtualenv_version=$BRANCH/g" inventory
./build.sh
