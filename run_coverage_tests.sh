#!/bin/bash

if [ "$VIRTUAL_ENV" = "" ] ; then
	echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
	exit 1
fi

cd $(dirname $0)



coverage run --omit='ominicontacto_app/migrations/*,ominicontacto_app/tests/*,ominicontacto_app/tests/tests.py ,reciclado_app/tests/*,reportes_app/migrations/*,reportes_app/tests/*' --source='ominicontacto_app,reciclado_app,reportes_app' manage.py test ominicontacto_app.tests reciclado_app.tests reportes_app.tests

coverage html -d /tmp/oml-coverity --title="Coverage para Omnileads"

which gnome-open > /dev/null 2> /dev/null && gnome-open /tmp/oml-coverity/index.html



