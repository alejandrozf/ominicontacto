#!/bin/bash

if [[ $CI_COMMIT_REF_NAME == *"release"* ]]; then
  cd /home/ftsinfra/ominicontacto/vagrant/deploy/host_node/
  vagrant package --base Centos-Staging --output centos-$CI_COMMIT_REF_NAME.box
  cp centos-$CI_COMMIT_REF_NAME.box /home/ftsinfra/oml-boxes
  cp -a .vagrant/machines/centos/virtualbox/private_key /home/ftsinfra/oml-boxes/centos_private_key_$CI_COMMIT_REF_NAME
  rm -rf centos-$CI_COMMIT_REF_NAME.box
fi
