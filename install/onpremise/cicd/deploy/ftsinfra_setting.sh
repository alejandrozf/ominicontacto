#!/bin/bash

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
SRC=/home/ftsinfra
PATH_DEPLOY=$SRC/ominicontacto/install/onpremise/deploy/vagrant/deploy/host_node

cd $PATH_DEPLOY
#Instalar los siguientes paquetes
pip3 install --upgrade pip
pip3 install html-testRunner pyvirtualdisplay --user
pip3 install selenium
pip3 install 'awscli==1.18.5'
pip3 install docker-py

cd $HOME
cp ominicontacto/install/onpremise/deploy/vagrant/deploy/git_cleanup.sh ./
cd ominicontacto/install/docker/devenv/
bash get_modules.sh True
cd $HOME

mv .bash_logout .bash_logout_bk
echo "export PATH='$HOME/.local/bin:$PATH'" >> ~/.bashrc
source ~/.bashrc

doctl auth init --context cicd
doctl auth switch --context cicd

echo "cp .env_do on ~/"
