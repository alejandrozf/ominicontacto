# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from __future__ import unicode_literals
import json
from django.utils.translation import ugettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.external_system import (
    AgenteProfileSistemaExternoSerializer, SistemaExternoSerializer)
from ominicontacto_app.models import AgenteProfile, SistemaExterno


class SistemaExternoList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los sistemas externos '
                         'de forma exitosa'),
            'externalSystems': []}
        try:
            sistemasExternos = SistemaExterno.objects.all().order_by('id')
            data['externalSystems'] = [
                SistemaExternoSerializer(se).data for se in sistemasExternos]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los sistemas externos')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SistemaExternoCreate(APIView):
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
                'message': _('Se creo el sistema externo '
                             'de forma exitosa')}
            serializer = SistemaExternoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = json.dumps(serializer.errors)
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al crear el sistema externo')
            return Response(
                data=data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SistemaExternoUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo el sistema externo '
                         'de forma exitosa')}
        try:
            sistemaExterno = SistemaExterno.objects.get(pk=pk)
            serializer = SistemaExternoSerializer(
                sistemaExterno, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = json.dumps(serializer.errors)
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except SistemaExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe el sistema externo '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'el sistema externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SistemaExternoDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion del '
                         'sistema externo de forma exitosa'),
            'externalSystem': None}
        try:
            sitio = SistemaExterno.objects.get(pk=pk)
            data['externalSystem'] = SistemaExternoSerializer(sitio).data
            return Response(data=data, status=status.HTTP_200_OK)
        except SistemaExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe el sistema externo '
                                'para obtener el detalle')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'del sistema externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentesSistemaExternoList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los agentes '
                         'de forma exitosa'),
            'agents': []}
        try:
            agentes = AgenteProfile.objects.all().order_by('id')
            data['agents'] = [
                AgenteProfileSistemaExternoSerializer(a).data for a in agentes]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los agentes')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
