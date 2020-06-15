#!/bin/bash

vagrant up --no-provision
vagrant sh -c 'sudo yum install kernel-devel -y && sudo yum update -y && sudo shutdown -r now' centos
vagrant halt
cd ~ && cp vps_key.pem /home/ftsinfra/ominicontacto
exit 0
