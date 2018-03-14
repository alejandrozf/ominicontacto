#!/bin/bash

if [ "$VIRTUAL_ENV" = "" ] ; then
	echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
	exit 1
fi

cd $(dirname $0)



coverage run --omit='ominicontacto_app/migrations/*,ominicontacto_app/tests/*,reciclado_app/tests/*' --source='ominicontacto_app.models' manage.py test ominicontacto_app.tests reciclado_app.tests

coverage html -d /tmp/oml-coverity --title="Coverage para Omnileads"

which gnome-open > /dev/null 2> /dev/null && gnome-open /tmp/oml-coverity/index.html



