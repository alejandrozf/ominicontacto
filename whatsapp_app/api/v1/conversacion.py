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
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.api.v1.mensaje import (
    MensajeTextCreateSerializer, MensajeAtachmentCreateSerializer, MensajeListSerializer,
    MensajePlantillaCreateSerializer, MensajeWhatsappTemplateCreateSerializer)


class ConversacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_campana = serializers.IntegerField()
    nombre_campana = serializers.CharField()
    nombre_cliente = serializers.CharField()
    numero_cliente = serializers.CharField()
    foto = serializers.CharField()
    fecha = serializers.DateTimeField()


class ConversacionNuevaSerializer(ConversacionSerializer):
    es_transferencia_campana = serializers.BooleanField()
    cantidad_mensajes = serializers.IntegerField()


class ConversacionEnCursoSerializer(ConversacionSerializer):
    es_transferencia_agente = serializers.BooleanField()
    cantidad_mensajes_nuevos = serializers.IntegerField()


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
                "id_campana": 1,
                "nombre_campana": "nombre_campana",
                "nombre_cliente": "cliente",
                "numero_cliente": "0000000",
                "foto": "foto.jpg",
                "fecha": "23-03-08 01:30",
                "es_transferencia_campana": True,
                "cantidad_mensajes": 10
            },
            {
                "id": 2,
                "id_campana": 1,
                "nombre_campana": "nombre_campana",
                "nombre_cliente": "cliente",
                "numero_cliente": "0000000",
                "foto": "foto.jpg",
                "fecha": "23-03-08 02:30",
                "es_transferencia_campana": True,
                "cantidad_mensajes": 10
            }
        ]
        conversaciones_en_curso = [
            {
                "id": 1,
                "id_campana": 1,
                "nombre_campana": "nombre_campana",
                "nombre_cliente": "cliente",
                "numero_cliente": "0000000",
                "foto": "foto.jpg",
                "fecha": "23-03-08 01:30",
                "es_transferencia_agente": False,
                "cantidad_mensajes_nuevos": 5
            },
            {
                "id": 2,
                "id_campana": 1,
                "nombre_campana": "nombre_campana",
                "nombre_cliente": "cliente",
                "numero_cliente": "0000000",
                "foto": "foto.jpg",
                "fecha": "23-03-08 02:30",
                "es_transferencia_agente": True,
                "cantidad_mensajes_nuevos": 5
            }
        ]
        data = {
            "conversaciones_nuevas": ConversacionNuevaSerializer(
                conversaciones_nuevas, many=True).data,
            "conversaciones_en_curso": ConversacionEnCursoSerializer(
                conversaciones_en_curso, many=True).data
        }
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                data=data),
            status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["get"])
    def attend_chat(self, request, pk):
        #  agente = request.user.get_agente_profile()
        conversacion = {
            "id": 1,
            "id_campana": 1,
            "nombre_campana": "nombre_campana",
            "nombre_cliente": "cliente",
            "numero_cliente": "0000000",
            "foto": "foto.jpg",
            "fecha": "23-03-08 01:30"
        }  # Conversacion.objects.get(pk=pk)
        mensajes = [
            {
                "id": 1,
                "contenido": "Buenos días",
                "status": "",
                "fecha": "2023-03-07 01:30",
                "emisor": "cliente"
            },
            {
                "id": 2,
                "contenido": "Hola",
                "status": "",
                "fecha": "2023-03-07 01:30",
                "emisor": "cliente"
            }
        ]  # Mensajes.objects.filter(conversacion_id=pk)
        serializer_conversacion = ConversacionSerializer(conversacion)
        serializer_mensajes = MensajeListSerializer(mensajes, many=True)
        data = {
            "conversacion_otorgada": True,  # conversacion.otorgar(agente),
            "datos_de_conversacion": serializer_conversacion.data,
            "mensajes": serializer_mensajes.data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"])
    def messages(self, request, pk):
        mensajes = [
            {
                "id": 1,
                "conversacion": 1,
                "contenido": "Buenos días",
                "status": "",
                "fecha": "2023-03-07 01:30",
                "emisor": "cliente"
            },
            {
                "id": 2,
                "conversacion": 1,
                "contenido": "Hola",
                "status": "",
                "fecha": "2023-03-07 01:30",
                "emisor": "cliente"
            }
        ]  # Mensajes.objects.filter(conversacion_id=pk)
        serializer_mensajes = MensajeListSerializer(mensajes, many=True)
        data = {
            "mensajes": serializer_mensajes.data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_menssage_text(self, request, pk):
        data = request.data.copy()
        data.update({"conversacion": pk})
        serializer = MensajeTextCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_menssage_attachment(self, request, pk):
        data = request.data.copy()
        data.update({"conversacion": pk})
        serializer = MensajeAtachmentCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_template(self, request, pk):
        data = request.data.copy() #  Id Plantilla, Parámetros
        data.update({"conversacion": pk})
        serializer = MensajePlantillaCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_whatsapp_template(self, request, pk):
        data = request.data.copy() #  Id Template
        data.update({"conversacion": pk})
        serializer = MensajeWhatsappTemplateCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
            status=status.HTTP_200_OK)
