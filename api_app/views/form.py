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
from django.utils.translation import gettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.form import FormularioSerializer
from ominicontacto_app.models import Formulario


class FormList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los formularios '
                         'de forma exitosa'),
            'forms': []}
        try:
            formularios = Formulario.objects.all().order_by('id')
            data['forms'] = [
                FormularioSerializer(f).data for f in formularios]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los formularios')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormCreate(APIView):
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
                'message': _('Se creo el formulario '
                             'de forma exitosa')}
            serializer = FormularioSerializer(data=request.data)
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
            data['message'] = _('Error al crear el formulario')
            return Response(
                data=data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo el formulario '
                         'de forma exitosa')}
        try:
            formulario = Formulario.objects.get(pk=pk)
            if not formulario.se_puede_modificar():
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido actualizar un '
                                    'formulario con calificaciones')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = FormularioSerializer(
                    formulario, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=data, status=status.HTTP_200_OK)
                else:
                    data['status'] = 'ERROR'
                    data['message'] = json.dumps(serializer.errors)
                    data['errors'] = serializer.errors
                    return Response(
                        data=data, status=status.HTTP_400_BAD_REQUEST)
        except Formulario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe el formulario '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'el formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion del '
                         'formulario de forma exitosa'),
            'form': None}
        try:
            formulario = Formulario.objects.get(pk=pk)
            data['form'] = FormularioSerializer(formulario).data
            return Response(data=data, status=status.HTTP_200_OK)
        except Formulario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe el formulario '
                                'para obtener el detalle')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'del formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino el formulario '
                         'de forma exitosa')}
        try:
            formulario = Formulario.objects.get(pk=pk)
            if not formulario.se_puede_modificar():
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar un '
                                    'formulario con calificaciones')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                formulario.delete()
            return Response(data=data, status=status.HTTP_200_OK)
        except Formulario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe el formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar el formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormHide(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se oculto el formulario '
                         'de forma exitosa')}
        try:
            formulario = Formulario.objects.get(pk=pk)
            formulario.ocultar()
            return Response(data=data, status=status.HTTP_200_OK)
        except Formulario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al ocultar el formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FormShow(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se desoculto el formulario '
                         'de forma exitosa')}
        try:
            formulario = Formulario.objects.get(pk=pk)
            formulario.desocultar()
            return Response(data=data, status=status.HTTP_200_OK)
        except Formulario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al desocultar el formulario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
