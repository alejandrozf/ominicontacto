#!/bin/bash
PATH=$PATH:/root/.local/bin/
AWS="/usr/local/bin/aws"

BUILD_DIR="/home/ftsinfra/ominicontacto/build/"

cd $BUILD_DIR/vagrant
SSH_PORT=$(vagrant port --guest 22)
# Copiando rpms a vagrant host
scp -r -P $SSH_PORT -o stricthostkeychecking=no -i .vagrant/machines/centos/virtualbox/private_key vagrant@127.0.0.1:/vagrant/build/rpms ../
# Instalando y ejecutando terraform
cd $BUILD_DIR/terraform
terraform init
terraform apply -auto-approve
# Subiendo los rpms al bucket
BUCKET_URL=$(terraform output bucket_url)
cd ..
$AWS s3 sync rpms s3://$BUCKET_URL
