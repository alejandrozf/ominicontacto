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

# APIs para visualizar proveedores
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.api.v1.plantilla_mensaje import ListSerializer as ListPlantillaMensajeSerializer
from whatsapp_app.api.v1.template_whatsapp import ListSerializer as ListTemplateWhatsappSerializer
from whatsapp_app.models import ConfiguracionWhatsappCampana
from ominicontacto_app.models import Campana
from whatsapp_app.models import Linea
from whatsapp_app.models import GrupoTemplateWhatsapp
from whatsapp_app.models import GrupoPlantillaMensaje


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing = serializers.IntegerField(source='campana.id')
    line = serializers.IntegerField(source='linea.id')
    group_template_whatsapp = serializers.IntegerField(source='grupo_template_whatsapp.id')
    group_template_message = serializers.IntegerField(source='grupo_plantilla_whatsapp.id')
    service_level = serializers.IntegerField(source='nivel_servicio')


class CreateSerializer(serializers.ModelSerializer):
    campaing = serializers.PrimaryKeyRelatedField(
        queryset=Campana.objects_default.all(), source='campana')
    line = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Linea.objects.all(), required=False, source='linea')
    group_template_whatsapp = serializers.PrimaryKeyRelatedField(
        queryset=GrupoTemplateWhatsapp.objects.all(), source='grupo_template_whatsapp')
    group_template_message = serializers.PrimaryKeyRelatedField(
        queryset=GrupoPlantillaMensaje.objects.all(), source='grupo_plantilla_whatsapp')
    service_level = serializers.IntegerField(source='nivel_servicio')

    class Meta:
        model = ConfiguracionWhatsappCampana
        fields = [
            'id',
            'campaing',
            'line',
            'group_template_whatsapp',
            'group_template_message',
            'service_level'
        ]


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing = serializers.IntegerField(source='campana.id')
    line = serializers.IntegerField(source='linea.id')
    group_template_whatsapp = serializers.IntegerField(source='grupo_template_whatsapp.id')
    group_template_message = serializers.IntegerField(source='grupo_plantilla_whatsapp.id')
    service_level = serializers.IntegerField(source='nivel_servicio')


class UpdateSerializer(serializers.ModelSerializer):
    campaing = serializers.PrimaryKeyRelatedField(
        queryset=Campana.objects_default.all(), source='campana')
    line = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Linea.objects.all(), required=False, source='linea')
    group_template_whatsapp = serializers.PrimaryKeyRelatedField(
        queryset=GrupoTemplateWhatsapp.objects.all(), source='grupo_template_whatsapp')
    group_template_message = serializers.PrimaryKeyRelatedField(
        queryset=GrupoPlantillaMensaje.objects.all(), source='grupo_plantilla_whatsapp')
    service_level = serializers.IntegerField(source='nivel_servicio')

    class Meta:
        model = ConfiguracionWhatsappCampana
        fields = [
            'id',
            'campaing',
            'line',
            'group_template_whatsapp',
            'group_template_message',
            'service_level'
        ]


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = ConfiguracionWhatsappCampana.objects.filter(is_active=True)
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las configuraciones de whatsapp de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print("Error: ", e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las configuraciones de whatsapp')),
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
                        message=_('Se creo la configuraciones de whatsapp de forma exitosa'),
                        data=serializer.data),
                    status=status.HTTP_201_CREATED)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al crear la configuraciones de whatsapp')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = ConfiguracionWhatsappCampana.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = RetrieveSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo la configuracion de whatsapp de forma exitosa')),
                status=status.HTTP_200_OK)
        except ConfiguracionWhatsappCampana.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuracion de whatsapp no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la configuracion de whatsapp')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            queryset = ConfiguracionWhatsappCampana.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = UpdateSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        data=serializer.data,
                        message=_('Se actualizó la configuracion de whatsapp de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except ConfiguracionWhatsappCampana.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuración de whatsapp no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar la configuaración de whatsapp')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            queryset = ConfiguracionWhatsappCampana.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            instance.delete()
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se elimino la configuración de whatsapp de forma exitosa')),
                status=status.HTTP_200_OK)
        except ConfiguracionWhatsappCampana.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuración de whatsapp no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al eliminar la Configuración de whatsapp')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"], url_path='templates/(?P<campana_pk>[^/.]+)/')
    def templates(self, request, campana_pk):
        configuracion = ConfiguracionWhatsappCampana.objects.filter(campana__id=campana_pk).last()
        if configuracion:
            templates = configuracion.grupo_template_whatsapp.templates.all()
            plantillas = configuracion.grupo_plantilla_whatsapp.plantillas.all()
            templates = ListTemplateWhatsappSerializer(templates, many=True)
            plantillas = ListPlantillaMensajeSerializer(plantillas, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data={
                        "message_templates": plantillas.data,
                        "whatsapp_templates": templates.data
                    }),
                status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=get_response_data(message=_('Configuración de whatsapp no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
