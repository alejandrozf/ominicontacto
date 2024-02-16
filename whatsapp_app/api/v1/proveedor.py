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
from django.contrib.postgres.fields import JSONField
from django.utils.functional import cached_property
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

from whatsapp_app.models import ConfiguracionProveedor


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    provider_type = serializers.IntegerField(source='tipo_proveedor')
    configuration = serializers.JSONField(source='configuracion')


class CreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    provider_type = serializers.IntegerField(source='tipo_proveedor')
    configuration = serializers.JSONField(source='configuracion')

    class Meta:
        model = ConfiguracionProveedor
        fields = [
            "id",
            "name",
            "provider_type",
            "configuration"
        ]

    def validate_configuracion(self, configuration):
        tipo_proveedor = self.initial_data.get('provider_type')
        if tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'api_key' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        if tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'business_id' not in configuration\
                    or 'token_de_acceso' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        return configuration


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    provider_type = serializers.IntegerField(source='tipo_proveedor')
    configuration = serializers.JSONField(source='configuracion')


class UpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')
    provider_type = serializers.IntegerField(source='tipo_proveedor')
    configuration = serializers.JSONField(source='configuracion')

    class Meta:
        model = ConfiguracionProveedor
        fields = [
            "id",
            "name",
            "provider_type",
            "configuration"
        ]

    @cached_property
    def _readable_fields(self):
        return [f for f in self.fields.values()
                if not f.write_only and f.field_name in self.initial_data]

    def validate_configuracion(self, configuration):
        if self.initial_data.get('provider_type'):
            tipo_proveedor = self.initial_data.get('tipo_proveedor')
        else:
            tipo_proveedor = self.instance.tipo_proveedor
        if tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            if 'api_key' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        if tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            if 'business_id' not in configuration\
                    or 'token_de_acceso' not in configuration:
                raise serializers.ValidationError({
                    'error': _('Configuración incorrecta para el tipo de proveedor')})
        return configuration


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = ConfiguracionProveedor.objects.filter(
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
                    message=_('Se obtuvieron las configuraciones de proveedor de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las configuraciones de proveedor')),
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
                        message=_('Se creo la configuaración de proveedor de forma exitosa'),
                        data=serializer.data),
                    status=status.HTTP_201_CREATED)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return response.Response(
                data=get_response_data(message=_('Error al crear la configuaración de proveedor')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = ConfiguracionProveedor.objects.filter(
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
                    message=_('Se obtuvo la configuración del proveedor de forma exitosa')),
                status=status.HTTP_200_OK)
        except ConfiguracionProveedor.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuración del proveedor no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la configuración del proveedor')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            queryset = ConfiguracionProveedor.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            serializer = UpdateSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        data=serializer.data,
                        message=_('Se actualizó la configuración del proveedor de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except ConfiguracionProveedor.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuración del proveedor no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar la configuaración del proveedor')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            queryset = ConfiguracionProveedor.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            if not instance.lineas.filter(is_active=True):
                instance.delete()
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se elimino la Configuración del proveedor de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Proveedor con líneas activas.')),
                    status=status.HTTP_401_UNAUTHORIZED)
        except ConfiguracionProveedor.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Configuración del proveedor no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al eliminar la Configuración del proveedor')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
