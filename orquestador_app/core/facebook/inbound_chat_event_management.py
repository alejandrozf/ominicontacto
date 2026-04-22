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

from django.utils import timezone
from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from ominicontacto_app.models import Campana
from ominicontacto_app.services.redis.connection import create_redis_connection
from facebook_meta_app.models import ConversationMessengerMetaApp, MessageMessengerMetaApp

from .send_message import (
    autoresponse_welcome, autoresponse_out_of_time, autoreponse_destino_interactivo,
    send_text_message)
from orquestador_app.core.check_out_of_time import is_out_of_time
from orquestador_app.core.notify_agents import send_notify

redis_2 = create_redis_connection(db=2)


async def inbound_chat_event(page, timestamp, message_id, origen, content,
                             sender, context, type, file=None):
    notifications = await s2a_inbound_chat_event(
        page,
        timestamp,
        message_id,
        origen,
        content,
        sender,
        context,
        type,
        file=file
    )
    for ntype, nargs in notifications:
        await send_notify(ntype, **nargs)


@sync_to_async
def s2a_inbound_chat_event(page, timestamp, message_id, origen, content,
                           sender, context, type, file=None):
    notifications = []
    try:
        is_out_of_time_chat = is_out_of_time(page, timestamp)
        print("is_out_of_time_chat >>>>", is_out_of_time_chat)
        message_inbound, created_message =\
            MessageMessengerMetaApp.objects.get_or_create(
                message_id=message_id, defaults={
                    'origen': origen,
                    'timestamp': timestamp,
                    'sender': sender,
                    'content': content,
                    'type': type,
                    'file': file,
                    'status': 'delivered'
                }
            )
        print("created_message >>>>", created_message, origen)
        if created_message or not message_inbound.conversation:
            created_conversation = False
            destination_entrante = page.destination
            conversations_from_origen = ConversationMessengerMetaApp.objects.filter(
                page=page, page_client_id=origen)
            print("conversations_from_origen >>>>", conversations_from_origen.count())
            conversation =\
                conversations_from_origen.filter(is_disposition=False).last()
            if not conversation:
                client_alias = sender['name'] if 'name' in sender else ""
                campana = None
                if destination_entrante.content_type == ContentType.objects.get(model='campana'):
                    campana = destination_entrante.content_object
                conversation = ConversationMessengerMetaApp.objects.create(
                    page=page,
                    client=None,
                    campana=campana,
                    page_client_id=origen,
                    is_active=True,
                    agent=None,
                    expire=(
                        timestamp + timezone.timedelta(days=1)) - timezone.timedelta(
                            seconds=timestamp.second, microseconds=timestamp.microsecond),
                    timestamp=timestamp,
                    date_last_interaction=timestamp,
                    client_alias=client_alias
                )
                created_conversation = True
                if not is_out_of_time_chat:
                    print("Nueva conversación creada >>>", conversation.id)
                    autoresponse_welcome(conversation, timestamp)
                # if client is None:
                #     redis_2.sadd(
                #         f'OML:WHATSAPP:CAMP:{conversation.campana_id}:NOT-IDENTIFIED-CONV',
                #         conversation.destination
                #     )
                #     redis_2.publish('OML:CHANNEL:WHATSAPPEVENTS', json.dumps({
                #         'type': 'WHATSAPP:NOT-IDENTIFIED-CONV',
                #         'campaign_id': conversation.campana_id,
                #     }))
            else:
                if not conversation.is_active:
                    conversation.is_active = True
                if conversation.saliente and not conversation.atendida:
                    conversation.atendida = True
                conversation.date_last_interaction = timestamp
                if not conversation.client_alias:
                    conversation.client_alias = sender['name'] if 'name' in sender else ""
                conversation.save()
            message_inbound.conversation = conversation
            message_inbound.save()
            if created_conversation and is_out_of_time_chat:
                autoresponse_out_of_time(conversation, timestamp)
                conversation.is_active = False
                conversation.is_disposition = True
                conversation.save(update_fields=['is_active', 'is_disposition'])
                if conversation.agent:
                    notifications.append(('notify_facebook_new_message', {
                        'conversation': conversation,
                        'page': page,
                        'message': message_inbound,
                    }))
                return notifications
            #  ## notificar a agentes
            if (created_conversation or created_message) and conversation.campana \
                    and not conversation.agent:
                # redis_2.sadd(
                #     f'OML:WHATSAPP:CAMP:{conversation.campana_id}:NEW-INBOUND-CONV',
                #     conversation.id
                # )
                # redis_2.publish('OML:CHANNEL:WHATSAPPEVENTS', json.dumps({
                #     'type': 'WHATSAPP:NEW-INBOUND-CONV',
                #     'campaign_id': conversation.campana_id,
                # }))
                notifications.append(('notify_facebook_new_chat', {
                    'conversation': conversation,
                }))
            elif created_message and conversation.agent:
                print("Notificando nuevo mensaje a agente asignado >>>>")
                notifications.append(('notify_facebook_new_message', {
                    'conversation': conversation,
                    'page': page,
                    'message': message_inbound,
                }))
            if not conversation.campana:
                if type == 'quick_reply':
                    for notification in asignar_campana(
                            page, timestamp, conversation, content, context):
                        notifications.append(notification)
                else:
                    print('primer menu >>>>>>>>>>>>>>>>>>>>>>')
                    autoreponse_destino_interactivo(page.destination, conversation, timestamp)

    except Exception as e:
        print("inbound_chat_event >>>>>>>> Error: ", e)
    return notifications


