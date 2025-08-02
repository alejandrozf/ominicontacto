#!/bin/bash
set -e

# Zona horaria
[ ! -f /etc/localtime ] && ln -s /usr/share/zoneinfo/$TZ /etc/localtime

echo "=== Generate crontab OMniLeads ==="
CRON_FILE=/var/spool/cron/crontabs/omnileads
touch  $CRON_FILE
chown omnileads:omnileads $CRON_FILE
chmod 600 $CRON_FILE

su omnileads -c "python3 ${INSTALL_PREFIX}ominicontacto/manage.py regenerar_cronos"

# Reaper de zombies
trap 'while wait -n; do :; done' CHLD
crond -f &
wait
