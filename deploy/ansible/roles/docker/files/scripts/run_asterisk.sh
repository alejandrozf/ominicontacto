#!/bin/bash

# run as user asterisk by default
ASTERISK_USER=${ASTERISK_USER:-asterisk}
INTERFACE=$(ip route list | awk '/^default/ {print $5}')
INTERNAL_SUBNET=$(route | grep $INTERFACE| tail -1 |awk -F " " '{print $1"/"$3}')
if [ "$1" = "" ]; then
{% if devenv == 1 %}
  echo "Creating symlink of asterisk dialplan files"
  array=(oml_extensions_bridgecall.conf oml_extensions_commonsub.conf oml_extensions_modules.conf oml_extensions_postcall.conf oml_extensions_precall.conf oml_extensions.conf)
  for i in $(seq 0 6); do
    if [ ! -f /etc/asterisk/${array[i]} ]; then ln -s /var/tmp/${array[i]} /etc/asterisk/${array[i]}; fi
  done
{% endif %}
  echo "Setting localtime"
  rm -rf /etc/localtime
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
  echo "Writting manager.conf file"
  cat > /etc/asterisk/oml_manager.conf <<EOF
[${AMI_USER}]
secret =  ${AMI_PASSWORD}
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.255
permit = ${INTERNAL_SUBNET}
read = all
write = all
EOF
  echo "Creating /var/lib/asterisk/sounds/oml directory"
  mkdir /var/lib/asterisk/sounds/oml
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
