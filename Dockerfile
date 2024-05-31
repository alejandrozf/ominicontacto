# vim:set ft=dockerfile:

########################################################################
# Stage build python pip requirements and utils
FROM python:3.9-alpine as dev

ENV INSTALL_PREFIX /opt/omnileads

RUN apk add --virtual .buildeps \
      build-base \
      libffi-dev \
      postgresql14-dev \
      git \
      zlib-dev \
      jpeg-dev \
      libxml2-dev \
      libxslt-dev \
      cairo-dev \
      py3-flake8 \
      cargo \
      openssl-dev \
      libsass-dev \
      npm

COPY requirements/requirements.txt ./

RUN mkdir -p $INSTALL_PREFIX/virtualenv \
  && pip3 install --upgrade pip \
  && pip3 install -r requirements.txt \
  && pip3 install flake8 \
  && apk del .buildeps

########################################################################
# Stage build VueJS
FROM freetechsolutions/vue-cli:develop as vuejs

WORKDIR /omnileads_ui/oml_frontend
COPY omnileads_ui/ ./
RUN npm install
RUN npm run build

########################################################################
# Build omlapp image with binaries
FROM python:3.9-alpine as run

ENV INSTALL_PREFIX /opt/omnileads

# Copia todo el virtualenv
COPY --from=dev /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --from=dev /src/pyst2/ /src/pyst2/
COPY --from=dev /usr/local/bin/flake8 /usr/local/bin/
COPY --from=dev /usr/local/bin/uwsgi /usr/local/bin/
COPY --from=dev /usr/local/bin/daphne /usr/local/bin/

RUN apk add --no-cache bash \
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
        postgresql14-client \
        pcre pcre-dev \
        aws-cli \
        git \
        build-base \
        gcc \
        wget \
        coreutils \
        sudo \
    && wget https://sourceware.org/pub/libffi/libffi-3.3.tar.gz \
    &&  tar xzvf libffi-3.3.tar.gz \
    && cd libffi-3.3/ \
    && ./configure \
    && make \
    && make install \
    && addgroup -g 1000 -S omnileads &&  adduser -u 1000 -S omnileads -G omnileads -h $INSTALL_PREFIX -s /bin/bash \
    && cd $INSTALL_PREFIX \
    && mkdir -p wombat-json bin backup media_root/reporte_campana static log run addons ominicontacto asterisk/var/spool/monitor \
    && wget https://keys-server.freetech.com.ar:20852/cert --no-check-certificate

#Copia el codigo de rama actual
COPY ominicontacto/ $INSTALL_PREFIX/ominicontacto/ominicontacto
COPY requirements $INSTALL_PREFIX/ominicontacto
COPY test $INSTALL_PREFIX/ominicontacto
COPY tests $INSTALL_PREFIX/ominicontacto
COPY api_app $INSTALL_PREFIX/ominicontacto/api_app
COPY configuracion_telefonia_app $INSTALL_PREFIX/ominicontacto/configuracion_telefonia_app
COPY ominicontacto_app $INSTALL_PREFIX/ominicontacto/ominicontacto_app
COPY reciclado_app $INSTALL_PREFIX/ominicontacto/reciclado_app
COPY reportes_app $INSTALL_PREFIX/ominicontacto/reportes_app
COPY supervision_app $INSTALL_PREFIX/ominicontacto/supervision_app
COPY slowsql $INSTALL_PREFIX/ominicontacto/slowsql
COPY notification_app $INSTALL_PREFIX/ominicontacto/notification_app
COPY utiles_globales.py manage.py $INSTALL_PREFIX/ominicontacto/
COPY omnileads_ui $INSTALL_PREFIX/ominicontacto/omnileads_ui
COPY orquestador_app $INSTALL_PREFIX/ominicontacto/orquestador_app
COPY whatsapp_app $INSTALL_PREFIX/ominicontacto/whatsapp_app
COPY build/oml_uwsgi.ini ${INSTALL_PREFIX}/run/oml_uwsgi.ini
COPY build/scripts/* $INSTALL_PREFIX/bin/
COPY omnileads_ui/ $INSTALL_PREFIX/ominicontacto/omnileads_ui
COPY --from=vuejs  /omnileads_ui/oml_frontend/dist/ $INSTALL_PREFIX/ominicontacto/omnileads_ui/dist
RUN chmod +x $INSTALL_PREFIX/bin/*
RUN chown -R omnileads:omnileads $INSTALL_PREFIX /var/spool/cron/ /var/spool/cron/crontabs/
