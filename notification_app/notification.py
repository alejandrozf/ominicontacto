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
from notification_app.consumers import AgentConsole
from ominicontacto_app.services.redis.redis_streams import RedisStreams


class AgentNotifier:

    TYPE_UNPAUSE = 'unpause'
    TYPE_PAUSE = 'pause'
    TYPE_CONTACT_SAVED = 'contact_saved'

    def get_group_name(self, user_id=None):
        if user_id is not None:
            return AgentConsole.GROUP_USER_OBJ.format(user_id=user_id)
        else:
            return AgentConsole.GROUP_USER_CLS

    def notify_pause(self, user_id, pause_id, pause_name):
        message = {
            "id": pause_id,
            "name": pause_name
        }
        self.send_message(self.TYPE_PAUSE, message, user_id=user_id)

    def notify_unpause(self, user_id, pause_id):
        message = {
            "id": pause_id,
        }
        self.send_message(self.TYPE_UNPAUSE, message, user_id=user_id)

    def notify_dispositioned(self, user_id, call_id, dispositioned):
        message = {
            "id": call_id,
            "dispositioned": dispositioned
        }
        self.send_message(self.TYPE_UNPAUSE, message, user_id=user_id)

    def notify_contact_saved(self, user_id, call_id, contact_id):
        message = {
            "id": call_id,
            "contact_id": contact_id
        }
        self.send_message(self.TYPE_CONTACT_SAVED, message, user_id=user_id)

    def send_message(self, type, message, user_id=None):
        # si user_id=None se envia mensaje a todos los agentes conectados
        async_to_sync(get_channel_layer().group_send)(self.get_group_name(user_id), {
            "type": "broadcast",
            "payload": {
                "type": type,
                "args": message
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
