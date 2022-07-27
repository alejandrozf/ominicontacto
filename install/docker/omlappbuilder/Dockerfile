FROM python:3.7-alpine

ENV INSTALL_PREFIX /opt/omnileads

RUN apk add --virtual .buildeps \
      build-base \
      libffi-dev \
      postgresql-dev \
      git \
      zlib-dev \
      jpeg-dev \
      libxml2-dev \
      libxslt-dev \
      cairo-dev \
      py3-flake8

COPY requirements.txt ./

RUN mkdir -p $INSTALL_PREFIX/virtualenv \
  && pip3 install -r requirements.txt \
  && pip3 install flake8
