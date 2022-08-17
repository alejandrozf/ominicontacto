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
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.call_disposition import NombreCalificacionSerializer
from ominicontacto_app.models import NombreCalificacion


class CalificacionList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron las calificaciones '
                         'de forma exitosa'),
            'callDispositions': []}
        try:
            calificaciones = NombreCalificacion.objects.exclude(
                nombre=settings.CALIFICACION_REAGENDA).order_by('id')
            data['callDispositions'] = [
                NombreCalificacionSerializer(c).data for c in calificaciones]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener las calificaciones')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalificacionDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo el detalle de la calificacion '
                         'de forma exitosa'),
            'callDisposition': []}
        try:
            calificacion = NombreCalificacion.objects.get(pk=pk)
            data['callDisposition'] = NombreCalificacionSerializer(
                calificacion).data
            return Response(data=data, status=status.HTTP_200_OK)
        except NombreCalificacion.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'de la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalificacionCreate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def validate_nombre(self, name, data):
        errors = []
        if name == '':
            errors.append('El nombre es un campo requerido')
        if len(name) > 50:
            errors.append('El nombre no puede ser mayor a 50 caracteres')
        if name == settings.CALIFICACION_REAGENDA:
            errors.append('Esta calificación está reservada para el sistema')
        if len(errors) > 0:
            data['errors']['nombre'] = errors

    def post(self, request):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se creo la calificacion '
                         'de forma exitosa')}
        try:
            nombre = request.data.get('nombre')
            self.validate_nombre(nombre, data)
            if len(data['errors']) > 0:
                data['status'] = 'ERROR'
                data['message'] = _('Error al hacer la peticion')
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
            NombreCalificacion.objects.create(nombre=nombre)
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al crear '
                                'la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalificacionUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def validate_nombre(self, name, data):
        errors = []
        if name == '':
            errors.append('El nombre es un campo requerido')
        if len(name) > 50:
            errors.append('El nombre no puede ser mayor a 50 caracteres')
        if name == settings.CALIFICACION_REAGENDA:
            errors.append('Esta calificación está reservada para el sistema')
        if len(errors) > 0:
            data['errors']['nombre'] = errors

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo la calificacion '
                         'de forma exitosa')}
        try:
            calificacion = NombreCalificacion.objects.get(pk=pk)
            nombre = request.data.get('nombre')
            self.validate_nombre(nombre, data)
            if len(data['errors']) > 0:
                data['status'] = 'ERROR'
                data['message'] = _('Error al hacer la peticion')
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
            calificacion.nombre = nombre
            calificacion.save()
            return Response(data=data, status=status.HTTP_200_OK)
        except NombreCalificacion.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe la calificacion '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalificacionDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino la calificacion '
                         'de forma exitosa')}
        try:
            calificacion = NombreCalificacion.objects.get(pk=pk)
            agenda = NombreCalificacion.objects.get(
                nombre=settings.CALIFICACION_REAGENDA)
            if calificacion == agenda:
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar una '
                                    'calificacion reservada del sistema')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                calificacion.delete()
                return Response(data=data, status=status.HTTP_200_OK)
        except NombreCalificacion.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar la calificacion')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
