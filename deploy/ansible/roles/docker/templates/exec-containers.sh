#!/bin/bash

ASTERISK_CONTAINER_ID=`sudo docker ps -a |grep asterisk-freepbx |awk -F " " '{print $1}'`
KAMAILIO_CONTAINER_ID=`sudo docker ps -a |grep rtpengine-kamailio |awk -F " " '{print $1}'`

echo "Ingrese 1 para abrir shell de Asterisk o 2 para abrir shell de Kamailio"
echo -en "Opcion: "; read opcion

if [ $opcion -eq 1 ]; then
sudo docker exec -i -t $ASTERISK_CONTAINER_ID /bin/bash
elif [ $opcion -eq 2 ]; then
sudo docker exec -i -t $KAMAILIO_CONTAINER_ID /bin/bash
fi
