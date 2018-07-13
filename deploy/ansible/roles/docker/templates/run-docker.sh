#!/bin/bash

COMPOSE_HTTP_TIMEOUT=200 /usr/local/bin/docker-compose up --build -d
ASTERISK_CONTAINER_ID=`docker ps -a |grep asterisk-omnileads |awk -F " " '{print $1}'`
KAMAILIO_CONTAINER_ID=`docker ps -a |grep rtpengine-kamailio |awk -F " " '{print $1}'`
asterisk_location={{ asterisk_location }}
kamailio_location={{ kamailio_location }}

#Archivos de configuracion asterisk para ir en el container de asterisk
#docker cp {{ install_prefix }}ominicontacto/asterisk-files/archivos-no-enlaces/*.conf asterisk:/opt/omnileads/asterisk/etc/asterisk/
#docker cp {{ install_prefix }}ominicontacto/asterisk-files/*.conf asterisk:/opt/omnileads/asterisk/etc/asterisk/

cat {{ install_prefix }}ominicontacto/ominicontacto_voip/extra-files/odbc.ini | sudo docker exec -i $ASTERISK_CONTAINER_ID /bin/bash -c 'cat > /etc/odbc.ini'
cat {{ install_prefix }}ominicontacto/ominicontacto_voip/extra-files/odbcinst.ini  | sudo docker exec -i $ASTERISK_CONTAINER_ID /bin/bash -c 'cat > /etc/odbcinst.ini'
cat {{ install_prefix }}ominicontacto/ominicontacto_voip/asterisk-files/cron-omnileads  | sudo docker exec -i $ASTERISK_CONTAINER_ID /bin/bash -c 'cat > /var/spool/cron/cron-omnileads'
cat /tmp/conversor.sh  | sudo docker exec -i $ASTERISK_CONTAINER_ID /bin/bash -c 'cat > {{ install_prefix }}bin'

#Archivos de configuracion kamailio para ir en el container de kamailioro
cat /tmp/openssl.cnf |sudo docker exec -i $KAMAILIO_CONTAINER_ID /bin/bash -c 'cat > /etc/pki/tls/openssl.cnf'
cat {{ install_prefix }}bin/certificate-create.sh |sudo docker exec -i $KAMAILIO_CONTAINER_ID /bin/bash -c 'cat > /tmp/certificate-create.sh'

docker exec -i $ASTERISK_CONTAINER_ID /bin/bash -c "chown -R omnileads. $asterisk_location && service asterisk stop && service asterisk start "
docker exec -i $KAMAILIO_CONTAINER_ID /bin/bash -c "chown -R omnileads. $kamailio_location && cd /tmp/ && \
                                                    echo 'y'| $kamailio_location/sbin/kamdbctl create && \
                                                    chmod +x certificate_create.sh && ./certificate-create.sh && \
                                                    systemctl start kamailio"
docker cp kamailio:{{ kamailio_location }}/etc/certs/cert.pem {{ install_prefix }}nginx_certs/
docker cp kamailio:{{ kamailio_location }}/etc/certs/key.pem {{ install_prefix }}nginx_certs/
docker cp kamailio:/tmp/voip.cert {{ install_prefix }}static/ominicontacto/voip.cert
chown -R omnileads. {{ install_prefix }}nginx_certs
