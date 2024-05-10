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

# APIs para visualizar destinos
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data

from whatsapp_app.api.v1.plantilla_mensaje import ListSerializer as PlantillaMensajeListSerializer
from whatsapp_app.models import GrupoPlantillaMensaje
from whatsapp_app.models import PlantillaMensaje
from ominicontacto_app.models import Campana


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    templates = PlantillaMensajeListSerializer(read_only=True, many=True, source='plantillas')


class CreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    templates = serializers.PrimaryKeyRelatedField(
        allow_empty=False, many=True, queryset=PlantillaMensaje.objects.all(), source='plantillas')

    class Meta:
        model = GrupoPlantillaMensaje
        fields = [
            'id',
            'name',
            'templates',
        ]


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    templates = PlantillaMensajeListSerializer(read_only=True, many=True, source='plantillas')


class UpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    templates = serializers.PrimaryKeyRelatedField(
        allow_empty=False, many=True, queryset=PlantillaMensaje.objects.all(), source='plantillas')

    class Meta:
        model = GrupoPlantillaMensaje
        fields = [
            'id',
            'name',
            'templates',
        ]


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = GrupoPlantillaMensaje.objects.filter(is_active=True)
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los grupo plantilla mensaje de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener los destinos')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            serializer = CreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                    updated_by=request.user,
                )
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se creo grupo plantilla mensaje de forma exitosa'),
                        data=serializer.data),
                    status=status.HTTP_201_CREATED)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return response.Response(
                data=get_response_data(message=_('Error al crear el grupo plantilla mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = GrupoPlantillaMensaje.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = RetrieveSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo grupo plantilla mensaje de forma exitosa')),
                status=status.HTTP_200_OK)
        except GrupoPlantillaMensaje.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Grupo plantilla mensaje no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener grupo plantilla mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            queryset = GrupoPlantillaMensaje.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = UpdateSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        data=serializer.data,
                        message=_('Se actualizó grupo plantilla mensaje de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except GrupoPlantillaMensaje.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Grupo plantilla mensaje no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar grupo plantilla mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            queryset = GrupoPlantillaMensaje.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            if not instance.configuracionwhatsapp.exclude(campana__estado=Campana.ESTADO_BORRADA):
                instance.delete()
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se elimino grupo plantilla mensaje de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Grupo plantilla está siendo usado por alguna campaña activa')),
                    status=status.HTTP_401_UNAUTHORIZED)
        except GrupoPlantillaMensaje.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Grupo plantilla mensaje no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al eliminar Grupo plantilla mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
