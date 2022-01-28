FROM freetechsolutions/omlapp-builder:latest as builder

FROM python:3.7-alpine

ENV INSTALL_PREFIX /opt/omnileads

# Copia todo el virtualenv
COPY --from=builder /usr/local/lib/python3.7/ /usr/local/lib/python3.7/
COPY --from=builder /src/pyst2/ /src/pyst2/
COPY --from=builder /usr/local/bin/flake8 /usr/local/bin/
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/

RUN apk add bash \
        busybox-suid \
        py3-cairo \
        curl \
        gettext \
        lame \
        libjpeg-turbo \
        libpq \
        libxslt \
        sox \
        tzdata \
        postgresql-client \
        pcre pcre-dev \
        aws-cli \
        git \
    && addgroup -g 1000 -S omnileads &&  adduser -u 1000 -S omnileads -G omnileads -h $INSTALL_PREFIX -s /bin/bash \
    && cd $INSTALL_PREFIX \
    && mkdir -p wombat-json bin backup media_root/reporte_campana static log run \
    && chown -R omnileads.omnileads $INSTALL_PREFIX /var/spool/cron/ /var/spool/cron/crontabs/ \
    && wget https://keys-server.freetech.com.ar:20852/cert --no-check-certificate

#Copia el codigo de rama actual
COPY ominicontacto/ $INSTALL_PREFIX/ominicontacto/ominicontacto
COPY api_app $INSTALL_PREFIX/ominicontacto/api_app
COPY configuracion_telefonia_app $INSTALL_PREFIX/ominicontacto/configuracion_telefonia_app
COPY ominicontacto_app $INSTALL_PREFIX/ominicontacto/ominicontacto_app
COPY reciclado_app $INSTALL_PREFIX/ominicontacto/reciclado_app
COPY reportes_app $INSTALL_PREFIX/ominicontacto/reportes_app
COPY supervision_app $INSTALL_PREFIX/ominicontacto/supervision_app
COPY utiles_globales.py manage.py $INSTALL_PREFIX/ominicontacto/

RUN git clone --branch develop https://gitlab.com/omnileads/omlutilities.git $INSTALL_PREFIX/utils

COPY install/docker/scripts/oml_uwsgi.ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini
COPY install/docker/scripts/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD [""]
