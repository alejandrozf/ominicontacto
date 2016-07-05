#!/bin/bash

BASEDIR=$(cd $(dirname $0) ; pwd)

if [ -z "${VIRTUAL_ENV}" -a -d ${BASEDIR}/virtualenv ] ; then
	. ${BASEDIR}/virtualenv/bin/activate
fi


uwsgi \
    --module=ominicontacto.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-ominicontacto.settings} \
    $EXTRA_ENV \
    --master \
    --processes=${UWSGI_PROCESSES:-5} --enable-threads \
    --home=${VIRTUAL_ENV} \
    --http=${UWSGI_HTTP:-0.0.0.0:8000} \
    --uwsgi-socket=0.0.0.0:8097 \
    --python-path=${BASEDIR} \
    --master-fifo=/tmp/.ominicontacto-uwsgi-fifo \
    $*
