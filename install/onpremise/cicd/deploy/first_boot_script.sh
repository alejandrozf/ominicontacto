#!/bin/bash

BRANCH=oml-2002-fix-test-de-integracion
COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
FTSINFRAPASS=c0nqu33st4sCICD
FTSINFRAUSER=ftsinfra
CHROMEDRIVER_VERSION="90.0.4430.24"


echo "************************************************** DOCKER install ******************************************************************"
echo "************************************************** DOCKER install ******************************************************************"
echo "************************************************** DOCKER install ******************************************************************"
apt update && apt upgrade -y
apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3-pip

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
usermod -aG docker $FTSINFRAUSER

curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "************************************************** Google chrome & chromedriver  install ******************************************************************"
echo "************************************************** Google chrome & chromedriver  install ******************************************************************"
echo "************************************************** Google chrome & chromedriver  install ******************************************************************"

echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
wget https://dl.google.com/linux/linux_signing_key.pub
apt-key add linux_signing_key.pub
apt update && apt install google-chrome-stable xvfb -y

wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
cp chromedriver /usr/bin/

sudo apt install curl
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "************************************************** DOCTL install ******************************************************************"
echo "************************************************** DOCTL install ******************************************************************"
echo "************************************************** DOCTL install ******************************************************************"
cd /tmp/
wget https://github.com/digitalocean/doctl/releases/download/v1.60.0/doctl-1.60.0-linux-amd64.tar.gz
tar xfz doctl-1.60.0-linux-amd64.tar.gz
mv doctl /usr/local/bin

echo "************************************************** Create FTSINFRA user ******************************************************************"
echo "************************************************** Create FTSINFRA user ******************************************************************"
echo "************************************************** Create FTSINFRA user ******************************************************************"
useradd -m -s /bin/bash -c "gitlab CI/CD user" $FTSINFRAUSER
echo "$FTSINFRAUSER    ALL=(ALL)       ALL" >> /etc/sudoers

cd /home/$FTSINFRAUSER
git clone --recurse-submodules --branch $BRANCH $COMPONENT_REPO
chown -R $FTSINFRAUSER.$FTSINFRAUSER /home/$FTSINFRAUSER
