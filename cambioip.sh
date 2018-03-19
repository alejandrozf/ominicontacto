# Script para hacer los cambios de IP en todos los archivos para que omnileads funcione bien con una IP distinta
# Autor: Andres Felipe Macias
#!/bin/bash

VIRTUAL_ENV=`which virtualenv`

echo "Ingrese la IP actual"
echo -en "IP: "; read ip_actual

echo "Ingrese la nueva IP"
echo -en "IP: "; read nueva_ip
echo "Cambiando IP en /etc/sysconfig/rtpengine"
sudo bash -c "cat > /etc/sysconfig/rtpengine <<EOF

#
# Archivo autogenerado
#

OPTIONS=\"-i $nueva_ip -n 127.0.0.1:22222 -m 20000 -M 30000 -L 7 --log-facility=local1\"
EOF"

echo "Cambiando IP en kamailio-local.cfg"
cd /opt/kamailio/etc/kamailio/
sudo sed -i "s/$ip_actual.*/$nueva_ip!g\"/" kamailio-local.cfg

cd /opt/omnileads/local
echo "Cambiando IP en oml_settings_local.py de /opt/omnileads/local"
    sed -i "s/\(^OML_OMNILEADS_IP\).*/OML_OMNILEADS_IP = \"$nueva_ip\"/" oml_settings_local.py
    sed -i "s/\(^OML_WOMBAT_URL\).*/OML_WOMBAT_URL = \"http:\/\/$nueva_ip:8080\/wombat\"/" oml_settings_local.py
    sed -i "s/\(^OML_KAMAILIO_IP\).*/OML_KAMAILIO_IP = \"$nueva_ip\/255.255.255.255\"/" oml_settings_local.py
    sed -i "s/\(^OML_SUPERVISION_URL\).*/OML_SUPERVISION_URL = \"https:\/\/$nueva_ip:10443\/Omnisup\/index.php?page=Lista_Campanas\&supervId=\"/" oml_settings_local.py
    sed -i "s/\(^OML_GRABACIONES_URL\).*/OML_GRABACIONES_URL = \"http:\/\/$nueva_ip\/grabaciones\"/" oml_settings_local.py

cd /opt/omnileads/ominicontacto/ominicontacto_app/static/ominicontacto/JS/
echo "Cambiando IP en /static/JS/config.js"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js

cd /opt/omnileads/Omnisup/static/Js
echo "Cambiando IP en supervision"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js

if [ "$VIRTUAL_ENV" = "" ] ; then
  echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
  exit 1
fi

source /opt/omnileads/virtualenv/bin/activate
cd /opt/omnileads/ominicontacto
python manage.py collectstatic
python manage.py compress
python manage.py regenerar_asterisk

echo "Restarteando servicios"
echo "Parando kamailio"
sudo service kamailio stop
sleep 5
echo "Comenzando kamailio"
sudo service kamailio start
echo "Parando rtpengine"
sudo service rtpengine stop
sleep 5
echo "Comenzando rtpengine"
sudo service rtpengine start
echo "Parando ominicontacto-daemon"
sudo service ominicontacto-daemon stop
sleep 7
echo "Comenzando ominicontacto-daemon"
sudo service ominicontacto-daemon start
echo "Parando httpd"
sudo service httpd stop
sleep 5
echo "Empezando httpd"
sudo service httpd start
echo "Parando asterisk"
sudo fwconsole stop
sleep 5
echo "Empezando asterisk"
sudo fwconsole start

