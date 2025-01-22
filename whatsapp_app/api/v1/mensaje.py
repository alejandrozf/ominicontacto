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
import json
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp
from whatsapp_app.api.v1.contacto import ListSerializer as ContactoSerializer


class MensajeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    message_id = serializers.CharField()
    conversation = serializers.PrimaryKeyRelatedField(queryset=ConversacionWhatsapp.objects.all())
    contact_data = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField()
    content = serializers.SerializerMethodField()
    origin = serializers.CharField(source='origen')
    sender = serializers.JSONField()
    type = serializers.CharField()
    status = serializers.CharField()
    fail_reason = serializers.CharField()
    file = serializers.FileField()

    def get_contact_data(self, obj):
        if obj.conversation.client:
            serializer = ContactoSerializer(obj.conversation.client)
            return serializer.data
        return {}

    def get_content(self, obj):
        if obj.content:
            if obj.type == 'list':
                content = json.loads(obj.content[0]['text'])
                text = content['title'] + '\n'
                options = content['items'][0]['options']
                for option in options:
                    text += "{}-{} \n"\
                            .format(option['title'],
                                    option['description'] if 'description' in option else '')
                return {'text': text}
            elif obj.type == 'list_reply':
                text = "Reply-option:\n {}-{}"\
                    .format(obj.content['title'],
                            obj.content['description'] if 'description' in obj.content else '')
                return {'text': text}
            return obj.content
        return {}


class MensajeTextCreateSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    content = serializers.CharField()
    sender = serializers.IntegerField()


class MensajeAtachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeWhatsapp
        fields = [
            'id',
            'conversation',
            'sender',
            'file'
        ]


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
