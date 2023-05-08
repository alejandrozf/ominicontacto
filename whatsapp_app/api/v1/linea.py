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

# APIs para visualizar lineas
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import JSONField
from django.db.models import F
from django.db.models import Func
from django.db.models import Value
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data

from whatsapp_app.models import Linea
from whatsapp_app.models import ConfiguracionProveedor
from configuracion_telefonia_app.models import DestinoEntrante, GrupoHorario
from whatsapp_app.models import PlantillaMensaje


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.IntegerField(source='proveedor.id')
    configuration = serializers.JSONField(source='configuracion')
    destination = serializers.IntegerField(source='destino.id', required=False)
    schedule = serializers.IntegerField(source='horario.id', required=False)
    destination_type = serializers.IntegerField(source='destino.tipo', required=False)
    welcome_message = serializers.IntegerField(source='mensaje_bienvenida.id', required=False)
    farewell_message = serializers.IntegerField(source='mensaje_despedida.id', required=False)
    afterhours_message = serializers.IntegerField(source='mensaje_fueradehora.id', required=False)


class CreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.PrimaryKeyRelatedField(
        queryset=ConfiguracionProveedor.objects.all(), source='proveedor')
    configuration = serializers.JSONField(source='configuracion')
    destination = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=DestinoEntrante.objects.all(), required=False, source='destino')
    schedule = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=GrupoHorario.objects.all(), required=False, source='horario')
    welcome_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_bienvenida')
    farewell_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_despedida')
    afterhours_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_fueradehora')

    class Meta:
        model = Linea
        fields = [
            'id',
            'name',
            'number',
            'provider',
            'configuration',
            'destination',
            'schedule',
            'welcome_message',
            'farewell_message',
            'afterhours_message'
        ]

    def validate_configuracion(self, configuration):
        proveedor_id = self.initial_data.get('provider')
        proveedor = ConfiguracionProveedor.objects.get(pk=proveedor_id)
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'app_name' not in configuration\
                    or 'app_id' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'app_id' not in configuration\
                    or 'token_de_verificacion' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        return configuration


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.IntegerField(source='proveedor.id')
    configuration = serializers.JSONField(source='configuracion')
    destination = serializers.IntegerField(source='destino.id', required=False)
    schedule = serializers.IntegerField(source='horario.id', required=False)
    destination_type = serializers.IntegerField(source='destino.tipo', required=False)
    welcome_message = serializers.IntegerField(source='mensaje_bienvenida.id', required=False)
    farewell_message = serializers.IntegerField(source='mensaje_despedida.id', required=False)
    afterhours_message = serializers.IntegerField(source='mensaje_fueradehora.id', required=False)


class UpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    number = serializers.CharField(source='numero')
    provider = serializers.PrimaryKeyRelatedField(
        queryset=ConfiguracionProveedor.objects.all(), source='proveedor')
    configuration = serializers.JSONField(source='configuracion')
    destination = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=DestinoEntrante.objects.all(),
        required=False, source='destino')
    schedule = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=GrupoHorario.objects.all(),
        required=False, source='horario')
    welcome_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_bienvenida')
    farewell_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_despedida')
    afterhours_message = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=PlantillaMensaje.objects.all(),
        required=False, source='mensaje_fueradehora')

    class Meta:
        model = Linea
        fields = [
            'id',
            'name',
            'number',
            'provider',
            'configuration',
            'destination',
            'schedule',
            'welcome_message',
            'farewell_message',
            'afterhours_message'
        ]

    def validate_configuracion(self, configuration):
        if self.initial_data.get('provider'):
            proveedor_id = self.initial_data.get('provider')
            proveedor = ConfiguracionProveedor.objects.get(pk=proveedor_id)
        else:
            proveedor = self.instance.proveedor
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'app_name' not in configuration\
                    or 'app_id' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'app_id' not in configuration\
                    or 'token_de_verificacion' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        return configuration


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = Linea.objects.filter(
                is_active=True
            ).annotate(
                created_jsonb=Func(
                    Value("date"),
                    Func(F("created_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("created_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
                updated_jsonb=Func(
                    Value("date"),
                    Func(F("updated_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("updated_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            ).order_by(
                "nombre",
            )
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las líneas de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las líneas')),
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
                        message=_('Se creo la línea de forma exitosa'),
                        data=serializer.data),
                    status=status.HTTP_201_CREATED)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return response.Response(
                data=get_response_data(message=_('Error al crear la línea')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = Linea.objects.filter(
                is_active=True
            ).annotate(
                created_jsonb=Func(
                    Value("date"),
                    Func(F("created_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("created_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
                updated_jsonb=Func(
                    Value("date"),
                    Func(F("updated_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("updated_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            )
            instance = queryset.get(pk=pk)
            serializer = RetrieveSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo la línea de forma exitosa')),
                status=status.HTTP_200_OK)
        except Linea.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Línea no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la línea')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            queryset = Linea.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = UpdateSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        data=serializer.data,
                        message=_('Se actualizó la línea de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Linea.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Línea no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar la línea')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            queryset = Linea.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            instance.delete()
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se elimino la línea de forma exitosa')),
                status=status.HTTP_200_OK)
        except Linea.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Línea no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al eliminar la línea')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
