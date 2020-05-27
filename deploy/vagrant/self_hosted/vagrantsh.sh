#!/bin/bash

vagrant up --no-provision
vagrant sh -c 'sudo yum install kernel-devel kernel-headers -y && sudo yum update -y && sudo shutdown -r now' centos
vagrant halt
exit 0