def asignar_campana(page, timestamp, conversation, content, context):
    notifications = []
    try:
        try:
            destino = conversation.page.destination.destinos_siguientes.filter(
                opcion_menu_messenger_meta_app__opcion__valor=context['text']).last()
        except Exception as e:
            print("Error al obtener destino >>>", e)
        auto_response = {}
        print("destino interactivo asignar_campana >>>>", destino)
        if destino:
            if isinstance(destino.destino_siguiente.content_object, Campana):
                campana = destino.destino_siguiente.content_object
                conversation.campana = campana
                conversation.save()
                notifications.append(('notify_facebook_new_chat', {
                    'conversation': conversation,
                }))
                if page.destination.content_object.texto_derivacion:
                    auto_response = {"text": page.destination.content_object.texto_derivacion}
                    if auto_response:
                        # timestamp = timezone.now().astimezone(timezone.get_current_timezone())
                        message_id = send_text_message(
                            page, conversation.page_client_id, auto_response)
                        if message_id:
                            MessageMessengerMetaApp.objects.get_or_create(
                                message_id=message_id,
                                conversation=conversation,
                                defaults={
                                    'origen': page.page_id,
                                    'timestamp': timestamp,
                                    'sender': {},
                                    'content': auto_response,
                                    'type': 'message'
                                }
                            )
            # elif isinstance(destino.destino_siguiente.content_object, PlantillaMensaje):
            #     plantilla = destino.destino_siguiente.content_object
            #     conversation.is_disposition = True
            #     conversation.save()
            #     auto_response = {"text": plantilla.configuracion['text']}
            #     if auto_response:
            #         timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            #         orquestador_response = send_text_message(
            #             page, conversation.destination, auto_response)
            #         if orquestador_response["status"] == "submitted":
            #             MessageMessengerMetaApp.objects.get_or_create(
            #                 message_id=orquestador_response['messageId'],
            #                 conversation=conversation,
            #                 defaults={
            #                     'origen': page.page_id,
            #                     'timestamp': timestamp,
            #                     'sender': {},
            #                     'content': auto_response,
            #                     'type': 'text'
            #                 }
            #             )
            else:
                print("destino interactivo siguiente >>>>", destino.destino_siguiente)
                autoreponse_destino_interactivo(page, destino.destino_siguiente, conversation)
        else:
            pass
    except Exception as e:
        print("asignar_campana >>>>>>>", e)
    return notifications
