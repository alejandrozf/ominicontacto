#!/bin/bash

COMPOSE_HTTP_TIMEOUT=200 /usr/local/bin/docker-compose up --build -d
ASTERISK_CONTAINER_ID=`docker ps -a |grep asterisk-omnileads |awk -F " " '{print $1}'`
KAMAILIO_CONTAINER_ID=`docker ps -a |grep rtpengine-kamailio |awk -F " " '{print $1}'`

#Archivos de configuracion asterisk para ir en el container de asterisk
#docker cp {{ install_prefix }}ominicontacto/asterisk-files/archivos-no-enlaces/*.conf asterisk:/opt/omnileads/asterisk/etc/asterisk/
#docker cp {{ install_prefix }}ominicontacto/asterisk-files/*.conf asterisk:/opt/omnileads/asterisk/etc/asterisk/
docker cp {{ install_prefix }}ominicontacto/ominicontacto_voip/extra-files/odbc.ini asterisk:/etc/
docker cp {{ install_prefix }}ominicontacto/ominicontacto_voip/extra-files/odbcinst.ini asterisk:/etc/
docker cp {{ install_prefix }}ominicontacto/ominicontacto_voip/asterisk-files/cron-omnileads asterisk:/var/spool/cron/
docker cp /tmp/conversor.sh asterisk:{{ install_prefix }}bin

#Archivos de configuracion kamailio para ir en el container de kamailioro
docker cp /tmp/kamailio.service kamailio:/etc/systemd/system/
docker cp /tmp/kamailio kamailio:/etc/default/
docker cp {{ install_prefix }}bin/certificate-create.sh kamailio:/tmp/

docker restart asterisk
docker exec -i -t $ASTERISK_CONTAINER_ID /bin/bash -c "service asterisk start"
docker exec -i -t $KAMAILIO_CONTAINER_ID /bin/bash -c "cd /tmp/ && ./certificate-create.sh && \
                                                          systemctl daemon reload && \
                                                          systemctl start rtpengine && systemctl enable rtpengine && \
                                                          systemctl enable kamailio && systemctl start kamailio"
