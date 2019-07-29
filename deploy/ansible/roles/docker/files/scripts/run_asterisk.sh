#!/bin/bash

# run as user asterisk by default
ASTERISK_USER=${ASTERISK_USER:-asterisk}

if [ "$1" = "" ]; then
  /usr/sbin/sshd
  mkdir /root/.ssh/
  touch /root/.ssh/authorized_keys
{% if prodenv == 1 %}
  cat /var/tmp/id_rsa.pub > /root/.ssh/authorized_keys
{% else %}
  cat /opt/sshkeys/id_rsa.pub > /root/.ssh/authorized_keys
  echo "Creating symlink of asterisk dialplan files"
  array=(oml_extensions_agent_session.conf oml_extensions_bridgecall.conf oml_extensions_commonsub.conf oml_extensions_modules.conf oml_extensions_postcall.conf oml_extensions_precall.conf oml_extensions.conf)
  for i in $(seq 0 6); do
    if [ ! -f /etc/asterisk/${array[i]} ]; then ln -s /var/tmp/${array[i]} /etc/asterisk/${array[i]}; fi
  done
{% endif %}
  rm -rf /etc/localtime
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
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
