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
import json
from django.utils import timezone
import logging
from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from configuracion_telefonia_app.models import DestinoEntrante
from ominicontacto_app.models import Campana
from ominicontacto_app.services.redis.connection import create_redis_connection
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp, PlantillaMensaje

from .send_message import (
    autoresponse_welcome, autoresponse_out_of_time, autoreponse_destino_interactivo,
    send_text_message)
from orquestador_app.core.check_out_of_time import is_out_of_time
from orquestador_app.core.notify_agents import send_notify

redis_2 = create_redis_connection(db=2)

logger = logging.getLogger(__name__)


def _next_whatsapp_expire(timestamp):
    return (timestamp + timezone.timedelta(days=1)) - timezone.timedelta(
        seconds=timestamp.second,
        microseconds=timestamp.microsecond,
    )


def _get_origin_message_id(context):
    if not isinstance(context, dict):
        return None
    return context.get('gsId') or context.get('id')


def _add_origin_context(content, context):
    origin_message_id = _get_origin_message_id(context)
    if not origin_message_id:
        return
    try:
        mensaje_origen = MensajeWhatsapp.objects.get(message_id=origin_message_id)
    except MensajeWhatsapp.DoesNotExist:
        logger.debug("No se encontro mensaje origen para context=%r", context)
        return
    content.update({'context': mensaje_origen.content})


def _store_outbound_text_message(line, conversation, message):
    if not message:
        return
    timestamp = timezone.now().astimezone(timezone.get_current_timezone())
    message_id = send_text_message(line, conversation.destination, message)
    if message_id:
        MensajeWhatsapp.objects.get_or_create(
            message_id=message_id,
            conversation=conversation,
            defaults={
                'origen': line.numero,
                'timestamp': timestamp,
                'sender': {},
                'content': message,
                'type': 'text'
            }
        )


async def inbound_chat_event(line, timestamp, message_id, origen, content, sender, context, type):
    notifications = await s2a_inbound_chat_event(
        line,
        timestamp,
        message_id,
        origen,
        content,
        sender,
        context,
        type
    )
    for ntype, nargs in notifications:
        await send_notify(ntype, **nargs)


@sync_to_async
def s2a_inbound_chat_event(line, timestamp, message_id, origen, content, sender, context, type):
    notifications = []
    try:
        logger.debug("entrante por la linea=%r content=%r", line.nombre, content, context, type)
        is_out_of_time_chat = is_out_of_time(line, timestamp)
        if context and type in ['reply_text', 'reply_image', 'reply_video',
                                'reply_document', 'list_reply', 'button_reply', 'button']:
            _add_origin_context(content, context)
        message_inbound, created_message =\
            MensajeWhatsapp.objects.get_or_create(
                message_id=message_id, defaults={
                    'origen': origen,
                    'timestamp': timestamp,
                    'sender': sender,
                    'content': content,
                    'type': type,
                    'status': 'delivered'
                }
            )
        if created_message or not message_inbound.conversation:
            created_conversation = False
            reactivated_conversation = False
            destination_entrante = line.destino
            conversations_from_origen = ConversacionWhatsapp.objects.filter(
                line=line, whatsapp_id=origen)
            client = None
            conversation =\
                conversations_from_origen.filter(
                    expire__gte=timestamp, is_disposition=False).last()
            if not conversation:
                conversation = conversations_from_origen.filter(is_disposition=False).last()
                reactivated_conversation = conversation is not None
            if not conversation:
                client_alias = sender['name'] if 'name' in sender else ""
                campana = None
                if destination_entrante.content_type == ContentType.objects.get(model='campana'):
                    campana = destination_entrante.content_object
                if campana:
                    client = campana.bd_contacto.contactos.filter(
                        telefono=origen).last()
                conversation = ConversacionWhatsapp.objects.create(
                    line=line,
                    client=client,
                    campana=campana,
                    destination=origen,
                    whatsapp_id=origen,
                    is_active=True,
                    agent=None,
                    expire=_next_whatsapp_expire(timestamp),
                    timestamp=timestamp,
                    date_last_interaction=timestamp,
                    client_alias=client_alias
                )
                created_conversation = True
                if not is_out_of_time_chat:
                    autoresponse_welcome(line, conversation, timestamp)
                if client is None and not is_out_of_time_chat:
                    redis_2.sadd(
                        f'OML:WHATSAPP:CAMP:{conversation.campana_id}:NOT-IDENTIFIED-CONV',
                        conversation.destination
                    )
                    redis_2.publish('OML:CHANNEL:WHATSAPPEVENTS', json.dumps({
                        'type': 'WHATSAPP:NOT-IDENTIFIED-CONV',
                        'campaign_id': conversation.campana_id,
                    }))
            else:
                if not conversation.is_active:
                    conversation.is_active = True
                if conversation.saliente and not conversation.atendida:
                    conversation.atendida = True
                conversation.expire = _next_whatsapp_expire(timestamp)
                conversation.date_last_interaction = timestamp
                if not conversation.client_alias:
                    conversation.client_alias = sender['name'] if 'name' in sender else ""
                conversation.save()
            message_inbound.conversation = conversation
            message_inbound.save()
            if created_conversation and is_out_of_time_chat:
                autoresponse_out_of_time(line, conversation, timestamp)
                conversation.is_active = False
                conversation.is_disposition = True
                conversation.save(update_fields=['is_active', 'is_disposition'])
                if conversation.agent:
                    notifications.append(('notify_whatsapp_new_message', {
                        'conversation': conversation,
                        'line': line,
                        'message': message_inbound,
                    }))
                return notifications
            #  ## notificar a agentes
            if (created_conversation or reactivated_conversation) and conversation.campana \
                    and not conversation.agent:
                redis_2.sadd(
                    f'OML:WHATSAPP:CAMP:{conversation.campana_id}:NEW-INBOUND-CONV',
                    conversation.id
                )
                redis_2.publish('OML:CHANNEL:WHATSAPPEVENTS', json.dumps({
                    'type': 'WHATSAPP:NEW-INBOUND-CONV',
                    'campaign_id': conversation.campana_id,
                }))
                notifications.append(('notify_whatsapp_new_chat', {
                    'conversation': conversation,
                }))
            elif created_message and conversation.agent:
                notifications.append(('notify_whatsapp_new_message', {
                    'conversation': conversation,
                    'line': line,
                    'message': message_inbound,
                }))

            if not conversation.campana:
                if type == 'list_reply':
                    for notification in asignar_campana(line, conversation, content, context):
                        notifications.append(notification)
                else:

                    autoreponse_destino_interactivo(line, line.destino, conversation)

    except Exception as e:
        logger.exception("inbound_chat_event %r", e)
    return notifications


