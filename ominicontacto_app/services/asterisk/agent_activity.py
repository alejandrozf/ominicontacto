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

from ominicontacto_app.models import QueueMember, Pausa
from ominicontacto_app.services.asterisk_database import AgenteFamily
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from api_app.utiles import AgentesParsing


class AgentActivityAmiManager(object):

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
            error = self._insert_astb_status(agente_profile, 'login')
        if manage_connection:
            self.disconnect_manager()
        return error

    def logout_agent(self, agente_profile, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        queue_remove_error = self._queue_add_remove(agente_profile, 'QueueRemove')
        insert_astdb_error = self._insert_astb_status(agente_profile, 'logout')
        if manage_connection:
            self.disconnect_manager()
        return queue_remove_error, insert_astdb_error

    def pause_agent(self, agente_profile, pause_id, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        pause_name = ''
        queue_pause_error = self._queue_pause_unpause(agente_profile, pause_id, 'pause')
        if pause_id == '0':
            pause_name = 'ACW'
        elif pause_id == '00':
            pause_name = 'Supervision'
        else:
            pause_name = Pausa.objects.activa_by_pauseid(pause_id).nombre
        insert_astdb_error = self._insert_astb_status(agente_profile, 'PAUSE-' + str(pause_name))
        if not insert_astdb_error:
            insert_astdb_error = self._insert_astdb_pause_id(agente_profile, pause_id)
        if manage_connection:
            self.disconnect_manager()
        return queue_pause_error, insert_astdb_error

    def unpause_agent(self, agente_profile, pause_id, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        queue_unpause_error = self._queue_pause_unpause(agente_profile, pause_id, 'unpause')
        insert_astdb_error = self._insert_astb_status(agente_profile, 'unpause')
        if manage_connection:
            self.disconnect_manager()
        return queue_unpause_error, insert_astdb_error

    def set_agent_as_unavailable(self, agente_profile, manage_connection=False):
        if manage_connection:
            self.connect_manager()
        self._insert_astb_status(agente_profile, 'UNAVAILABLE')
        if manage_connection:
            self.manager_disconnect()

    def get_pause_id(self, pause_id):
        return pause_id

    def _get_family(self, agente_profile):
        agente_family = AgenteFamily()
        return agente_family._get_nombre_family(agente_profile)

    def _get_astdb_status_data(self, agente_profile, action):
        family = self._get_family(agente_profile)
        tiempo_actual = int(time.time())
        key = 'STATUS'
        if action == 'login' or action == 'unpause':
            value = 'READY:' + str(tiempo_actual)
        elif action == 'logout':
            value = 'OFFLINE:' + str(tiempo_actual)
        elif 'PAUSE' in action:
            value = action + ':' + str(tiempo_actual)
        elif 'UNAVAILABLE' in action:
            value = action + ':' + str(tiempo_actual)
        content = [family, key, value]
        return content

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

    def _insert_astb_status(self, agente_profile, action):
        content = self._get_astdb_status_data(agente_profile, action)
        data_returned, error = self.manager._ami_manager('dbput', content)
        return error

    def _insert_astdb_pause_id(self, agente_profile, pause_id):
        family = self._get_family(agente_profile)
        key = 'PAUSE_ID'
        value = pause_id
        content = [family, key, value]
        data_returned, error = self.manager._ami_manager('dbput', content)
        return error

    def _close_open_session(self, agente_profile):
        status, error = self._get_astdb_agent_status(agente_profile)
        if not error and not status == 'OFFLINE':
            # Finalizo posibles pausas en curso.
            error = self._queue_pause_unpause(agente_profile, '', 'unpause')
            # Finalizo posible sesión en curso.
            if not error:
                error = self._queue_add_remove(agente_profile, 'QueueRemove')
        return error

    def _get_astdb_agent_status(self, agente_profile):
        family = self._get_family(agente_profile)
        data_returned, error = self.manager._ami_manager("command", "database show {0}".format(
            family))
        if not error:
            parser = AgentesParsing()
            agent_data = parser.parsear_datos_agente(data_returned)
            status = agent_data.get('status', 'OFFLINE')
        return status, error
