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
import json
from django.conf import settings
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
from orquestador_app.core.send_menssage import sync_templates
from orquestador_app.core.media_management import meta_get_media_template


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    line = serializers.IntegerField(source='linea.id')
    name = serializers.CharField(source='nombre')
    identifier = serializers.CharField(source='identificador')
    identifier_media = serializers.CharField(source='identificador_media')
    link_media = serializers.CharField()
    text_header = serializers.CharField(source='texto_header')
    text = serializers.CharField(source='texto')
    language = serializers.CharField(source='idioma')
    status = serializers.CharField()
    created = serializers.CharField(source='creado')
    updated = serializers.CharField(source='modificado')
    type = serializers.CharField(source='tipo')
    category = serializers.CharField(source='categoria')
    is_active = serializers.BooleanField(default=True)


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    line = serializers.IntegerField(source='linea.id')
    name = serializers.CharField(source='nombre')
    identifier = serializers.CharField(source='identificador')
    text_header = serializers.CharField(source='texto_header')
    text = serializers.CharField(source='texto')
    language = serializers.CharField(source='idioma')
    status = serializers.CharField()
    created = serializers.CharField(source='creado')
    updated = serializers.CharField(source='modificado')
    type = serializers.CharField(source='tipo')
    category = serializers.CharField(source='categoria')
    is_active = serializers.BooleanField(default=True)


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
            templates = sync_templates(linea)
            if proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
                for attrs in templates:
                    containerMeta = json.loads(attrs['containerMeta'])
                    if 'buttons' in containerMeta:
                        tipo = 'BUTTON'
                    else:
                        tipo = attrs['templateType']
                    linea.templates_whatsapp.update_or_create(
                        identificador=attrs['id'], defaults={
                            'nombre': attrs['elementName'],
                            'texto': attrs['data'],
                            'idioma': attrs['languageCode'],
                            'status': attrs['status'],
                            'creado': attrs['createdOn'],
                            'modificado': attrs['modifiedOn'],
                            'tipo': tipo,
                            'categoria': attrs['category'],
                            'is_active': attrs['status'] == 'APPROVED',
                            'identificador_media':
                                containerMeta['mediaId'] if 'mediaId' in containerMeta else '',
                            'link_media':
                                containerMeta['mediaUrl'] if 'mediaUrl' in containerMeta else '',
                        }
                    )
            elif proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
                for attrs in templates:
                    tipo = 'TEXT'
                    texto = ''
                    texto_header = ''
                    link_template_media = ''
                    for comp in attrs['components']:
                        comp_type = comp.get('type')
                        if comp_type == 'HEADER':
                            if comp.get('format') in ['IMAGE', 'VIDEO', 'DOCUMENT']:
                                tipo = comp.get('format')
                                example = comp.get('example')
                                nombre_archivo = meta_get_media_template(
                                    linea, example['header_handle'][0]
                                )
                                domain = request.build_absolute_uri('/')[:-1]
                                # domain = "https://nominally-hopeful-condor.ngrok-free.app"
                                url_media = domain + settings.MEDIA_URL + 'archivos_whatsapp/'
                                link_template_media = url_media + nombre_archivo
                            if 'text' in comp:
                                texto_header = comp.get('text')
                        if comp_type == 'BUTTONS':
                            tipo = 'BUTTONS'
                            buttons = comp.get('buttons', [])
                        if comp_type == 'BODY':
                            if 'text' in comp:
                                texto = comp.get('text')
                    linea.templates_whatsapp.update_or_create(
                        identificador=attrs['id'], defaults={
                            'nombre': attrs['name'],
                            'texto_header': texto_header,
                            'texto': texto,
                            'botones': buttons if tipo == 'BUTTONS' else [],
                            'idioma': attrs['language'],
                            'status': attrs['status'],
                            'tipo': tipo,
                            'categoria': attrs['category'],
                            'is_active': attrs['status'] == 'APPROVED',
                            'link_media': link_template_media
                        }
                    )
            else:
                raise NotImplementedError()

            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los templates de whatsapp de forma exitosa')),
                status=status.HTTP_200_OK)
        except Exception as e:
            print("error >>>>>>>>>>>", e)
            return response.Response(
                data=get_response_data(message=_(str(e))),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"], url_path='status_change/(?P<linea_pk>[^/.]+)/')
    def status_change(self, request, pk, linea_pk):
        try:
            linea = Linea.objects.get(pk=linea_pk)
            template = linea.templates_whatsapp.filter(pk=pk).last()
            if template:
                template.is_active = not template.is_active
                template.save()
                return response.Response(
                    data=get_response_data(
                        message=_('Se cambio el estado del template de forma exitosa'),
                        status=HttpResponseStatus.SUCCESS),
                    status=status.HTTP_200_OK)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR,
                    message=_('No tiene permiso para esta accion'),
                    data={}),
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return response.Response(
                data=get_response_data(message=_(str(e))),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(detail=False, methods=["get"], url_path='available_templates/(?P<linea_pk>[^/.]+)/')
    # def conversation_templates(self, request, linea_pk):
    #     try:
    #         linea = Linea.objects.get(pk=linea_pk)
    #         templates = linea.templates_whatsapp.filter(is_active=True)
    #         serializer = ListSerializer(templates, many=True)
    #         return response.Response(
    #             data=get_response_data(
    #                 status=HttpResponseStatus.SUCCESS,
    #                 message=_('Se obtuvieron las plantillas de forma exitosa'),
    #                 data=serializer.data),
    #             status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print("********************************", e)
    #         return response.Response(
    #             data=get_response_data(message=_(str(e))),
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(detail=False, methods=["get"], url_path='campaing_templates/(?P<campaing_pk>[^/.]+)/')
    # def campaing_templates(self, request, campaing_pk):
    #     try:
    #         campana = Campana.objects.get(pk=campaing_pk)
    #         if campana.linea:
    #             templates = campana.linea.templates_whatsapp.filter(is_active=True)
    #             serializer = ListSerializer(templates, many=True)
    #             return response.Response(
    #                 data=get_response_data(
    #                     status=HttpResponseStatus.SUCCESS,
    #                     message=_('Se obtuvieron los templates de forma exitosa'),
    #                     data=serializer.data),
    #                 status=status.HTTP_200_OK)
    #         return response.Response(
    #             data=get_response_data(
    #                 status=HttpResponseStatus.SUCCESS,
    #                 message=_('No tiene templates disponibles'),
    #                 data={}),
    #             status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print("********************************", e)
    #         return response.Response(
    #             data=get_response_data(message=_(str(e))),
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
