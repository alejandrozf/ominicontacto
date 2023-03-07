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
import requests
import json
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data

from whatsapp_app.models import Linea, ConfiguracionProveedor, TemplateWhatsapp


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    linea = serializers.IntegerField(source='linea.id')
    nombre = serializers.CharField()
    identificador = serializers.CharField()
    texto = serializers.CharField()
    idioma = serializers.CharField()
    status = serializers.CharField()
    creado = serializers.CharField()
    modificado = serializers.CharField()
    tipo = serializers.CharField()


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    linea = serializers.IntegerField(source='linea.id')
    nombre = serializers.CharField()
    identificador = serializers.CharField()
    texto = serializers.CharField()
    idioma = serializers.CharField()
    status = serializers.CharField()
    creado = serializers.CharField()
    modificado = serializers.CharField()
    tipo = serializers.CharField()


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = TemplateWhatsapp.objects.all().order_by("nombre")
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las plantillas de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las plantillas')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            instance = TemplateWhatsapp.objects.get(pk=pk)
            serializer = RetrieveSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo el template de forma exitosa')),
                status=status.HTTP_200_OK)
        except TemplateWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Template no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener el Template')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path='sincronizar_templates/(?P<linea_pk>[^/.]+)/')
    def sincronizar_templates(self, request, linea_pk):
        try:
            linea = Linea.objects.get(pk=linea_pk)
            proveedor = linea.proveedor
            if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
                appname = linea.configuracion['app_name']
                apikey = proveedor.configuracion['api_key']
                url = 'https://api.gupshup.io/sm/api/v1/template/list/{}'.format(appname)  # mover
                headers = {"apikey": apikey}
                respuesta = requests.get(url, headers=headers)
                templates = json.loads(respuesta.text)['templates']
                TemplateWhatsapp.objects.filter(linea=linea).delete()
                TemplateWhatsapp.objects.bulk_create(
                    [TemplateWhatsapp(
                        linea=linea,
                        identificador=attrs['id'],
                        nombre=attrs['elementName'],
                        texto=attrs['data'],
                        idioma=attrs['languageCode'],
                        status=attrs['status'],
                        creado=attrs['createdOn'],
                        modificado=attrs['modifiedOn'],
                        tipo=attrs['templateType'],
                        categoria=attrs['category']
                    ) for attrs in templates],
                    ignore_conflicts=False
                )
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los templates de whatsapp de forma exitosa')),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al sincronizar los templates')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
