#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

if [ ! -f /etc/localtime ]; then
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
fi

$COMMAND regenerar_asterisk

chown -R omnileads:omnileads ${INSTALL_PREFIX}

echo "write crontab omnileads"
touch /var/spool/cron/crontabs/omnileads
cat > /var/spool/cron/crontabs/omnileads << EOF
SHELL=/bin/bash
* * * * * flock -n /opt/omnileads/actualizar_campanas_preview.lock /usr/local/bin/python3 /opt/omnileads/ominicontacto/manage.py actualizar_campanas_preview  > /dev/stdout
0 1 * * * flock -n /opt/omnileads/callrec_converter.lock /opt/omnileads/bin/callrec_converter.sh  > /dev/stdout
EOF

exec crond -b