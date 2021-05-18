#!/bin/bash

sudo mkdir /root/.ssh
sudo touch /root/.ssh/authorized_keys
sudo echo "${CICD_ROOT_PUBLIC_KEY}" > /root/.ssh/authorized_keys
sudo yum update -y
sudo yum install kernel-devel -y
sudo systemctl disable firewalld && sudo systemctl stop firewalld
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sudo sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
