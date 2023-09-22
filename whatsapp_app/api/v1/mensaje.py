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
from whatsapp_app.models import ConversacionWhatsapp


class MensajeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    conversation = serializers.PrimaryKeyRelatedField(queryset=ConversacionWhatsapp.objects.all())
    contact_data = serializers.JSONField(source='conversation.client')
    timestamp = serializers.IntegerField()
    content = serializers.JSONField()
    origen = serializers.CharField()
    sender = serializers.JSONField()
    type = serializers.CharField()


class MensajeTextCreateSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    content = serializers.CharField()
    sender = serializers.IntegerField()


class MensajeAtachmentCreateSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    content = serializers.CharField()
    sender = serializers.IntegerField()


class MensajePlantillaCreateSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    content = serializers.CharField()
    sender = serializers.IntegerField()


class MensajeWhatsappTemplateCreateSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    content = serializers.CharField()
    sender = serializers.IntegerField()


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
