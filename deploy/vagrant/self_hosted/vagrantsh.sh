#!/bin/bash

vagrant up --no-provision
vagrant sh -c 'sudo yum install kernel-devel -y && sudo yum update -y && sudo shutdown -r now' centos
vagrant sh -c 'sudo apt-get update -y && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && sudo apt-get install linux-image-amd64 -y && sudo shutdown -r now' debian
vagrant sh -c 'sudo apt-get update -y && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y &&  sudo shutdown -r now' ubuntu
exit 0
