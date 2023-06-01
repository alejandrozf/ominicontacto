# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
import logging
import requests
from rest_framework import serializers
from constance import config
from django.utils.translation import gettext_lazy as _
logger = logging.getLogger(__name__)


class RegisterServerSerializer(serializers.Serializer):

    client = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def _create_credentials(self, data):
        create_url = '{0}/retrieve_key/'.format(config.KEYS_SERVER_HOST)
        try:
            result = requests.post(
                create_url, json=data, verify=config.SSL_CERT_FILE)
            return result.json()
        except AttributeError:
            msg = _('No tiene settings de conexion configurados')
            logger.error(msg)
            return {'status': 'ERROR', 'msg': msg}
        except requests.exceptions.RequestException as e:
            msg = _('Error en el intento de conexion a: {0} debido {1}'.format(create_url, e))
            logger.error(msg)
            return {'status': 'ERROR', 'msg': msg}

    def create(self, validated_data):
        client = validated_data.get('client')
        password = validated_data.get('password')
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        result = self._create_credentials({
            'client': client, 'password': password, 'email': email, 'phone': phone})
        if result['status'] != 'ERROR':
            config.CLIENT_NAME = result['user_name']
            config.CLIENT_PASSWORD = password
            config.CLIENT_EMAIL = result['user_email']
            config.CLIENT_PHONE = result['user_phone']
            config.CLIENT_KEY = result['user_key']
        else:
            config.CLIENT_NAME = ''
            config.CLIENT_PASSWORD = ''
            config.CLIENT_EMAIL = ''
            config.CLIENT_PHONE = ''
            config.CLIENT_KEY = ''
        return result

    class Meta:
        fields = '__all__'
