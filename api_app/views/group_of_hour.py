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
from django.db import models
from django.utils.translation import ugettext as _
from api_app.utils.group_of_hours import (
    eliminar_grupo_horario_config, escribir_grupo_horario_config
)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.group_of_hour import (
    GrupoHorarioSerializer)
from configuracion_telefonia_app.models import GrupoHorario


class GroupOfHourList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los grupos horarios '
                         'de forma exitosa'),
            'groupOfHours': []}
        try:
            grupos_horarios = GrupoHorario.objects.all().order_by('id')
            data['groupOfHours'] = [
                GrupoHorarioSerializer(gh).data for gh in grupos_horarios]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los grupos horarios')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupOfHourCreate(APIView):
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
                'message': _('Se creo el grupo horario '
                             'de forma exitosa')}
            serializer = GrupoHorarioSerializer(data=request.data)
            if serializer.is_valid():
                grupo_horario = serializer.save()
                if not escribir_grupo_horario_config(self, grupo_horario):
                    responseData['message'] = _('Se creo el grupo horario pero no se pudo '
                                                'cargar la configuración telefónica')
                return Response(data=responseData, status=status.HTTP_200_OK)
            else:
                responseData['status'] = 'ERROR'
                responseData['message'] = [
                    serializer.errors[key] for key in serializer.errors]
                responseData['errors'] = serializer.errors
                return Response(
                    data=responseData, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            responseData['status'] = 'ERROR'
            responseData['message'] = _('Error al crear el grupo horario')
            return Response(
                data=responseData,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupOfHourUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo el grupo horario '
                         'de forma exitosa')}
        try:
            grupo_horario = GrupoHorario.objects.get(pk=pk)
            serializer = GrupoHorarioSerializer(
                grupo_horario, data=request.data)
            if serializer.is_valid():
                serializer.save()
                if not escribir_grupo_horario_config(self, grupo_horario):
                    data['message'] = _('Se actualizo el grupo horario pero no se pudo '
                                        'cargar la configuración telefónica')
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = [
                    serializer.errors[key] for key in serializer.errors]
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except GrupoHorario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = 'No existe el grupo horario'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'el grupo horario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupOfHourDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion el grupo horario '
                         'de forma exitosa'),
            'groupOfHour': None}
        try:
            grupo_horario = GrupoHorario.objects.get(pk=pk)
            data['groupOfHour'] = GrupoHorarioSerializer(grupo_horario).data
            return Response(data=data, status=status.HTTP_200_OK)
        except GrupoHorario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = 'No existe el grupo horario'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'del grupo horario')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupOfHourDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino el grupo horario '
                         'de forma exitosa')}
        try:
            grupo_horario = GrupoHorario.objects.get(pk=pk)
            if grupo_horario.validaciones_fecha_hora.count() > 0:
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar un '
                                    'grupo horario asociado a Validacion Fecha Hora')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not eliminar_grupo_horario_config(self, grupo_horario):
                    data['message'] = _('Se elimino el grupo horario pero no se pudo '
                                        'cargar la configuración telefónica')
                grupo_horario.delete()
            return Response(data=data, status=status.HTTP_200_OK)
        except GrupoHorario.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = 'No existe el grupo horario'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except models.ProtectedError as exc:
            return Response(
                data={
                    "status": "ERROR",
                    "message": _(
                       "No está permitido eliminar el '{modelo}' porque está siendo "
                        "usado por {related}.".format(
                            modelo=_("Grupo Horario"),
                            related=", ".join(str(o) for o in exc.protected_objects),
                        )
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = 'Error al eliminar el grupo horario'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
