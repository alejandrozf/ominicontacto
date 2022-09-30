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
from api_app.serializers.external_site_authentication import AutenticacionSitioExternoSerializer
from ominicontacto_app.models import AutenticacionSitioExterno


class ExternalSiteAuthenticationList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron las autenticaciones para sitios '
                         'externos de forma exitosa'),
            'externalSiteAuthentications': []}
        try:
            auths_sitio_externo = AutenticacionSitioExterno.objects.all().order_by('id')
            data['externalSiteAuthentications'] = [
                AutenticacionSitioExternoSerializer(auth).data for auth in auths_sitio_externo]
            return Response(data=data, status=status.HTTP_200_OK)
        except AutenticacionSitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener las autenticaciones para sitios externos')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalSiteAuthenticationCreate(APIView):
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
                'message': _('Se creo la autenticacion para sitio externo '
                             'de forma exitosa')}
            auth_sitio_externo = AutenticacionSitioExternoSerializer(data=request.data)
            if auth_sitio_externo.is_valid():
                auth_sitio_externo.save()
                return Response(data=responseData, status=status.HTTP_200_OK)
            else:
                responseData['status'] = 'ERROR'
                responseData['message'] = [
                    auth_sitio_externo.errors[key] for key in auth_sitio_externo.errors]
                responseData['errors'] = auth_sitio_externo.errors
                return Response(
                    data=responseData, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            responseData['status'] = 'ERROR'
            responseData['message'] = _('Error al crear la autenticacion para sitio externo')
            return Response(
                data=responseData,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalSiteAuthenticationUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo la autenticacion para sitio externo '
                         'de forma exitosa')}
        try:
            auth_sitio_externo = AutenticacionSitioExterno.objects.get(pk=pk)
            serializer = AutenticacionSitioExternoSerializer(
                auth_sitio_externo, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = [
                    serializer.errors[key] for key in serializer.errors]
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except AutenticacionSitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe la autenticacion para sitio externo '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'la autenticacion para sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalSiteAuthenticationDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion de la autenticacion para '
                         'sitio externo de forma exitosa'),
            'externalSiteAuthentication': None}
        try:
            auth_sitio_externo = AutenticacionSitioExterno.objects.get(pk=pk)
            data['externalSiteAuthentication'] = AutenticacionSitioExternoSerializer(
                auth_sitio_externo).data
            return Response(data=data, status=status.HTTP_200_OK)
        except AutenticacionSitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'de la autenticacion para sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalSiteAuthenticationDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino la autenticacion para sitio externo '
                         'de forma exitosa')}
        try:
            auth_sitio_externo = AutenticacionSitioExterno.objects.get(pk=pk)
            if auth_sitio_externo.tiene_sitios_externos():
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar una '
                                    'autenticacion que tiene sitios externos')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                auth_sitio_externo.delete()
                return Response(data=data, status=status.HTTP_200_OK)
        except AutenticacionSitioExterno.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la autenticacion para sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar la autenticacion para sitio externo')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