def asignar_campana(line, conversation, content, context):
    notifications = []
    try:
        origin_message_id = _get_origin_message_id(context)
        if not origin_message_id:
            return notifications
        mensaje_origen = MensajeWhatsapp.objects.get(message_id=origin_message_id)

        destino_entrante_id = mensaje_origen.sender['destino_entrante']
        destination_entrante = DestinoEntrante.objects.get(id=destino_entrante_id)
        destino = destination_entrante.destinos_siguientes.filter(
            opcion_menu_whatsapp__opcion__valor=content['title']).last()
        auto_response = {}
        if destino:
            if isinstance(destino.destino_siguiente.content_object, Campana):
                campana = destino.destino_siguiente.content_object
                client = campana.bd_contacto.contactos.filter(
                    telefono=conversation.destination).last()
                conversation.campana = campana
                conversation.client = client
                conversation.atendida = True
                conversation.save()
                notifications.append(('notify_whatsapp_new_chat', {
                    'conversation': conversation,
                }))
                opcion_whatsapp = getattr(destino, 'opcion_menu_whatsapp', None)
                if (
                    opcion_whatsapp and
                    opcion_whatsapp.send_message_before_campaign and
                    opcion_whatsapp.message_before_campaign
                ):
                    auto_response = opcion_whatsapp.message_before_campaign.configuracion
                elif destination_entrante.content_object.texto_derivacion:
                    auto_response = {"text": destination_entrante.content_object.texto_derivacion}
                _store_outbound_text_message(line, conversation, auto_response)
            elif isinstance(destino.destino_siguiente.content_object, PlantillaMensaje):
                plantilla = destino.destino_siguiente.content_object
                conversation.is_disposition = True
                conversation.save()
                auto_response = plantilla.configuracion
                _store_outbound_text_message(line, conversation, auto_response)
            else:
                autoreponse_destino_interactivo(line, destino.destino_siguiente, conversation)
        else:
            if destination_entrante.content_object.texto_opcion_incorrecta:
                auto_response =\
                    {"text": destination_entrante.content_object.texto_opcion_incorrecta}
    except Exception as e:
        logger.exception("asignar_campana %r", e)
    return notifications
