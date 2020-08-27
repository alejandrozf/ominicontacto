# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from __future__ import unicode_literals

import time
import redis
from django.conf import settings

from ominicontacto_app.models import QueueMember, Pausa
from ominicontacto_app.services.asterisk.redis_database import AgenteFamily
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector


class AgentActivityAmiManager(object):
    redis_connection = None

    def __init__(self, *args, **kwargs):
        self.manager = AMIManagerConnector()

    def connect_manager(self):
        self.manager.connect()

    def disconnect_manager(self):
        self.manager.disconnect()

    def login_agent(self, agente_profile, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        error = self._close_open_session(agente_profile)
        # Inicio nueva sesión
        if not error:
            error = self._queue_add_remove(agente_profile, 'QueueAdd')
        if not error:
            error = self._set_agent_redis_status(agente_profile, 'login')
        if manage_connection:
            self.disconnect_manager()
        return error

    def logout_agent(self, agente_profile, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        queue_remove_error = self._queue_add_remove(agente_profile, 'QueueRemove')
        if manage_connection:
            self.disconnect_manager()
        insert_redis_error = self._set_agent_redis_status(agente_profile, 'logout')
        return queue_remove_error, insert_redis_error

    def pause_agent(self, agente_profile, pause_id, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        pause_name = ''
        queue_pause_error = self._queue_pause_unpause(agente_profile, pause_id, 'pause')
        if manage_connection:
            self.disconnect_manager()

        if pause_id == '0':
            pause_name = 'ACW'
        elif pause_id == '00':
            pause_name = 'Supervision'
        else:
            pause_name = Pausa.objects.activa_by_pauseid(pause_id).nombre

        insert_redis_error = self._set_agent_pause_redis_status(
            agente_profile, pause_name, pause_id)

        return queue_pause_error, insert_redis_error

    def unpause_agent(self, agente_profile, pause_id, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        queue_unpause_error = self._queue_pause_unpause(agente_profile, pause_id, 'unpause')
        if manage_connection:
            self.disconnect_manager()
        insert_redis_error = self._set_agent_redis_status(agente_profile, 'unpause')
        return queue_unpause_error, insert_redis_error

    def set_agent_as_unavailable(self, agente_profile):
        self._set_agent_redis_status(agente_profile, 'UNAVAILABLE')

    def get_pause_id(self, pause_id):
        return pause_id

    def _get_family(self, agente_profile):
        agente_family = AgenteFamily()
        return agente_family._get_nombre_family(agente_profile)

    def _get_redis_status_data(self, action):
        if action == 'login' or action == 'unpause':
            status = 'READY'
        elif action == 'logout':
            status = 'OFFLINE'
        elif 'PAUSE' in action:
            status = action
        elif 'UNAVAILABLE' in action:
            status = action

        return {
            'STATUS': status,
            'TIMESTAMP': str(int(time.time()))
        }

    def _get_queue_data(self, agente_profile):
        agent_id = agente_profile.id
        member_name = agente_profile.get_asterisk_caller_id()
        queues = QueueMember.objects.obtener_queue_por_agent(agent_id)
        penalties = QueueMember.objects.obtener_penalty_por_agent(agent_id)
        sip_extension = agente_profile.sip_extension
        interface = "PJSIP/" + str(sip_extension).strip('[]')
        content = [agent_id, member_name, queues, penalties, interface]
        return content

    def _queue_add_remove(self, agente_profile, action):
        content = self._get_queue_data(agente_profile)
        data_returned, error = self.manager._ami_manager(action, content)
        return error

    def _queue_pause_unpause(self, agente_profile, pause_id, action):
        if action == 'unpause':
            pause_state = 'false'
        elif action == 'pause':
            pause_state = 'true'
        content = self._get_queue_data(agente_profile)
        content.append(pause_id)
        content.append(pause_state)
        data_returned, error = self.manager._ami_manager('QueuePause', content)

    def _close_open_session(self, agente_profile):
        status, error = self._get_redis_agent_status(agente_profile)
        if not error and not status == 'OFFLINE':
            # Finalizo posibles pausas en curso.
            error = self._queue_pause_unpause(agente_profile, '', 'unpause')
            # Finalizo posible sesión en curso.
            if not error:
                error = self._queue_add_remove(agente_profile, 'QueueRemove')
        return error

    def get_redis_connection(self):
        if self.redis_connection is None:
            self.redis_connection = redis.Redis(
                host=settings.REDIS_HOSTNAME,
                port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                decode_responses=True)
        return self.redis_connection

    def _save_agent_data(self, agente_profile, data):
        error = False
        family = self._get_family(agente_profile)
        redis_connection = self.get_redis_connection()
        try:
            redis_connection.hset(family, mapping=data)
        except redis.exceptions.RedisError:
            error = True
        return error

    def _set_agent_redis_status(self, agente_profile, action):
        data = self._get_redis_status_data(action)
        return self._save_agent_data(agente_profile, data)

    def _set_agent_pause_redis_status(self, agente_profile, pause_name, pause_id):
        action = 'PAUSE-' + pause_name
        data = self._get_redis_status_data(action)
        data['PAUSE_ID'] = pause_id
        return self._save_agent_data(agente_profile, data)

    def _get_redis_agent_status(self, agente_profile):
        family = self._get_family(agente_profile)
        redis_connection = self.get_redis_connection()
        status = None
        error = False
        try:
            status = redis_connection.hget(family, 'STATUS')
            if status is None:
                error = True
        except redis.exceptions.RedisError:
            error = True

        return status, error
