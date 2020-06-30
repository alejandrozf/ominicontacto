#!/bin/bash
PATH=$PATH:/root/.local/bin/
AWS="/usr/local/bin/aws"

cd /home/ftsinfra/ominicontacto/deploy/vagrant/build
SSH_PORT=$(vagrant port --guest 22)
cd /home/ftsinfra/ominicontacto
# Copiando rpms a vagrant host
scp -r -P $SSH_PORT -o stricthostkeychecking=no -i deploy/vagrant/build/.vagrant/machines/centos/virtualbox/private_key vagrant@127.0.0.1:/vagrant/build/rpms build/
# Instalando y ejecutando terraform
cd /home/ftsinfra/ominicontacto/build/terraform
terraform init
terraform apply -auto-approve
# Subiendo los rpms al bucket
BUCKET_URL=$(terraform output bucket_url)
cd ..
$AWS s3 sync rpms s3://$BUCKET_URL
