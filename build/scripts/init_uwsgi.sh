#!/bin/bash

COMMAND="python3 ${INSTALL_PREFIX}ominicontacto/manage.py"

set -e

echo "******** OMniLeads UWSGI server ********"
echo "Remove omlcron crontabs"
cat /dev/null > /var/spool/cron/crontabs/root
echo "uwsgi.ini settings"

if [[ $UWSGI_CUSTOM == "True" ]]; then
cat >> ${INSTALL_PREFIX}/run/oml_uwsgi.ini << EOF
processes=${UWSGI_PROCESSES}
threads=${UWSGI_THREADS}
max-worker-lifetime=7200
reload-on-rss=1024
reload-on-as=2048
evil-reload-on-rss=3096
max-requests=2000
EOF
fi

chown omnileads:omnileads ${INSTALL_PREFIX}/run/oml_uwsgi.ini
su omnileads -c "touch  /var/spool/cron/crontabs/omnileads"

echo "Run django command compilemessages"
$COMMAND compilemessages
echo "Run django command colllect_static"
echo 'yes' | $COMMAND collectstatic
$COMMAND collectstatic_js_reverse
echo "Run django command compress"
$COMMAND compress --force
echo "Run actualizar_permisos"
$COMMAND actualizar_permisos
echo "Run django command regenerar_asterisk"
su omnileads -c "$COMMAND regenerar_asterisk"
echo "Init uWSGI"
exec /usr/local/bin/uwsgi --ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini --http-socket ${DJANGO_HOSTNAME}:${UWSGI_PORT}
