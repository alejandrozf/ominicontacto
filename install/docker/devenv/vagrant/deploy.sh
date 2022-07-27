#!/bin/bash

sudo apt-get update

sudo apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/docker-archive-keyring.gpg

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y

sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo systemctl start docker.service
sudo systemctl start containerd.service

sudo  curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo  chmod +x /usr/local/bin/docker-compose
sudo  ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

curl https://dl.min.io/client/mc/release/linux-amd64/mc --create-dirs -o $HOME/minio-binaries/mc

chmod +x $HOME/minio-binaries/mc
export PATH=$PATH:$HOME/minio-binaries/


sudo usermod -aG docker vagrant
sudo reboot

# minio
# install mc minio command line tool
# https://docs.min.io/minio/baremetal/reference/minio-mc.html


# mc alias set devenv http://localhost:9000 minio 098098ZZZ
# mc mb devenv/devenv
# mc admin user add devenv omnileads 098098XX
# mc admin policy set devenv readwrite user=omnileads