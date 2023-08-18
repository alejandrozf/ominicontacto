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

    def notify_whatsapp_new_chat(self, user_id, id_conversacion):
        message = {
            'id': id_conversacion,
            'campaing_id': 'id_campana',
            'client_name': 'nombre_cliente',
            'photo': 'foto.jpg',
            'date': '20/04/2023',
            'campaing_name': 'nombre_campana',
            'message_number': '10'
        }
        self.send_message(
            self.TYPE_WHATSAPP_NEW_CHAT, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_chat_attended(self, user_id, id_conversacion):
        message = {
            'id': id_conversacion,
            'campaing_id': 'id_campana',
        }
        self.send_message(
            self.TYPE_WHATSAPP_CHAT_ATTENDED, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_chat_transfered(self, user_id, id_conversacion):
        message = {
            'chat_info': {
                'id': id_conversacion,
                'campaing_id': 'id_campana',
                'client_name': 'nombre_cliente',
                'photo': 'foto.jpg',
                'date': '20/04/2023',
                'campaing_name': 'nombre_campana',
                'message_number': '10'
            },
            'messages': [
                {
                    'id': '1',
                    'content': 'contenido',
                    'status': 'leido',
                    'date': '20/04/2023',
                    'sender': 'emisor'
                },
                {
                    'id': '2',
                    'content': 'contenido',
                    'status': 'leido',
                    'date': '20/04/2023',
                    'sender': 'emisor'
                },
            ]
        }
        self.send_message(
            self.TYPE_WHATSAPP_NEW_CHAT, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_new_message(self, user_id, message):
        message = {
            'chat_id': 1,
            'campaing_id': 1,
            'message_id': 1,
            'content': message,
            'user': 'Cliente EMI',
            'status': 1,
            'date': '2023-03-07 01:30',
            'sender': 1
        }
        self.send_message(
            self.TYPE_WHATSAPP_NEW_MESSAGE, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_message_status(self, user_id, id_message):
        message = {
            'chat_id': 'id_conversacion',
            'campaing_id': 'id_campana',
            'message_id': 'id_message',
            'status': '',
            'date': '20/04/2023',
        }
        self.send_message(
            self.TYPE_WHATSAPP_MESSAGE_STATUS, message, user_id=user_id, whatsapp_event=True)

    def notify_whatsapp_chat_expired(self, user_id, id_message):
        message = {
            'chat_id': 'id_conversacion',
            'campaing_id': 'campaing_id',
        }
        self.send_message(
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
