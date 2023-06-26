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

from __future__ import unicode_literals
from django.utils.translation import gettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from constance import config
from api_app.serializers.register_server import RegisterServerSerializer


class RegisterServerList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo el registro del servidor '
                         'forma exitosa'),
            'registerServer': None,
            'adminName': '',
            'registered': False}
        try:
            user = self.request.user
            client = config.CLIENT_NAME
            password = config.CLIENT_PASSWORD
            email = config.CLIENT_EMAIL
            telefono = config.CLIENT_PHONE
            data['adminName'] = user.username if user.username else ''
            data['isAdmin'] = user.get_is_administrador()
            data['registered'] = (config.CLIENT_NAME != '' and config.CLIENT_KEY != '')
            data['registerServer'] = {
                'client': client, 'password': password, 'email': email, 'phone': telefono}
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener el registro al servidor')
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterServerCreate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        try:
            data = {
                'status': 'SUCCESS',
                'errors': {},
                'message': _('Se creo el registro al servidor '
                             'de forma exitosa')}
            serializer = RegisterServerSerializer(data=request.data)
            if serializer.is_valid():
                register = serializer.save()
                if register['status'] == 'ERROR':
                    print('===> Register server error: ', register)
                    data['message'] = register.get('msg', 'Error al crear el registro al servidor')
                    data['status'] = 'ERROR'
                    return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = _('Falta informacion para completar el registro')
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al crear el registro al servidor')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
