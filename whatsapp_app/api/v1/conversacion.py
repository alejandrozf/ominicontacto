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
from datetime import datetime
import json
import operator
import mimetypes
from functools import reduce
from django.db.models import F, Func, OuterRef, Prefetch, Q, Subquery
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
from api_app.services.media_url import build_public_media_url
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.api.v1.mensaje import MensajeListSerializer, MensajeAtachmentCreateSerializer
from whatsapp_app.api.v1.contacto import ListSerializer as ContactoSerializer
from whatsapp_app.api.v1.calificacion import OpcionCalificacionSerializer
from whatsapp_app.models import (
    ConversacionWhatsapp, Linea, MensajeWhatsapp, PlantillaMensaje,
    TemplateWhatsapp)
from ominicontacto_app.models import Campana, AgenteProfile, Contacto, CalificacionCliente
from ominicontacto_app.services.redis.connection import create_redis_connection
from notification_app.notification import AgentNotifier
from orquestador_app.core.whatsapp.send_message import (
    send_template_message, send_text_message, send_multimedia_file)
from orquestador_app.core.whatsapp.gupshup_code_error import GUPSHUP_CODE_ERROR
from whatsapp_app.api.v1.linea import ListSerializer as LineSerializer

redis_2 = create_redis_connection(db=2)


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


def _merge_forward_flags(original_content, content):
    if not isinstance(original_content, dict) or not isinstance(content, dict):
        return content
    if original_content.get('forwarded') is True:
        content['forwarded'] = True
    if original_content.get('frequently_forwarded') is True:
        content['frequently_forwarded'] = True
    return content


def _normalize_agent_snapshot(agent):
    if not isinstance(agent, dict):
        return None
    username = agent.get('username') or agent.get('name')
    if not username:
        return None
    return {
        'id': agent.get('id') or agent.get('agent_id'),
        'username': username,
        'name': agent.get('name') or username,
    }


def _normalize_campaign_snapshot(campaign):
    if not isinstance(campaign, dict):
        return None
    name = campaign.get('name')
    if not name:
        return None
    return {
        'id': campaign.get('id'),
        'name': name,
    }


def _build_conversation_agent_snapshot(conversation):
    if not conversation.agent:
        return None
    username = conversation.agent.user.username
    full_name = conversation.agent.user.get_full_name()
    return {
        'id': conversation.agent.user_id,
        'username': username,
        'name': full_name or username,
    }


def _build_message_agent_snapshot(message):
    sender = message.sender if isinstance(message.sender, dict) else {}
    if not sender.get('agent_id'):
        return None
    username = sender.get('name')
    if not username:
        return None
    return {
        'id': sender.get('agent_id'),
        'username': username,
        'name': username,
    }


def _extract_transfer_summary(conversation):
    cached_summary = getattr(conversation, '_transfer_summary_cache', None)
    if cached_summary is not None:
        return cached_summary
    initial_agent = None
    transferred_agent = None
    transferred_campaign = None
    for message in conversation.mensajes.all().order_by('timestamp', 'id'):
        if message.type == 'transfer_event':
            content = message.content if isinstance(message.content, dict) else {}
            if not initial_agent:
                initial_agent = _normalize_agent_snapshot(content.get('from_agent'))
            if content.get('event_type') == 'agent_transfer':
                transferred_agent = _normalize_agent_snapshot(content.get('to_agent'))
            if content.get('event_type') == 'campaign_transfer':
                transferred_campaign = _normalize_campaign_snapshot(content.get('to_campaign'))
        elif not initial_agent:
            initial_agent = _build_message_agent_snapshot(message)
    if not initial_agent:
        initial_agent = _build_conversation_agent_snapshot(conversation)
    summary = {
        'initial_agent': initial_agent,
        'transferred_agent': transferred_agent,
        'transferred_campaign': transferred_campaign,
    }
    conversation._transfer_summary_cache = summary
    return summary


