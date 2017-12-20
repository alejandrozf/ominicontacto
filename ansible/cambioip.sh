## Script para hacer los cambios de IP en todos los archivos para que omnileads funcione bien con una IP distinta
# Autor: Andres Felipe Macias

echo "Ingrese la IP actual"
echo -en "IP: "; read ip_actual

cd /etc/sysconfig/network-scripts/

mi_ip=`grep --color=never "$ip_actual" * | awk -F "=" '{print $2}'`
if [ "$ip_actual" != "$mi_ip" ]; then
   echo "La IP que ingresaste no coincide con la IP actual, vuelve a correr el script"
else

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
echo "Cambiando IP en oml_settings_local.py"
    sed -i "s/\(^OML_OMNILEADS_IP\).*/OML_OMNILEADS_IP = \"$nueva_ip\"/" oml_settings_local.py
    sed -i "s/\(^OML_WOMBAT_URL\).*/OML_WOMBAT_URL = \"http:\/\/$nueva_ip:8080\/wombat\"/" oml_settings_local.py
    sed -i "s/\(^OML_KAMAILIO_IP\).*/OML_KAMAILIO_IP = \"$nueva_ip\/255.255.255.255\"/" oml_settings_local.py
    sed -i "s/\(^OML_SUPERVISION_URL\).*/OML_SUPERVISION_URL = \"https:\/\/$nueva_ip:10443\/Omnisup\/index.php?page=Lista_Campanas\&supervId=\"/" oml_settings_local.py
    sed -i "s/\(^OML_GRABACIONES_URL\).*/OML_GRABACIONES_URL = \"http:\/\/$nueva_ip\/grabaciones\"/" oml_settings_local.py

cd /home/freetech/static/ominicontacto/JS/
echo "Cambiando IP en /static/JS/config.js"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js

cd /home/freetech/Omnisup/static/Js
echo "Cambiando IP en supervision"
    sed -i "s/\(^var KamailioIp\).*/var KamailioIp = \"$nueva_ip\";/" config.js
fi

