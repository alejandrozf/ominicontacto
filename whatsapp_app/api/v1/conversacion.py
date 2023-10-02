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
from django.utils import timezone
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
from whatsapp_app.api.v1.mensaje import MensajeListSerializer
from whatsapp_app.models import (
    ConversacionWhatsapp, MensajeWhatsapp, PlantillaMensaje,
    ConfiguracionWhatsappCampana, TemplateWhatsapp)
from ominicontacto_app.models import Campana, AgenteProfile
from notification_app.notification import AgentNotifier
from orquestador_app.core.gupshup_send_menssage import send_template_message, send_text_message

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
MESSAGE_LIMIT = 2


class ConversacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    conversation_id = serializers.CharField()
    conversation_type = serializers.CharField()
    campaing_id = serializers.PrimaryKeyRelatedField(
        source='campana', queryset=Campana.objects.all())
    campaing_name = serializers.CharField(source='campana.nombre')
    destination = serializers.CharField()
    client = serializers.SerializerMethodField()
    agent = serializers.PrimaryKeyRelatedField(queryset=AgenteProfile.objects.all())
    is_active = serializers.BooleanField(default=True)
    expire = serializers.DateTimeField()
    timestamp = serializers.DateTimeField()
    message_number = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    line_number = serializers.SerializerMethodField()

    def get_message_number(self, obj):
        return obj.mensajes.count()

    def get_line_number(self, obj):
        campana = obj.campana
        configuracion = ConfiguracionWhatsappCampana.objects.filter(campana=campana).last()
        return configuracion.linea.numero

    def get_messages(self, obj):
        return MensajeListSerializer(obj.mensajes.all().order_by('timestamp'), many=True).data

    def get_client(self, obj):
        if obj.client:
            return obj.client.obtener_datos()
        return None


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
            request.user.get_agente_profile()
            conversaciones_nuevas = ConversacionWhatsapp.objects.filter(agent=None)
            conversaciones_en_curso = ConversacionWhatsapp.objects.exclude(agent=None)
            conversaciones_nuevas = ConversacionSerializer(conversaciones_nuevas, many=True)
            conversaciones_en_curso = ConversacionSerializer(conversaciones_en_curso, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las conversaciones de forma exitosa'),
                    data={
                        "new_conversations": conversaciones_nuevas.data,
                        "inprogress_conversations": conversaciones_en_curso.data}),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las conversaciones')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = ConversacionWhatsapp.objects.all()
            instance = queryset.get(pk=pk)
            serializer = ConversacionSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo la conversacion de forma exitosa')),
                status=status.HTTP_200_OK)
        except ConversacionWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Conversacion no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def agent_chats_lists(self, request):
        agente = request.user.get_agente_profile()
        conversaciones_asignadas = agente.conversaciones.all()
        conversaciones_en_curso = ConversacionSerializer(conversaciones_asignadas, many=True)
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                data=conversaciones_en_curso.data),
            status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"])
    def attend_chat(self, request, pk):
        try:
            agente = request.user.get_agente_profile()
            conversacion = ConversacionWhatsapp.objects.get(pk=pk)
            conversation_granted = conversacion.otorgar_conversacion(agente),
            mensajes = conversacion.mensajes.all()
            serializer_conversacion = ConversacionSerializer(conversacion)
            serializer_mensajes = MensajeListSerializer(mensajes, many=True)
            data = {
                "conversation_granted": conversation_granted,
                "conversation_data": serializer_conversacion.data,
                "messages": serializer_mensajes.data
            }
            print(data)
            agentes = conversacion.campana.obtener_agentes()
            agent_notifier = AgentNotifier()
            for agente in agentes:
                print("attend_chat...")
                message = {
                    'chat_id': conversacion.id,
                    'campaign_id': conversacion.campana.pk,
                    'campaign_name': conversacion.campana.nombre,
                    'agent': agente.user.pk
                }
                agent_notifier.notify_whatsapp_chat_attended(agente.user_id, message)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS, data={},
                    message=_('Se asignó la conversación de forma exitosa')),
                status=status.HTTP_200_OK
            )
        except ConversacionWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No se puede asignar una conversación que no existe')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error al asignar la conversación")
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al asignar la conversación')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def assign_contact(self, request, pk):
        contact_pk = request.data.get('contact_pk')
        conversacion = ConversacionWhatsapp.objects.get(pk=pk)
        conversacion.contacto = contact_pk
        conversacion.save()
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS,),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["get"])
    def messages(self, request, pk):
        conversation = ConversacionWhatsapp.objects.get(pk=pk)
        if 'message_id' in self.request.GET:
            last_message = MensajeWhatsapp.objects.get(id=self.request.GET['message_id'])
            mensajes = MensajeWhatsapp.objects.filter(
                conversation=pk, timestamp__gte=last_message.timestamp).order_by('timestamp')
        else:
            mensajes = MensajeWhatsapp.objects.filter(conversation=pk).order_by('timestamp')
        serializer_mensajes = MensajeListSerializer(mensajes, many=True)
        data = {
            "messages": serializer_mensajes.data,
            "conversation_info": ConversacionSerializer(conversation).data
        }
        return response.Response(
            data=get_response_data(status=HttpResponseStatus.SUCCESS, data=data),
            status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_text(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            destination = conversation.destination
            sender = request.user.get_agente_profile()
            data = request.data.copy()
            line = ConfiguracionWhatsappCampana.objects.filter(
                campana=conversation.campana).last().linea
            message = {"text": data['message'], "type": "text"}
            orquestador_response = send_text_message(
                line, destination, message)  # orquestador
            if orquestador_response["status"] == "submitted":
                mensaje = MensajeWhatsapp.objects.create(
                    conversation=conversation,
                    origen=line.numero,
                    timestamp=timezone.now().astimezone(
                        timezone.get_current_timezone()),
                    sender={"name": sender.user.username, "agent_id": sender.user.id},
                    content=message,
                    type="text",
                )
                serializer = MensajeListSerializer(mensaje)
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data={}),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @decorators.action(detail=True, methods=["post"])
    # def send_message_attachment(self, request, pk):
    #     sender = request.user.get_agente_profile()
    #     data = request.data.copy()
    #     data.update({"conversation": pk, "sender": MESSAGE_SENDERS['AGENT']})
    #     serializer = MensajeAtachmentCreateSerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     # serializer.save()
    #     # orquestador_response = send_message_attachment(serializer.data) # orquestador
    #     orquestador_response = {
    #         "status": MESSAGE_STATUS['SENT'],
    #         "message_id": "1",
    #         "date": "01-01-2022 09:10"
    #     }
    #     return response.Response(
    #         data=get_response_data(status=HttpResponseStatus.SUCCESS, data=orquestador_response),
    #         status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"])
    def send_message_template(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            destination = conversation.destination
            sender = request.user.get_agente_profile()
            data = request.data.copy()  # template_id
            line = ConfiguracionWhatsappCampana.objects.filter(
                campana=conversation.campana).last().linea
            message = PlantillaMensaje.objects.get(pk=data['template_id']).configuracion
            orquestador_response = send_text_message(
                line, destination, message)  # orquestador
            if orquestador_response["status"] == "submitted":
                mensaje = MensajeWhatsapp.objects.create(
                    conversation=conversation,
                    origen=line.numero,
                    timestamp=timezone.now().astimezone(
                        timezone.get_current_timezone()),
                    sender={"name": sender.user.username, "agent_id": sender.user.id},
                    content=message,
                    type="template",
                )
                serializer = MensajeListSerializer(mensaje)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS, data=serializer.data,
                    message=_('Se envió el mensaje de forma exitosa')),
                status=status.HTTP_200_OK)
        except Exception as e:
            print("Error al enviar el mensaje")
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def send_message_whatsapp_template(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            destination = conversation.destination
            data = request.data.copy()  # Id Template
            template = TemplateWhatsapp.objects.get(id=data['template_id'])
            template_id = template.identificador
            sender = request.user.get_agente_profile()
            line = ConfiguracionWhatsappCampana.objects.filter(
                campana=conversation.campana).last().linea
            orquestador_response = send_template_message(
                line, destination, template_id, data['params'])  # orquestador
            if orquestador_response["status"] == "submitted":
                text = template.texto.replace('{{', '{').\
                    replace('}}', '}').format("", *data['params'])
                mensaje = MensajeWhatsapp.objects.create(
                    conversation=conversation,
                    origen=line.numero,
                    timestamp=timezone.now().astimezone(
                        timezone.get_current_timezone()),
                    sender={"name": sender.user.username, "agent_id": sender.user.id},
                    content={"text": text, "type": "template"},
                    type="template",
                )
                serializer = MensajeListSerializer(mensaje)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS, data=serializer.data,
                    message=_('Se envió el mensaje de forma exitosa')
                ),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["post"])
    def send_initing_conversation(self, request):
        try:
            data = request.data.copy()  # Id Template
            line = ConfiguracionWhatsappCampana.objects.filter(
                campana=data['campaing']).last().linea
            template = TemplateWhatsapp.objects.get(id=data['template_id'])
            template_id = template.identificador
            orquestador_response = send_template_message(
                line, data['destination'], template_id, data['params'])  # orquestador
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS, data=orquestador_response),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data={}),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
