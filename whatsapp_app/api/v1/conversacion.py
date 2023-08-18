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
import datetime
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
from whatsapp_app.api.v1.mensaje import (
    MensajeTextCreateSerializer, MensajeAtachmentCreateSerializer, MensajeListSerializer,
    MensajePlantillaCreateSerializer, MensajeWhatsappTemplateCreateSerializer)
MESSAGE_SENDERS = {
    'AGENT': 0,
    'CLIENT': 1
}
MESSAGE_STATUS = {
    'SENDING': 0,
    'SENT': 1,
    'DELIVERED': 2,
    'READ': 3,
    'ERROR': 4
}


class ConversacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing_id = serializers.IntegerField()
    campaing_name = serializers.CharField()
    client_name = serializers.CharField()
    client_number = serializers.CharField()
    photo = serializers.CharField()
    date = serializers.DateTimeField()


class ConversacionNuevaSerializer(ConversacionSerializer):
    is_transfer_campaing = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ConversacionEnCursoSerializer(ConversacionSerializer):
    is_transfer_agent = serializers.BooleanField()
    number_messages = serializers.IntegerField()


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = []
            serializer = ConversacionSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las conversaciones de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las conversaciones')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def agent_chats_lists(self, request):
        #  agente = request.user.get_agente_profile()
        conversaciones_nuevas = [
            {
                "id": 1,
                "campaing_id": 1,
                "campaing_name": "nombre_campana",
                "client_name": "7221313052",
                "client_number": "7221313052",
                "photo": "foto.jpg",
                "date": datetime.datetime.now(),
                "is_transfer_campaing": True,
                "number_messages": 2
            },
            {
                "id": 2,
                "campaing_id": 1,
                "campaing_name": "nombre_campana",
                "client_name": "7221313052",
                "client_number": "7221313052",
                "photo": "foto.jpg",
                "date": datetime.datetime.now(),
                "is_transfer_campaing": True,
                "number_messages": 5
            }
        ]
        conversaciones_en_curso = [
            {
                "id": 3,
                "campaing_id": 1,
                "campaing_name": "nombre_campana",
                "client_name": "Cliente 1",
                "client_number": "0000000",
                "photo": "foto.jpg",
                "date": datetime.datetime.now(),
                "is_transfer_agent": True,
                "number_messages": 10
            },
            {
                "id": 4,
                "campaing_id": 1,
                "campaing_name": "nombre_campana",
                "client_name": "Cliente 2",
                "client_number": "0000000",
                "photo": "foto.jpg",
                "date": datetime.datetime.now(),
                "is_transfer_agent": True,
                "number_messages": 4
            }
        ]
        data = {
            "conversations_new": ConversacionNuevaSerializer(
                conversaciones_nuevas, many=True).data,
            "conversations_in_progress": ConversacionEnCursoSerializer(
                conversaciones_en_curso, many=True).data
        }
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                data=data),
            status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"])
    def attend_chat(self, request, pk):
        #  agente = request.user.get_agente_profile()
        conversacion = {
            "id": 1,
            "campaing_id": 1,
            "campaing_name": "nombre_campana",
            "client_name": "cliente",
            "client_number": "0000000",
            "photo": "foto.jpg",
            "date": "23-03-08 01:30",
        }  # Conversacion.objects.get(pk=pk)
        mensajes = [
            {
                "id": 1,
                "conversation": 1,
                "content": "Buenos días",
                "status": "",
                "date": "2023-03-07 01:30",
                "sender": "cliente"
            },
            {
                "id": 2,
                "conversation": 1,
                "content": "Hola",
                "status": "",
                "date": "2023-03-07 01:30",
                "sender": "cliente"
            }
        ]  # Mensajes.objects.filter(conversacion_id=pk)
        serializer_conversacion = ConversacionSerializer(conversacion)
        serializer_mensajes = MensajeListSerializer(mensajes, many=True)
        data = {
            "conversation_granted": True,  # conversacion.otorgar(agente),
            "conversation_data": serializer_conversacion.data,
            "messages": serializer_mensajes.data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def assign_contact(self, request, pk):
        #  contact_pk = request.data.get('contact_pk')
        #  conversacion = Conversacion.objects.get(pk=pk)
        #  conversacion.contacto = contact_pk
        #  conversacion.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS,),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"])
    def messages(self, request, pk):
        mensajes = [
            {
                "id": 1,
                "conversation": 1,
                "content": "Buenos días",
                "status": MESSAGE_STATUS['SENDING'],
                "date": "2023-03-07 01:30",
                "user": "Cliente EMI",
                "sender": MESSAGE_SENDERS['CLIENT']
            },
            {
                "id": 2,
                "conversation": 1,
                "content": "Buenas, en que puedo ayudarte",
                "status": MESSAGE_STATUS['SENT'],
                "date": "2023-03-07 01:30",
                "user": "Agente Sofia",
                "sender": MESSAGE_SENDERS['AGENT']
            },
            {
                "id": 3,
                "conversation": 1,
                "content": "Quiero agregar agentes a campaña, como lo hago?",
                "status": MESSAGE_STATUS['DELIVERED'],
                "date": "2023-03-07 01:30",
                "user": "Cliente EMI",
                "sender": MESSAGE_SENDERS['CLIENT']
            },
            {
                "id": 4,
                "conversation": 1,
                "content": "Claro, a que tipo de campana te refieres?",
                "status": MESSAGE_STATUS['READ'],
                "date": "2023-03-07 01:30",
                "user": "Agente Sofia",
                "sender": MESSAGE_SENDERS['AGENT']
            },
            {
                "id": 5,
                "conversation": 1,
                "content": "Son de tipo Inbount",
                "status": MESSAGE_STATUS['ERROR'],
                "date": "2023-03-07 01:30",
                "user": "Cliente EMI",
                "sender": MESSAGE_SENDERS['CLIENT']
            }
        ]
        # if 'message_id' in self.request.GET:
        #     last_message = Mensajes.objects.get(id=message_id).date
        #     mensajes =\
        #         Mensajes.objects.filter(chat_id=pk, date__lt=last_message.date)
        #         .order_by('-date')[:MESSAGE_LIMIT]
        # else:
        #     mensajes = Mensajes.objects.filter(chat_id=pk).order_by('-date')[:MESSAGE_LIMIT]
        serializer_mensajes = MensajeListSerializer(mensajes, many=True)
        data = {
            "messages": serializer_mensajes.data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_text(self, request, pk):
        # sender = request.user.get_agente_profile()
        data = request.data.copy()
        data.update({"conversation": pk, "sender": MESSAGE_SENDERS['AGENT']})
        serializer = MensajeTextCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        # orquestador_response = send_message_text(serializer.data) # orquestador
        orquestador_response = {
            "status": MESSAGE_STATUS['SENT'],
            "message_id": "1",
            "date": "01-01-2022 09:10"
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=orquestador_response),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_attachment(self, request, pk):
        # sender = request.user.get_agente_profile()
        data = request.data.copy()
        data.update({"conversation": pk, "sender": MESSAGE_SENDERS['AGENT']})
        serializer = MensajeAtachmentCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        # orquestador_response = send_message_attachment(serializer.data) # orquestador
        orquestador_response = {
            "status": MESSAGE_STATUS['SENT'],
            "message_id": "1",
            "date": "01-01-2022 09:10"
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=orquestador_response),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_template(self, request, pk):
        # sender = request.user.get_agente_profile()
        data = request.data.copy()  # Id Plantilla, Parámetros
        data.update({"conversation": pk, "sender": MESSAGE_SENDERS['AGENT']})
        serializer = MensajePlantillaCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        # orquestador_response = send_message_template(serializer.data) # orquestador
        orquestador_response = {
            "status": MESSAGE_STATUS['SENT'],
            "message_id": "1",
            "date": "01-01-2022 09:10"
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=orquestador_response),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_whatsapp_template(self, request, pk):
        # sender = request.user.get_agente_profile()
        data = request.data.copy()  # Id Template
        data.update({"conversation": pk, "sender": MESSAGE_SENDERS['AGENT']})
        serializer = MensajeWhatsappTemplateCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        # orquestador_response = send_message_whatsapp_template(serializer.data) # orquestador
        orquestador_response = {
            "status": MESSAGE_STATUS['SENT'],
            "message_id": "1",
            "date": "01-01-2022 09:10"
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=orquestador_response),
            status=status.HTTP_200_OK)
