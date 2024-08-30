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
import operator
import mimetypes
from functools import reduce
from django.db.models import Q
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
from whatsapp_app.api.v1.mensaje import MensajeListSerializer, MensajeAtachmentCreateSerializer
from whatsapp_app.api.v1.contacto import ListSerializer as ContactoSerializer
from whatsapp_app.api.v1.calificacion import OpcionCalificacionSerializer
from whatsapp_app.models import (
    ConversacionWhatsapp, MensajeWhatsapp, PlantillaMensaje,
    TemplateWhatsapp)
from ominicontacto_app.models import Campana, AgenteProfile, Contacto
from notification_app.notification import AgentNotifier
from orquestador_app.core.gupshup_send_menssage import (
    send_template_message, send_text_message, send_multimedia_file)
from orquestador_app.core.media_management import get_media_url
from orquestador_app.core.gupshup_code_error import GUPSHUP_CODE_ERROR
from whatsapp_app.api.v1.linea import ListSerializer as LineSerializer


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

mimetypes.init()


def get_type(fileName):
    mimestart = mimetypes.guess_type(fileName)[0]
    if mimestart is not None:
        type_file = mimestart.split('/')[0]
        return type_file if type_file not in ['application', 'text'] else 'file'
    return 'file'


class ConversacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing_id = serializers.PrimaryKeyRelatedField(
        source='campana', queryset=Campana.objects.all())
    campaing_name = serializers.CharField(source='campana.nombre')
    destination = serializers.CharField()
    client = serializers.SerializerMethodField()
    agent = serializers.PrimaryKeyRelatedField(queryset=AgenteProfile.objects.all())
    is_active = serializers.BooleanField(default=True)
    is_disposition = serializers.BooleanField()
    expire = serializers.DateTimeField()
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField()
    message_number = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    line = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)
    error_ex = serializers.JSONField()
    client_alias = serializers.CharField(default="")

    def get_line(self, obj):
        serializer = LineSerializer(instance=obj.line)
        return {
            'id': serializer.data['id'],
            'name': serializer.data['name'],
            'number': serializer.data['number'],
        }

    def get_message_number(self, obj):
        return obj.mensajes.count()

    def get_messages(self, obj):
        return MensajeListSerializer(obj.mensajes.all().order_by('timestamp', 'id'), many=True).data

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            return serializer.data
        return None


class ConversacionFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaign = serializers.SerializerMethodField()
    destination = serializers.CharField()
    disposition = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    expire = serializers.DateTimeField()
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField()
    message_number = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    line = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)

    def get_line(self, obj):
        serializer = LineSerializer(instance=obj.line)
        return {
            'id': serializer.data['id'],
            'name': serializer.data['name'],
            'number': serializer.data['number'],
        }

    def get_campaign(self, obj):
        if obj.campana:
            campana = obj.campana
            return {
                'id': campana.id,
                'name': campana.nombre,
                'type': campana.type,
            }
        return {}

    def get_agent(self, obj):
        if obj.agent:
            return {
                'id': obj.agent.user.id,
                'name': obj.agent.user.get_full_name(),
            }
        return None

    def get_message_number(self, obj):
        return obj.mensajes.count()

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            return serializer.data
        return None

    def get_disposition(self, obj):
        try:
            if obj.is_disposition and obj.conversation_disposition:
                serializer = OpcionCalificacionSerializer(
                    obj.conversation_disposition.opcion_calificacion)
                return serializer.data
            return {}
        except Exception as e:
            print(e)


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
            agente = request.user.get_agente_profile()
            agente_campanas = agente.get_campanas_activas_miembro().values_list(
                'queue_name__campana_id', flat=True)
            conversacines = ConversacionWhatsapp.objects.filter(
                is_disposition=False)
            conversaciones_nuevas = conversacines.filter(
                agent=None, campana__id__in=agente_campanas).order_by('-date_last_interaction')
            conversaciones_en_curso = conversacines.filter(
                agent=agente).order_by('-date_last_interaction')
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
        except Exception as e:
            print(e)
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
            conversacion = ConversacionWhatsapp.objects.get(pk=pk)
            agente = request.user.get_agente_profile()
            if not conversacion.agent or conversacion.agent == agente:
                conversation_granted = conversacion.otorgar_conversacion(agente),
                mensajes = conversacion.mensajes.all()
                serializer_conversacion = ConversacionSerializer(conversacion)
                serializer_mensajes = MensajeListSerializer(mensajes, many=True)
                data = {
                    "conversation_granted": conversation_granted,
                    "conversation_data": serializer_conversacion.data,
                    "messages": serializer_mensajes.data
                }
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
                        status=HttpResponseStatus.SUCCESS, data=data,
                        message=_('Se asignó la conversación de forma exitosa')),
                    status=status.HTTP_200_OK
                )
            return response.Response(
                data=get_response_data(
                    message=_('Esta conversación ya está siendo atendida por otro agente')),
                status=status.HTTP_401_UNAUTHORIZED)
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
        try:
            contact_pk = request.data.get('contact_pk')
            conversacion = ConversacionWhatsapp.objects.get(pk=pk)
            contact = Contacto.objects.get(pk=contact_pk)
            if contact.bd_contacto != conversacion.campana.bd_contacto:
                return response.Response(
                    data=get_response_data(
                        message=_('El contacto no pertenece a la base de datos de la campaña')),
                    status=status.HTTP_400_BAD_REQUEST)
            if ConversacionWhatsapp.objects.conversaciones_en_curso()\
                    .filter(client_id=contact.pk, line_id=conversacion.line.pk).exists():
                return response.Response(
                    data=get_response_data(
                        message=_('El contacto ya tiene una conversación activa')),
                    status=status.HTTP_400_BAD_REQUEST)
            conversacion.client = contact
            conversacion.save()
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se asigno el contacto a la conversacion de forma satisfactoria')),
                status=status.HTTP_200_OK)
        except ConversacionWhatsapp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No se puede asignar una conversación que no existe')),
                status=status.HTTP_404_NOT_FOUND)
        except Contacto.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('No existe el contacto que se quiere asignar')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error al asignar el contacto a la conversación")
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al asignar el contacto a la conversación')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        destination = conversation.destination
                        sender = request.user.get_agente_profile()
                        if not conversation.agent or conversation.agent != sender:
                            raise Exception(
                                _('Esta conversación ya está siendo atendida por otro agente'))
                        data = request.data.copy()
                        line = conversation.line
                        message = {"text": data['message'], "type": "text"}
                        orquestador_response = send_text_message(
                            line, destination, message)  # orquestador
                        if orquestador_response["status"] == "submitted":
                            mensaje = MensajeWhatsapp.objects.create(
                                message_id=orquestador_response['messageId'],
                                conversation=conversation,
                                origen=line.numero,
                                timestamp=timestamp,
                                sender={"name": sender.user.username, "agent_id": sender.user.id},
                                content=message,
                                type="text",
                            )
                            serializer = MensajeListSerializer(mensaje)
                        else:
                            raise Exception(
                                _('Este mensaje no se pudo enviar'))
                        return response.Response(
                            data=get_response_data(
                                status=HttpResponseStatus.SUCCESS,
                                data=serializer.data),
                            status=status.HTTP_200_OK)
                    return response.Response(
                        data=get_response_data(
                            message=_(
                                'La conversacion esta inactiva hasta que el cliente responda')),
                        status=status.HTTP_401_UNAUTHORIZED)
                return response.Response(data=get_response_data(
                    message=_('La conversacion ha expirado. Inicie una nueva conversacion.')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion es erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={},
                    errors=str(e), message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def send_message_attachment(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        destination = conversation.destination
                        sender = request.user.get_agente_profile()
                        if not conversation.agent or conversation.agent != sender:
                            raise Exception(
                                _('Esta conversación ya está siendo atendida por otro agente'))
                        line = conversation.line
                        data = request.data.copy()
                        data.update({"conversation": pk,
                                     "sender": MESSAGE_SENDERS['AGENT']})
                        serializer = MensajeAtachmentCreateSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        mensaje = serializer.save()
                        filename = data['file'].name
                        file_type = get_type(filename)
                        domain = request.build_absolute_uri('/')[:-1]
                        # domain = "https://nominally-hopeful-condor.ngrok-free.app"
                        media_url = domain + mensaje.file.url
                        message_dict = {
                            "type": file_type,
                            "previewUrl": media_url,
                            "originalUrl": media_url,
                            "url": media_url,
                            "name": filename,
                            "filename": filename
                        }
                        orquestador_response = send_multimedia_file(
                            line, destination, message_dict)
                        if orquestador_response["status"] == "submitted":
                            mensaje.message_id = orquestador_response['messageId']
                            mensaje.origen = line.numero
                            mensaje.timestamp = timestamp
                            mensaje.sender = {
                                "name": sender.user.username,
                                "agent_id": sender.user.id
                            }
                            mensaje.content = message_dict
                            mensaje.type = file_type
                            mensaje.save()
                            serializer = MensajeListSerializer(mensaje)
                        else:
                            mensaje.delete()
                            raise Exception(
                                _('Este mensaje no se pudo enviar'))
                        return response.Response(
                            data=get_response_data(
                                status=HttpResponseStatus.SUCCESS,
                                data=serializer.data),
                            status=status.HTTP_200_OK)
                    return response.Response(
                        data=get_response_data(
                            message=_(
                                'La conversacion esta inactiva hasta que el cliente responda')),
                        status=status.HTTP_401_UNAUTHORIZED)
                return response.Response(data=get_response_data(
                    message=_('La conversacion ha expirado. Inicie una nueva conversacion.')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion es erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={},
                    errors=str(e), message=_('Error al enviar el mensaje')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def send_message_template(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        destination = conversation.destination
                        sender = request.user.get_agente_profile()
                        if not conversation.agent or conversation.agent != sender:
                            raise Exception(
                                _('Esta conversación ya está siendo atendida por otro agente'))
                        data = request.data.copy()  # template_id
                        line = conversation.line
                        message = PlantillaMensaje.objects.get(pk=data['template_id']).configuracion
                        orquestador_response = send_text_message(
                            line, destination, message)  # orquestador
                        if orquestador_response["status"] == "submitted":
                            mensaje = MensajeWhatsapp.objects.create(
                                message_id=orquestador_response['messageId'],
                                conversation=conversation,
                                origen=line.numero,
                                timestamp=timestamp,
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
                    return response.Response(
                        data=get_response_data(
                            message=_(
                                'La conversacion esta inactiva hasta que el cliente responda')),
                        status=status.HTTP_401_UNAUTHORIZED)
                return response.Response(
                    data=get_response_data(
                        message=_(
                            'La conversacion ha expirado. Inicie una nueva conversacion.')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("Error al enviar el mensaje")
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al enviar el mensaje'),
                                       status=HttpResponseStatus.ERROR, data={}, errors=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def send_message_whatsapp_template(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                destination = conversation.destination
                data = request.data.copy()  # Id Template
                template = TemplateWhatsapp.objects.get(id=data['template_id'])
                template_id = template.identificador
                template_tipo = template.tipo
                multimedia_id = template.identificador_media
                sender = request.user.get_agente_profile()
                if not conversation.agent or conversation.agent != sender:
                    raise Exception(_('Esta conversación ya está siendo atendida por otro agente'))
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        line = conversation.line
                        orquestador_response = send_template_message(
                            line, destination, template_id, template_tipo,
                            data['params'], multimedia_id)  # orquestador
                        if orquestador_response["status"] == "submitted":
                            text = template.texto.replace('{{', '{').\
                                replace('}}', '}').format("", *data['params'])
                            if template_tipo == 'TEXT':
                                message_dict = {"text": text, "type": template_tipo}
                            else:
                                app_id = template.linea.configuracion['app_id']
                                media_url = get_media_url(app_id, multimedia_id)
                                message_dict = {
                                    "type": template_tipo.lower(),
                                    "previewUrl": media_url,
                                    "originalUrl": media_url,
                                    "url": media_url,
                                    "name": text,
                                    "filename": "",
                                    "caption": text
                                }
                            mensaje = MensajeWhatsapp.objects.create(
                                message_id=orquestador_response['messageId'],
                                conversation=conversation,
                                origen=line.numero,
                                timestamp=timestamp,
                                sender={"name": sender.user.username, "agent_id": sender.user.id},
                                content=message_dict,
                                type=template_tipo.lower(),
                            )
                            serializer = MensajeListSerializer(mensaje)
                        return response.Response(
                            data=get_response_data(
                                status=HttpResponseStatus.SUCCESS, data=serializer.data,
                                message=_('Se envió el mensaje de forma exitosa')
                            ),
                            status=status.HTTP_200_OK)
                    return response.Response(
                        data=get_response_data(
                            message=_(
                                'La conversacion esta inactiva hasta que el cliente responda')),
                        status=status.HTTP_401_UNAUTHORIZED)
                return response.Response(data=get_response_data(
                    message=_('La conversacion ha expirado. Inicie una nueva conversacion.')),
                    status=status.HTTP_401_UNAUTHORIZED)
            return response.Response(
                data=get_response_data(
                    message=_('Conversacion erronea')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(">>>>>>>.", e)
            return response.Response(
                data=get_response_data(message=_('Error al enviar el mensaje'),
                                       status=HttpResponseStatus.ERROR, data={}, errors=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def reactive_expired_conversation(self, request, pk):
        try:
            data = request.data.copy()  # Id Template
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            or_filter = Q(destination=conversation.destination)
            if conversation.client:
                or_filter |= Q(client_id=conversation.client.pk)
            conversation_already_taken = ConversacionWhatsapp.objects\
                .conversaciones_en_curso().filter(line_id=conversation.line.pk)\
                .filter(or_filter).exists()
            if conversation.error:
                return response.Response(
                    data=get_response_data(
                        message=_('Conversacion erronea')),
                    status=status.HTTP_401_UNAUTHORIZED)
            if conversation_already_taken:
                return response.Response(
                    data=get_response_data(
                        message=_('Ya existe una conversacion iniciada con el cliente')),
                    status=status.HTTP_401_UNAUTHORIZED)
            destination = conversation.destination
            sender = request.user.get_agente_profile()
            line = conversation.line
            template = TemplateWhatsapp.objects.get(id=data['template_id'])
            template_id = template.identificador
            template_tipo = template.tipo
            multimedia_id = template.identificador_media
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            orquestador_response = send_template_message(
                line, destination, template_id, template_tipo, data['params'], multimedia_id)
            if orquestador_response["status"] == "submitted":
                text = template.texto.replace('{{', '{').\
                    replace('}}', '}').format("", *data['params'])
                if template_tipo == 'TEXT':
                    message_dict = {"text": text, "type": template_tipo}
                else:
                    app_id = template.linea.configuracion['app_id']
                    media_url = get_media_url(app_id, multimedia_id)
                    message_dict = {
                        "type": template_tipo.lower(),
                        "previewUrl": media_url,
                        "originalUrl": media_url,
                        "url": media_url,
                        "name": text,
                        "filename": "",
                        "caption": text
                    }
                mensaje = MensajeWhatsapp.objects.create(
                    conversation=conversation,
                    message_id=orquestador_response['messageId'],
                    origen=line.numero,
                    timestamp=timestamp,
                    sender={"name": sender.user.username, "agent_id": sender.user.id},
                    content=message_dict,
                    type=template_tipo.lower(),
                )
                serializer = MensajeListSerializer(mensaje)
            return response.Response(
                data=get_response_data(
                    message=_('Se envio el mensaje de forma exitosa'),
                    status=HttpResponseStatus.SUCCESS, data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print('\n\n===> Error al reactivar la conversacion')
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al enviar el mensaje'),
                    status=HttpResponseStatus.SUCCESS, data={}),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["post"])
    def send_initing_conversation(self, request):
        try:
            sender = request.user.get_agente_profile()
            data = request.data.copy()  # Id Template
            # Verifico parametros
            required_fields = {'campaign', 'template_id', 'destination', 'params', 'contact', }
            missing_fields = required_fields.difference(data.keys())
            if missing_fields:
                return response.Response(
                    data=get_response_data(
                        message=_('Campos esperados: {0}').format(', '.join(missing_fields))),
                    status=status.HTTP_400_BAD_REQUEST)
            # Verifico campaña
            try:
                campana = Campana.objects.get(id=data['campaign'])
            except Campana.DoesNotExist:
                return response.Response(
                    data=get_response_data(message=_('Campaña inválida')),
                    status=status.HTTP_400_BAD_REQUEST)
            configuracion = campana.configuracionwhatsapp.filter(is_active=True).last()
            if not configuracion:
                return response.Response(
                    data=get_response_data(message=_('Campaña inválida')),
                    status=status.HTTP_400_BAD_REQUEST)
            line = configuracion.linea
            if not line or not campana.whatsapp_habilitado:
                return response.Response(
                    data=get_response_data(message=_('Campaña inválida')),
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                template = TemplateWhatsapp.objects.get(id=data['template_id'])
            except TemplateWhatsapp.DoesNotExist:
                return response.Response(
                    data=get_response_data(message=_('Template inválido')),
                    status=status.HTTP_400_BAD_REQUEST)
            template_id = template.identificador
            template_tipo = template.tipo
            multimedia_id = template.identificador_media
            destination = data['destination']
            contact_id = data['contact']
            try:
                contact = campana.bd_contacto.contactos.get(id=contact_id)
            except Contacto.DoesNotExist:
                return response.Response(
                    data=get_response_data(message=_('Contacto inválido')),
                    status=status.HTTP_400_BAD_REQUEST)
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            or_filter = Q(destination=destination) | Q(client_id=contact.pk)
            conversation_started = ConversacionWhatsapp.objects\
                .conversaciones_en_curso().filter(line_id=line.pk).filter(or_filter)
            if not conversation_started:
                orquestador_response = send_template_message(
                    line, destination, template_id, template_tipo, data['params'], multimedia_id)
                if orquestador_response["status"] == "submitted":
                    conversation_started = ConversacionWhatsapp.objects.create(
                        line=line,
                        destination=destination,
                        date_last_interaction=timestamp,
                        campana=campana,
                        agent=sender,
                        saliente=True,
                        client=contact
                    )
                    text = template.texto.replace('{{', '{').\
                        replace('}}', '}').format("", *data['params'])
                    if template_tipo == 'TEXT':
                        message_dict = {"text": text, "type": template_tipo}
                    else:
                        app_id = template.linea.configuracion['app_id']
                        media_url = get_media_url(app_id, multimedia_id)
                        message_dict = {
                            "type": template_tipo.lower(),
                            "previewUrl": media_url,
                            "originalUrl": media_url,
                            "url": media_url,
                            "name": text,
                            "filename": "",
                            "caption": text
                        }
                    mensaje = MensajeWhatsapp.objects.create(
                        conversation=conversation_started,
                        message_id=orquestador_response['messageId'],
                        origen=line.numero,
                        timestamp=timestamp,
                        sender={"name": sender.user.username, "agent_id": sender.user.id},
                        content=message_dict,
                        type=template_tipo.lower(),
                    )
                    serializer = MensajeListSerializer(mensaje)
                return response.Response(
                    data=get_response_data(
                        message=_('Conversacion creada correctamente'),
                        status=HttpResponseStatus.SUCCESS, data=serializer.data),
                    status=status.HTTP_200_OK)
            return response.Response(
                data=get_response_data(message=_('Ya existe una conversacion iniciada')),
                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al enviar el mensaje'),
                    status=HttpResponseStatus.ERROR, data={}),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False,
                       methods=["POST"],
                       url_path='(?P<campaing_id>[^/.]+)/filter_chats')
    def filter_chats(self, request, campaing_id):
        try:
            campaing = Campana.objects.get(id=campaing_id)
            chats_of_campaing = campaing.conversaciones.all()
            start_date_str = request.data.get('start_date', None)
            end_date_str = request.data.get('end_date', None)
            phone = request.data.get('phone', None)
            agents = request.data.get('agents', None)
            list_of_Q = []
            if agents:
                if -1 in agents:
                    list_of_Q.append(Q(agent__isnull=True))
                    agents.remove(-1)
                if agents:
                    list_of_Q.append(Q(agent__in=agents))
            if list_of_Q:
                chats_of_campaing = chats_of_campaing.filter(reduce(operator.or_, list_of_Q))
            list_of_Q = []
            if start_date_str and end_date_str:
                list_of_Q.append(
                    Q(date_last_interaction__date__range=[start_date_str, end_date_str]))
            if phone:
                list_of_Q.append(Q(destination__contains=phone))
            if list_of_Q:
                chats_of_campaing = chats_of_campaing.filter(reduce(operator.and_, list_of_Q))
            serializer = ConversacionFilterSerializer(
                chats_of_campaing, many=True)
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={}, message=_(str(e))),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
