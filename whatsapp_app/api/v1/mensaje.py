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


class MensajeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    conversacion = serializers.IntegerField()
    contenido = serializers.CharField()
    status = serializers.CharField()
    fecha = serializers.DateTimeField()
    emisor = serializers.CharField()


class MensajeTextCreateSerializer(serializers.Serializer):
    conversacion = serializers.IntegerField()
    contenido = serializers.CharField()
    emisor = serializers.CharField()


class MensajeAtachmentCreateSerializer(serializers.Serializer):
    conversacion = serializers.IntegerField()
    contenido = serializers.CharField()
    emisor = serializers.CharField()


class MensajePlantillaCreateSerializer(serializers.Serializer):
    conversacion = serializers.IntegerField()
    contenido = serializers.CharField()
    emisor = serializers.CharField()


class MensajeWhatsappTemplateCreateSerializer(serializers.Serializer):
    conversacion = serializers.IntegerField()
    contenido = serializers.CharField()
    emisor = serializers.CharField()


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = []
            serializer = MensajeListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los mensajes de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener los mensajes')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
