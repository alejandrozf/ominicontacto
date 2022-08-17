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
from django.utils.translation import ugettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.external_site import SitioExternoSerializer
from ominicontacto_app.models import SitioExterno


class SitioExternoList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los sitios '
                         'externos de forma exitosa'),
            'externalSites': []}
        try:
            sitios = SitioExterno.objects.all().order_by('id')
            data['externalSites'] = [
                SitioExternoSerializer(sitio).data for sitio in sitios]
            return Response(data=data, status=status.HTTP_200_OK)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los sitios externos')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoCreate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        try:
            responseData = {
                'status': 'SUCCESS',
                'errors': {},
                'message': _('Se creo el sitio externo '
                             'de forma exitosa')}
            sitio = SitioExternoSerializer(data=request.data)
            if sitio.is_valid():
                sitio.save()
                return Response(data=responseData, status=status.HTTP_200_OK)
            else:
                responseData['status'] = 'ERROR'
                responseData['message'] = _('Error al hacer la peticion')
                responseData['errors'] = sitio.errors
                return Response(
                    data=responseData, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            responseData['status'] = 'ERROR'
            responseData['message'] = _('Error al crear el sitio externo')
            return Response(
                data=responseData,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo el sitio externo '
                         'de forma exitosa')}
        try:
            sitioExterno = SitioExterno.objects.get(pk=pk)
            serializer = SitioExternoSerializer(
                sitioExterno, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = _('Error al hacer la peticion')
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe el sitio externo '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'el sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoDetalle(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion del '
                         'sitio externo de forma exitosa'),
            'externalSiteDetail': None}
        try:
            sitio = SitioExterno.objects.get(pk=pk)
            data['externalSiteDetail'] = SitioExternoSerializer(sitio).data
            return Response(data=data, status=status.HTTP_200_OK)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el '
                                'detalle del sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino el sitio externo '
                         'de forma exitosa')}
        try:
            sitio = SitioExterno.objects.get(pk=pk)
            if sitio.campana_set.exists():
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar un '
                                    'sitio externo asociado a una campaña')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                sitio.delete()
            return Response(data=data, status=status.HTTP_200_OK)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe el sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar el sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoOcultar(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se oculto el sitio externo '
                         'de forma exitosa')}
        try:
            sitio = SitioExterno.objects.get(pk=pk)
            sitio.ocultar()
            return Response(data=data, status=status.HTTP_200_OK)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al ocultar el sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SitioExternoDesocultar(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se desoculto el sitio externo '
                         'de forma exitosa')}
        try:
            sitio = SitioExterno.objects.get(pk=pk)
            sitio.desocultar()
            return Response(data=data, status=status.HTTP_200_OK)
        except SitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al desocultar el sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
