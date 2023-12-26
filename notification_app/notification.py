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
import datetime
import time
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification_app.consumers import AgentConsole, AgentConsoleWhatsapp
from ominicontacto_app.services.redis.redis_streams import RedisStreams
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


class AgentNotifier:

    TYPE_UNPAUSE = 'unpause'
    TYPE_PAUSE = 'pause'
    TYPE_CONTACT_SAVED = 'contact_saved'
    TYPE_WHATSAPP_NEW_CHAT = 'whatsapp_new_chat'
    TYPE_WHATSAPP_CHAT_ATTENDED = 'whatsapp_chat_attended'
    TYPE_WHATSAPP_CHAT_TRANSFERED = 'whatsapp_chat_transfered'
    TYPE_WHATSAPP_NEW_MESSAGE = 'whatsapp_new_message'
    TYPE_WHATSAPP_MESSAGE_STATUS = 'whatsapp_message_status'
    TYPE_WHATSAPP_CHAT_EXPIRED = 'whatsapp_chat_expired'

    def get_group_name(self, user_id=None, whatsapp_event=False):
        if user_id is not None:
            if whatsapp_event:
                return AgentConsoleWhatsapp.GROUP_USER_OBJ.format(user_id=user_id)
            return AgentConsole.GROUP_USER_OBJ.format(user_id=user_id)
        else:
            if whatsapp_event:
                return AgentConsoleWhatsapp.GROUP_USER_CLS
            return AgentConsole.GROUP_USER_CLS

    def notify_pause(self, user_id, pause_id, pause_name):
        message = {
            'id': pause_id,
            'name': pause_name
        }
        self.send_message(self.TYPE_PAUSE, message, user_id=user_id)

    def notify_unpause(self, user_id, pause_id):
        message = {
            'id': pause_id,
        }
        self.send_message(self.TYPE_UNPAUSE, message, user_id=user_id)

    def notify_dispositioned(self, user_id, call_id, dispositioned):
        message = {
            'id': call_id,
            'dispositioned': dispositioned
        }
        self.send_message(self.TYPE_UNPAUSE, message, user_id=user_id)

    def notify_contact_saved(self, user_id, call_id, contact_id):
        message = {
            "id": call_id,
            "contact_id": contact_id
        }
        self.send_message(self.TYPE_CONTACT_SAVED, message, user_id=user_id)

    async def notify_whatsapp_new_chat(self, user_id, **kwargs):
        conversation = kwargs.get('conversation', None)
        if conversation:
            message = {
                'chat_id': conversation.id,
                'campaing_id': conversation.campana.id if conversation.campana else "",
                'timestamp': conversation.timestamp.isoformat(),
            }
            await self.send_message_whatsapp(
                self.TYPE_WHATSAPP_NEW_CHAT, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_chat_attended(self, user_id, message):
        self.send_message(
            self.TYPE_WHATSAPP_CHAT_ATTENDED, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_chat_transfered(self, user_id, id_conversacion):
        message = {
            'chat_info': {
                'id': id_conversacion,
                'campaing_id': 'id_campana',
                'campaing_name': 'nombre_campana',
                'client_name': 'Cliente Transferido',
                "client_number": "7221313052",
                'photo': 'foto.jpg',
                'date': str(datetime.datetime.now()),
                'message_number': 2
            },
            'messages': [
                {
                    'chat_id': id_conversacion,
                    'message_id': 1,
                    'campaing_id': None,
                    'content': 'contenido1',
                    'message_id': 1,
                    'status': MESSAGE_STATUS['READ'],
                    'date': str(datetime.datetime.now()),
                    'sender': MESSAGE_SENDERS['CLIENT'],
                },
                {
                    'chat_id': id_conversacion,
                    'message_id': 2,
                    'campaing_id': None,
                    'content': 'contenido2',
                    'message_id': 2,
                    'status': MESSAGE_STATUS['READ'],
                    'date': str(datetime.datetime.now()),
                    'sender': MESSAGE_SENDERS['AGENT']
                },
            ]
        }
        self.send_message(
            self.TYPE_WHATSAPP_CHAT_TRANSFERED, message, user_id=user_id, whatsapp_event=True)

    async def notify_whatsapp_new_message(self, user_id, **kwargs):
        message = kwargs.get('message', None)
        line = kwargs.get('line', None)
        if message:
            message_json = {
                'chat_id': message.conversation.id,
                'campaing_id': message.conversation.campana.id
                if message.conversation.campana else "",
                'message_id': message.id,
                'content': message.content,
                'origen': message.origen,
                'timestamp': message.timestamp.isoformat(),
                'sender': message.sender,
                'type': message.type,
                'line_phone': line.numero if line else ''
            }
            print(self.TYPE_WHATSAPP_NEW_MESSAGE, message_json, user_id)
            await self.send_message_whatsapp(
                self.TYPE_WHATSAPP_NEW_MESSAGE, message_json, user_id=user_id, whatsapp_event=True)

    async def notify_whatsapp_message_status(self, user_id, **kwargs):
        message = kwargs.get('message', None)
        if message:
            message_json = {
                'chat_id': message.conversation.id,
                'message_id': message.id,
                'status': message.status,
                'date': message.timestamp.isoformat()
            }
            await self.send_message_whatsapp(
                self.TYPE_WHATSAPP_MESSAGE_STATUS,
                message_json,
                user_id=user_id,
                whatsapp_event=True)

    async def notify_whatsapp_chat_expired(self, user_id, **kwargs):
        conversation = kwargs.get('conversation', None)
        if conversation:
            message = {
                "conversation_id": conversation.id,
                "expire": conversation.expire.isoformat(),
                "is_active": conversation.is_active
            }
            await self.send_message_whatsapp(
                self.TYPE_WHATSAPP_CHAT_EXPIRED, message, user_id=user_id, whatsapp_event=True)

    def send_message(self, type, message, user_id=None, whatsapp_event=False):
        # si user_id=None se envia mensaje a todos los agentes conectados
        async_to_sync(
            get_channel_layer().group_send)(self.get_group_name(user_id, whatsapp_event), {
                'type': 'broadcast',
                'payload': {
                    'type': type,
                    'args': message
                }
            }
        )

    async def send_message_whatsapp(self, type, message, user_id=None, whatsapp_event=False):
        # si user_id=None se envia mensaje a todos los agentes conectados
        await get_channel_layer().group_send(
            self.get_group_name(user_id, whatsapp_event),
            {
                'type': 'broadcast',
                'payload': {
                    'type': type,
                    'args': message
                }
            })


class RedisStreamNotifier:

    def __init__(self):
        self.redis_stream = RedisStreams()

    def send(self, type_event, actives=None):
        if type_event == 'auth_event':
            stream_name = 'auth_event_{}'.format(str(datetime.date.today()))
        elif type_event == 'calification':
            stream_name = 'calification_event_{}'.format(str(datetime.date.today()))
        content = {
            'event': type_event,
            'timestamp': time.time(),
            'actives': actives
        }
        self.redis_stream.write_stream(stream_name, json.dumps(content), max_stream_length=100000)
