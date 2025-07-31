#!/bin/bash
set -e

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

[ ! -f /etc/localtime ] && ln -s /usr/share/zoneinfo/$TZ /etc/localtime

echo "=== Generate crontab OMniLeads ==="
touch /var/spool/cron/crontabs/omnileads
chown omnileads:omnileads /var/spool/cron/crontabs/omnileads
chmod 600 /var/spool/cron/crontabs/omnileads
su omnileads -c "${COMMAND} regenerar_cronos"

exec crond -f