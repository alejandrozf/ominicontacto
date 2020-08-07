#!/bin/bash

# run as user asterisk by default
ASTERISK_USER=${ASTERISK_USER:-asterisk}
INTERFACE=$(ip route list | awk '/^default/ {print $5}')
INTERNAL_NETADDR=$(route | grep $INTERFACE| tail -1 |awk -F " " '{print $1}')
INTERNAL_NETMASK=$(route | grep $INTERFACE| tail -1 |awk -F " " '{print $3}')
PUBLIC_IP=$(curl http://ipinfo.io/ip)

if [ "$1" = "" ]; then
  echo "Setting localtime"
  rm -rf /etc/localtime
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
{% if devenv == 1 %}
  echo "Creating symlink of asterisk dialplan files"
  array=(oml_extensions_bridgecall.conf oml_extensions_commonsub.conf oml_extensions_modules.conf oml_extensions_postcall.conf oml_extensions_precall.conf oml_extensions.conf)
  for i in $(seq 0 6); do
    if [ ! -f /etc/asterisk/${array[i]} ]; then ln -s /var/tmp/${array[i]} /etc/asterisk/${array[i]}; fi
  done
{% else %}
  echo "Modifying manager.conf file"
  sed -i "s/^\[bla\].*/[${AMI_USER}]/g" /etc/asterisk/oml_manager.conf
  sed -i "s/^secret.*/secret = ${AMI_PASSWORD}/g" /etc/asterisk/oml_manager.conf
  sed -i "/^permit = 127.0.0.1.*/a permit = ${INTERNAL_NETADDR}\/${INTERNAL_NETMASK}" /etc/asterisk/oml_manager.conf

  echo "Writting the IP in pjsip files"
  sed -i "0,/external_media_address=.*/s//external_media_address=${PUBLIC_IP}/g" /etc/asterisk/oml_pjsip_transports.conf
  sed -i "0,/external_signaling_address=.*/s//external_signaling_address=${PUBLIC_IP}/g" /etc/asterisk/oml_pjsip_transports.conf
  sed -i "0,/external_media_address=.*/! s/external_media_address=.*/external_media_address=${DOCKER_IP}/" /etc/asterisk/oml_pjsip_transports.conf
  sed -i "0,/external_signaling_address=.*/! s/external_signaling_address=.*/external_signaling_address=${DOCKER_IP}/" /etc/asterisk/oml_pjsip_transports.conf
  sed -i "0,/endpoint\/permit=.*/s//endpoint\/permit=${INTERNAL_NETADDR}\/${INTERNAL_NETMASK}/g" /etc/asterisk/oml_pjsip_wizard.conf

  echo "Writing the odbc.ini file with database variables"
  sed -i "s/postgresql/${PGHOST}/g" /etc/odbc.ini
  sed -i "s/^Database.*/Database            = ${PGDATABASE}/g" /etc/odbc.ini
  sed -i "s/^UserName.*/UserName            = ${PGUSER}/g" /etc/odbc.ini

  echo "Writing oml_res_odbc.conf file"
  sed -i "s/^username.*/username => ${PGUSER}/g" /etc/asterisk/oml_res_odbc.conf
{% endif %}

  echo "Initializing asterisk"
  COMMAND="/usr/sbin/asterisk -T -U ${ASTERISK_USER} -p -vvvvvvvf"
else
  COMMAND="$@"
fi

# recreate user and group for asterisk
# if they've sent as env variables (i.e. to macth with host user to fix permissions for mounted folders

deluser asterisk && \
adduser --gecos "" --no-create-home --uid 1000 --disabled-password ${ASTERISK_USER} || exit
chown -R 1000:1000 /etc/asterisk \
                                         /var/*/asterisk \
                                         /usr/*/asterisk
exec ${COMMAND}
