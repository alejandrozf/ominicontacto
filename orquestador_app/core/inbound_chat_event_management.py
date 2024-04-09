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
from django.contrib.contenttypes.models import ContentType
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp
from orquestador_app.core.gupshup_send_menssage import (
    autoresponse_welcome, autoresponse_out_of_time, autoreponse_destino_interactivo,
    send_text_message)
from orquestador_app.core.check_out_of_time import is_out_of_time
from orquestador_app.core.notify_agents import send_notify


async def inbound_chat_event(line, timestamp, message_id, origen, content, sender, type):
    try:
        print("mensaje entrante por la linea >>>", line.nombre, "content >>>>", content)
        is_out_of_time_chat = is_out_of_time(line, timestamp)
        message_inbound, created_message =\
            MensajeWhatsapp.objects.get_or_create(
                message_id=message_id, defaults={
                    'origen': origen,
                    'timestamp': timestamp,
                    'sender': sender,
                    'content': content,
                    'type': type
                }
            )
        if created_message or not message_inbound.conversation:
            created_conversation = False
            destination_entrante = line.destino
            conversations_from_origen = ConversacionWhatsapp.objects.filter(
                line=line, whatsapp_id=origen)
            conversation_with_identified_contact =\
                conversations_from_origen.filter(client__isnull=False).last()
            client = None
            if conversation_with_identified_contact:
                client = conversation_with_identified_contact.client
            conversation =\
                conversations_from_origen.filter(expire__gte=timestamp, is_disposition=False).last()
            if not conversation:
                client_alias = sender['name'] if 'name' in sender else ""
                campana = None
                if destination_entrante.content_type == ContentType.objects.get(model='campana'):
                    campana = destination_entrante.content_object
                conversation = ConversacionWhatsapp.objects.create(
                    line=line,
                    client=client,
                    campana=campana,
                    destination=origen,
                    whatsapp_id=origen,
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
                    autoresponse_welcome(line, conversation, timestamp)
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
            if is_out_of_time_chat:
                autoresponse_out_of_time(line, conversation, timestamp)
                conversation.is_disposition = True
                conversation.save()
                return
            #  ## notificar a agentes
            if created_conversation and conversation.campana:
                await send_notify('notify_whatsapp_new_chat', conversation=conversation)
            elif created_message and conversation.agent:
                await send_notify('notify_whatsapp_new_message', conversation=conversation,
                                  line=line,
                                  message=message_inbound)

            if not conversation.campana:
                if type == 'list_reply':
                    await asignar_campana(line, conversation, content)
                else:
                    autoreponse_destino_interactivo(line, conversation)

    except Exception as e:
        print("inbound_chat_event >>>>>>>> Error: ", e)


async def asignar_campana(line, conversation, content):
    try:
        destination_entrante = line.destino
        destino = destination_entrante.destinos_siguientes.filter(
            opcion_menu_whatsapp__opcion__valor=content['title']).last()
        auto_response = {}
        if destino:
            conversation.campana = destino.destino_siguiente.content_object
            conversation.save()
            await send_notify('notify_whatsapp_new_chat', conversation=conversation)
            if destination_entrante.content_object.texto_derivacion:
                auto_response = {"text": destination_entrante.content_object.texto_derivacion}
        else:
            if destination_entrante.content_object.texto_opcion_incorrecta:
                auto_response =\
                    {"text": destination_entrante.content_object.texto_opcion_incorrecta}
        if auto_response:
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            orquestador_response = send_text_message(line, conversation.destination, auto_response)
            if orquestador_response["status"] == "submitted":
                MensajeWhatsapp.objects.get_or_create(
                    message_id=orquestador_response['messageId'],
                    conversation=conversation,
                    defaults={
                        'origen': line.numero,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': auto_response,
                        'type': 'text'
                    }
                )
    except Exception as e:
        print("asignar_campana >>>>>>>", e)