def _parse_serialized_timestamp(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    if isinstance(timestamp, str):
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return timezone.now()


def _serialize_transfer_event_messages(conversation, messages=None):
    transfer_messages = []
    message_collection = messages if messages is not None else (
        conversation.mensajes.all().order_by('timestamp', 'id')
    )
    for message in message_collection:
        if message.type != 'transfer_event':
            continue
        transfer_messages.append({
            'id': message.id,
            'message_id': message.message_id,
            'conversation': conversation.id,
            'contact_data': {},
            'timestamp': message.timestamp.isoformat(),
            'content': message.content if isinstance(message.content, dict) else {},
            'origin': message.origen,
            'sender': message.sender,
            'type': message.type,
            'status': message.status,
            'fail_reason': message.fail_reason,
            'file': message.file.url if message.file else None,
        })
    return transfer_messages


def _serialize_messages_with_transfer_events(conversation, messages=None):
    message_collection = messages if messages is not None else (
        conversation.mensajes.all().order_by('timestamp', 'id')
    )
    real_messages = [
        message for message in message_collection
        if message.type != 'transfer_event'
    ]
    serialized_messages = list(MensajeListSerializer(real_messages, many=True).data)
    serialized_messages.extend(
        _serialize_transfer_event_messages(
            conversation,
            messages=message_collection,
        )
    )
    serialized_messages.sort(
        key=lambda message: (
            _parse_serialized_timestamp(message.get('timestamp')),
            message.get('id'),
        )
    )
    return serialized_messages


class ContactoSerializerEx(serializers.Serializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(source='telefono')
    disposition = serializers.IntegerField(source="last_disposition_id")

    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        return obj.obtener_datos()


class MensajesSerializerEx(serializers.Serializer):
    id = serializers.IntegerField()
    conversation = serializers.IntegerField(source="conversation_id")
    fail_reason = serializers.CharField()
    file = serializers.FileField()
    message_id = serializers.CharField()
    origin = serializers.CharField(source="origen")
    sender = serializers.JSONField()
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    type = serializers.CharField()

    contact_data = serializers.SerializerMethodField()

    def get_contact_data(self, obj):
        # is redundant since the same information can be optained from the conversation
        if obj.conversation.client:
            serializer = ContactoSerializerEx(obj.conversation.client)
            return serializer.data
        return {}

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        if obj.content:
            if obj.type == 'list-gupshup':
                content = json.loads(obj.content[0]['text'])
                text = content['title'] + '\n'
                options = content['items'][0]['options']
                for option in options:
                    text += "{}-{} \n"\
                            .format(option['title'],
                                    option['description'] if 'description' in option else '')
                return _merge_forward_flags(obj.content, {'text': text})
            elif obj.type == 'list-meta':
                content = json.loads(obj.content[0]['text'])
                text = content['header']['text'] + '\n'
                text += content['body']['text'] + '\n'
                options = content['action']['sections'][0]['rows']
                for option in options:
                    text += "{}-{} \n"\
                            .format(option['title'],
                                    option['description'] if 'description' in option else '')
                return _merge_forward_flags(obj.content, {'text': text})
            elif obj.type == 'list_reply':
                text = "Reply-option:\n {}-{}"\
                    .format(obj.content['title'],
                            obj.content['description'] if 'description' in obj.content else '')
                return _merge_forward_flags(obj.content, {'text': text})
            return _merge_forward_flags(obj.content, obj.content)
        return {}


class ConversacionSerializerEx(serializers.Serializer):
    id = serializers.IntegerField()
    agent = serializers.IntegerField(source="agent_id")
    campaing_id = serializers.IntegerField(source="campana_id")
    saliente = serializers.BooleanField(default=False)
    client_alias = serializers.CharField(default="")
    date_last_interaction = serializers.DateTimeField()
    destination = serializers.CharField()
    error = serializers.BooleanField(default=False)
    error_ex = serializers.JSONField()
    expire = serializers.DateTimeField()
    is_active = serializers.BooleanField(default=True)
    is_disposition = serializers.BooleanField()
    photo = serializers.CharField(default="")
    timestamp = serializers.DateTimeField()

    campaing_name = serializers.CharField(source='campana.nombre')

    client = serializers.SerializerMethodField()

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializerEx(obj.client)
            return serializer.data
        return None

    line = serializers.SerializerMethodField()
    initial_agent = serializers.SerializerMethodField()
    transferred_agent = serializers.SerializerMethodField()
    transferred_campaign = serializers.SerializerMethodField()

    def get_line(self, obj):
        return {
            "id": obj.line.id,
            "name": obj.line.nombre,
            "number": obj.line.numero,
        }

    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        return _serialize_messages_with_transfer_events(obj)

    def get_initial_agent(self, obj):
        return _extract_transfer_summary(obj)['initial_agent']

    def get_transferred_agent(self, obj):
        return _extract_transfer_summary(obj)['transferred_agent']

    def get_transferred_campaign(self, obj):
        return _extract_transfer_summary(obj)['transferred_campaign']

    message_number = serializers.IntegerField()
    message_unread = serializers.IntegerField()


class ConversacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaing_id = serializers.PrimaryKeyRelatedField(
        source='campana', queryset=Campana.objects.all())
    campaing_name = serializers.CharField(source='campana.nombre')
    saliente = serializers.BooleanField(default=False)
    destination = serializers.CharField()
    client = serializers.SerializerMethodField()
    agent = serializers.PrimaryKeyRelatedField(queryset=AgenteProfile.objects.all())
    is_active = serializers.BooleanField(default=True)
    is_disposition = serializers.BooleanField()
    expire = serializers.DateTimeField()
    timestamp = serializers.DateTimeField()
    date_last_interaction = serializers.DateTimeField()
    message_number = serializers.SerializerMethodField()
    message_unread = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    photo = serializers.CharField(default="")
    line = serializers.SerializerMethodField()
    initial_agent = serializers.SerializerMethodField()
    transferred_agent = serializers.SerializerMethodField()
    transferred_campaign = serializers.SerializerMethodField()
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

    def get_message_unread(self, obj):
        return obj.mensajes.mensajes_recibidos().filter(status='delivered').count()

    def get_messages(self, obj):
        return _serialize_messages_with_transfer_events(obj)

    def get_client(self, obj):
        if obj.client:
            serializer = ContactoSerializer(obj.client)
            return serializer.data
        return None

    def get_initial_agent(self, obj):
        return _extract_transfer_summary(obj)['initial_agent']

    def get_transferred_agent(self, obj):
        return _extract_transfer_summary(obj)['transferred_agent']

    def get_transferred_campaign(self, obj):
        return _extract_transfer_summary(obj)['transferred_campaign']


class ConversacionFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    campaign = serializers.SerializerMethodField()
    destination = serializers.CharField()
    was_closed_by_system = serializers.SerializerMethodField()
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
    initial_agent = serializers.SerializerMethodField()
    transferred_agent = serializers.SerializerMethodField()
    transferred_campaign = serializers.SerializerMethodField()
    error = serializers.BooleanField(default=False)

    def get_line(self, obj):
        return {
            'id': obj.line.id,
            'name': obj.line.nombre,
            'number': obj.line.numero,
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
            del serializer.fields['disposition']
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

    def get_was_closed_by_system(self, obj):
        return obj.is_disposition and not obj.conversation_disposition

    def get_initial_agent(self, obj):
        return _extract_transfer_summary(obj)['initial_agent']

    def get_transferred_agent(self, obj):
        return _extract_transfer_summary(obj)['transferred_agent']

    def get_transferred_campaign(self, obj):
        return _extract_transfer_summary(obj)['transferred_campaign']


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
            conversaciones = ConversacionWhatsapp.objects.filter(is_disposition=False).only(
                "id",
                "agent_id",
                "client_alias",
                "date_last_interaction",
                "destination",
                "error",
                "error_ex",
                "expire",
                "is_active",
                "is_disposition",
                "saliente",
                "timestamp",

                "campana_id",
                "client_id",
                "line_id",
            ).prefetch_related(
                Prefetch(lookup="campana", queryset=Campana.objects.only("id", "nombre")),
                Prefetch(
                    lookup="client",
                    queryset=Contacto.objects.only(
                        "id",
                        "telefono",
                        "datos",
                        "id_externo",
                        "bd_contacto",
                    ).annotate(
                        last_disposition_id=Subquery(
                            CalificacionCliente.objects.filter(
                                contacto=OuterRef("id"),
                            ).values("id")[:1]
                        ),
                    ).select_related("bd_contacto"),
                ),
                Prefetch(lookup="line", queryset=Linea.objects.only("id", "nombre", "numero")),
                Prefetch(
                    lookup="mensajes",
                    queryset=MensajeWhatsapp.objects.only(
                        "id",
                        "conversation_id",
                        "fail_reason",
                        "file",
                        "message_id",
                        "origen",
                        "sender",
                        "status",
                        "timestamp",
                        "type",

                        "content",
                    ).order_by("timestamp", "id")
                ),
            ).annotate(
                message_number=(
                    MensajeWhatsapp.objects.filter(
                        conversation_id=OuterRef("id"),
                    ).annotate(
                        count=Func(F("id"), function="Count"),
                    ).values("count")
                ),
                message_unread=(
                    MensajeWhatsapp.objects.filter(
                        conversation_id=OuterRef("id"),
                        origen=OuterRef("destination"),
                        status="delivered",
                    ).annotate(
                        count=Func(F("id"), function="Count"),
                    ).values("count")
                ),
                # performs worse than the previous ones
                # message_number=Count("mensajes"),
                # message_unread=Count("mensajes", filter=Q(
                #     mensajes__origen=F("destination"), mensajes__status="delivered"
                # )),
            ).order_by("-date_last_interaction")

            agente = AgenteProfile.objects.only("id").get(user_id=request.user.id)
            agente_campanas = agente.get_campanas_activas_miembro().values_list(
                "queue_name__campana_id", flat=True
            )
            conversaciones_nuevas = conversaciones.filter(
                Q(agent=None, campana__id__in=agente_campanas) |
                Q(agent=agente, atendida=False, saliente=False)
            )
            conversaciones_en_curso = conversaciones.filter(
                agent=agente,
            ).filter(
                Q(atendida=True) | Q(saliente=True)
            )

            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las conversaciones de forma exitosa'),
                    data={
                        "new_conversations": ConversacionSerializerEx(
                            instance=conversaciones_nuevas,
                            many=True,
                        ).data,
                        "inprogress_conversations": ConversacionSerializerEx(
                            instance=conversaciones_en_curso,
                            many=True,
                        ).data
                    }
                ),
                status=status.HTTP_200_OK,
            )
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
            instance.mensajes.mensajes_recibidos().update(status='read')
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
            print("Error al asignar la conversación >>>", e)
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
        mensajes = list(mensajes)
        data = {
            "messages": _serialize_messages_with_transfer_events(conversation, messages=mensajes),
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
                        print('>>> send_message_text')
                        message_id = send_text_message(
                            line, destination, message)  # orquestador
                        if message_id:
                            mensaje = MensajeWhatsapp.objects.create(
                                message_id=message_id,
                                conversation=conversation,
                                origen=line.numero,
                                timestamp=timestamp,
                                sender={"name": sender.user.username, "agent_id": sender.user.id},
                                content=message,
                                type="text",
                            )
                            serializer = MensajeListSerializer(mensaje)
                            return response.Response(
                                data=get_response_data(
                                    status=HttpResponseStatus.SUCCESS,
                                    data=serializer.data),
                                status=status.HTTP_200_OK)
                        else:
                            raise Exception(
                                _('Este mensaje no se pudo enviar'))
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
                        filename = data['file'].name[:100]
                        file_type = get_type(filename)
                        media_url = build_public_media_url(request, mensaje.file.url)
                        message_dict = {
                            "type": file_type,
                            "previewUrl": media_url,
                            "originalUrl": media_url,
                            "url": media_url,
                            "name": filename,
                            "filename": filename
                        }
                        message_id = send_multimedia_file(
                            line, destination, message_dict)
                        if message_id:
                            mensaje.message_id = message_id
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
            print(">>>>>>>>", e)
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
                        message_id = send_text_message(
                            line, destination, message)  # orquestador
                        if message_id:
                            mensaje = MensajeWhatsapp.objects.create(
                                message_id=message_id,
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
            print("Error al enviar el mensaje>>>", e)
            return response.Response(
                data=get_response_data(message=_('Error al enviar el mensaje'),
                                       status=HttpResponseStatus.ERROR, data={}, errors=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=["post"])
    def send_message_whatsapp_template(self, request, pk):
        try:
            conversation = ConversacionWhatsapp.objects.get(pk=pk)
            print("conversation>>>>", conversation)
            if not conversation.error or conversation.error_ex['code'] not in GUPSHUP_CODE_ERROR:
                destination = conversation.destination
                data = request.data.copy()  # Id Template
                template = TemplateWhatsapp.objects.get(id=data['template_id'])
                template_tipo = template.tipo
                sender = request.user.get_agente_profile()
                if not conversation.agent or conversation.agent != sender:
                    raise Exception(_('Esta conversación ya está siendo atendida por otro agente'))
                timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                if conversation.expire and conversation.expire >= timestamp:
                    if conversation.is_active:
                        line = conversation.line
                        message_id = send_template_message(
                            line, destination, template, data)
                        if message_id:
                            text = template.texto.replace('{{', '{').\
                                replace('}}', '}').format("", *data['params'])
                            header = template.texto_header.replace('{{', '{').\
                                replace('}}', '}').format("", *data['params_header'])
                            if template_tipo in ['TEXT', 'BUTTONS']:
                                message_dict = {
                                    "text": text,
                                    "header": header,
                                    "type": template_tipo,
                                    "buttons": template.botones
                                }
                            else:
                                media_url = template.link_media
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
                                message_id=message_id,
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
            print('reactive_expired_conversation >>>>', request.data)
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
            template_tipo = template.tipo
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            message_id = send_template_message(
                line, destination, template, data)
            if message_id:
                text = template.texto.replace('{{', '{').\
                    replace('}}', '}').format("", *data['params'])
                header = template.texto_header.replace('{{', '{').\
                    replace('}}', '}').format("", *data['params_header'])
                if template_tipo in ['TEXT', 'BUTTONS']:
                    message_dict = {
                        "text": text,
                        "header": header,
                        "type": template_tipo,
                        "buttons": template.botones
                    }
                else:
                    media_url = template.link_media
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
                    message_id=message_id,
                    origen=line.numero,
                    timestamp=timestamp,
                    sender={"name": sender.user.username, "agent_id": sender.user.id},
                    content=message_dict,
                    type=template_tipo.lower(),
                )
                conversation.expire = (
                    timestamp + timezone.timedelta(days=1)) - timezone.timedelta(
                        seconds=timestamp.second, microseconds=timestamp.microsecond)
                conversation.is_active = False
                conversation.save()
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
            required_fields = {
                'campaign', 'template_id', 'destination', 'params', 'params_header', 'contact', }
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
            template_tipo = template.tipo
            destination = data['destination']
            print("destination >>>", destination)
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
                message_id = send_template_message(
                    line, destination, template, data)
                if message_id:
                    conversation_started = ConversacionWhatsapp.objects.create(
                        line=line,
                        destination=destination,
                        whatsapp_id=destination,
                        date_last_interaction=timestamp,
                        campana=campana,
                        agent=sender,
                        saliente=True,
                        client=contact,
                        expire=(timestamp + timezone.timedelta(days=1)) - timezone.timedelta(
                            seconds=timestamp.second, microseconds=timestamp.microsecond))
                    text = template.texto.replace('{{', '{').\
                        replace('}}', '}').format("", *data['params'])
                    header = template.texto_header.replace('{{', '{').\
                        replace('}}', '}').format("", *data['params_header'])
                    if template_tipo in ['TEXT', 'BUTTONS']:
                        message_dict = {
                            "header": header,
                            "text": text,
                            "type": template_tipo,
                            "buttons": template.botones
                        }
                    else:
                        media_url = template.link_media
                        message_dict = {
                            "type": template.tipo.lower(),
                            "previewUrl": media_url,
                            "originalUrl": media_url,
                            "url": media_url,
                            "name": text,
                            "filename": "",
                            "caption": text
                        }
                    mensaje = MensajeWhatsapp.objects.create(
                        conversation=conversation_started,
                        message_id=message_id,
                        origen=line.numero,
                        timestamp=timestamp,
                        sender={"name": sender.user.username, "agent_id": sender.user.id},
                        content=message_dict,
                        type=template.tipo.lower(),
                    )
                    serializer = MensajeListSerializer(mensaje)
                    redis_2.sadd(
                        f"OML:WHATSAPP:CAMP:{conversation_started.campana_id}:NEW-OUTBOUND-CONV",
                        conversation_started.id
                    )
                    redis_2.publish('OML:CHANNEL:WHATSAPPEVENTS', json.dumps({
                        'type': 'WHATSAPP:NEW-OUTBOUND-CONV',
                        'campana_id': conversation_started.campana_id,
                    }))
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
            chats_of_campaing = campaing.conversaciones.select_related(
                "conversation_disposition__opcion_calificacion",
                "client__bd_contacto",
                "agent__user",
                "line",
            ).prefetch_related(
                "mensajes",
            )
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

    @decorators.action(detail=False,
                       methods=["POST"])
    def mark_as_read(self, request):
        try:
            MensajeWhatsapp.objects.filter(id__in=request.data).update(status='read')
            return response.Response(
                data=get_response_data(status=HttpResponseStatus.SUCCESS, data=[]),
                status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.ERROR, data={}, message=_(str(e))),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
