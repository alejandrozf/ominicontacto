## Script para hacer los cambios de IP en todos los archivos para que omnileads funcione bien con una IP distinta
# Autor: Andres Felipe Macias

VIRTUAL_ENV=`which virtualenv`

echo "Ingrese la IP actual"
echo -en "IP: "; read ip_actual

echo "Ingrese la nueva IP"
echo -en "IP: "; read nueva_ip
echo "Cambiando IP en /etc/sysconfig/rtpengine"
cat > /etc/sysconfig/rtpengine <<EOF

#
# Archivo autogenerado
#

OPTIONS="-i $nueva_ip -n 127.0.0.1:22222 -m 20000 -M 30000 -L 7 --log-facility=local1"
EOF

echo "Cambiando IP en kamailio.cfg"
cd /opt/kamailio/etc/kamailio/
   sed -i "s/$ip_actual.*/$nueva_ip!g\"/" kamailio.cfg

cd /home/freetech/local
echo "Cambiando IP en oml_settings_local.py de /home/freetech/local"
    sed -i "s/\(^OML_OMNILEADS_IP\).*/OML_OMNILEADS_IP = \"$nueva_ip\"/" oml_settings_local.py
    sed -i "s/\(^OML_WOMBAT_URL\).*/OML_WOMBAT_URL = \"http:\/\/$nueva_ip:8080\/wombat\"/" oml_settings_local.py
    sed -i "s/\(^OML_KAMAILIO_IP\).*/OML_KAMAILIO_IP = \"$nueva_ip\/255.255.255.255\"/" oml_settings_local.py
    sed -i "s/\(^OML_SUPERVISION_URL\).*/OML_SUPERVISION_URL = \"https:\/\/$nueva_ip:10443\/Omnisup\/index.php?page=Lista_Campanas\&supervId=\"/" oml_settings_local.py
    sed -i "s/\(^OML_GRABACIONES_URL\).*/OML_GRABACIONES_URL = \"http:\/\/$nueva_ip\/grabaciones\"/" oml_settings_local.py

cd /home/freetech/ominicontacto
if [ -z oml_settings_local.py ]; then
    echo "Cambiando IP en oml_settings_local.py" /home/freetech/ominicontacto
    sed -i "s/\(^OML_OMNILEADS_IP\).*/OML_OMNILEADS_IP = \"$nueva_ip\"/" oml_settings_local.py
    sed -i "s/\(^OML_WOMBAT_URL\).*/OML_WOMBAT_URL = \"http:\/\/$nueva_ip:8080\/wombat\"/" oml_settings_local.py
    sed -i "s/\(^OML_KAMAILIO_IP\).*/OML_KAMAILIO_IP = \"$nueva_ip\/255.255.255.255\"/" oml_settings_local.py
    sed -i "s/\(^OML_SUPERVISION_URL\).*/OML_SUPERVISION_URL = \"https:\/\/$nueva_ip:10443\/Omnisup\/index.php?page=Lista_Campanas\&supervId=\"/" oml_settings_local.py
    sed -i "s/\(^OML_GRABACIONES_URL\).*/OML_GRABACIONES_URL = \"http:\/\/$nueva_ip\/grabaciones\"/" oml_settings_local.py
else
    echo "No hay archivo de settings en /home/freetech/ominicontacto"
fi

cd /home/freetech/ominicontacto/ominicontacto_app/static/ominicontacto/JS/
echo "Cambiando IP en /static/JS/config.js"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js

cd /home/freetech/Omnisup/static/Js
echo "Cambiando IP en supervision"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js

if [ "$VIRTUAL_ENV" = "" ] ; then
  echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
  exit 1
fi

source /home/freetech/virtualenv/bin/activate
cd /home/freetech/ominicontacto
python manage.py collectstatic
python manage.py compress
python manage.py regenerar_asterisk

echo "Restarteando servicios"
echo "Parando kamailio"
service kamailio stop
sleep 5
echo "Comenzando kamailio"
service kamailio start
echo "Parando rtpengine"
service rtpengine stop
sleep 5
echo "Comenzando rtpengine"
service rtpengine start
echo "Parando ominicontacto-daemon"
service ominicontacto-daemon stop
sleep 7
echo "Comenzando ominicontacto-daemon"
service ominicontacto-daemon start
echo "Parando httpd"
service httpd stop
sleep 5
echo "Empezando httpd"
service httpd start
echo "Parando asterisk"
fwconsole stop
sleep 5
echo "Empezando asterisk"
fwconsole start
