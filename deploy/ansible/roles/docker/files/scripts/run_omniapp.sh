#!/bin/sh
COMMAND="python {{ install_prefix }}ominicontacto/manage.py"

# run as user OMNIAPP by default
OMNIAPP_USER=${OMNIAPP_USER:-"{{ usuario }}"}
OMNIAPP_GROUP=${OMNIAPP_GROUP:-${OMNIAPP_USER}}

set -e
until psql -h $PGHOST -U $PGUSER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - executing command"
sleep 5

if [ "$1" = "" ]; then
  $COMMAND migrate --noinput
  $COMMAND createsuperuser --noinput --username={{ admin_user }} --email=admin@example.com || true
  $COMMAND shell << EOF
  from ominicontacto_app.models import User
  u = User.objects.get(username='{{ admin_user }}')
  u.set_password('{{ admin_pass }}')
  u.save()
  exit()
EOF
  $COMMAND populate_history
  $COMMAND compilemessages
  echo 'yes' | $COMMAND collectstatic
  $COMMAND collectstatic_js_reverse
  $COMMAND compress --force
  $COMMAND actualizar_configuracion
  $COMMAND regenerar_asterisk
  echo "Iniciando Django Server"
else
  COMMAND="$@"
fi
{% if devenv == 1 %}
exec $COMMAND runserver 0.0.0.0:1210
{% else %}
exec {{ install_prefix }}virtualenv/bin/uwsgi --ini {{ install_prefix }}run/oml_uwsgi.ini
{% endif %}
