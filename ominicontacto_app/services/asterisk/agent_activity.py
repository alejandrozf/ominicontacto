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


class AgentActivityAmiManager(object):

    manager = AMIManagerConnector()

    def login_agent(self, agente_profile):
        queue_add_error = self.queue_add_remove(agente_profile, 'QueueAdd')
        insert_astdb_error = self.insert_astdb(agente_profile, 'login')
        queue_unpause_error = self.queue_pause_unpause(agente_profile, '', 'unpause')
        return queue_add_error, insert_astdb_error, queue_unpause_error

    def logout_agent(self, agente_profile):
        self.queue_add_remove(agente_profile, 'QueueRemove')
        self.insert_astdb(agente_profile, 'logout')

    def pause_agent(self, agente_profile, pause_id):
        pause_name = ''
        queue_pause_error = self.queue_pause_unpause(agente_profile, pause_id, 'pause')
        if pause_id == '0':
            pause_name = 'ACW'
        elif pause_id == '00':
            pause_name = 'Supervision'
        else:
            pause_name = Pausa.objects.activa_by_pauseid(pause_id).nombre
        insert_astdb_error = self.insert_astdb(agente_profile, 'PAUSE-' + str(pause_name))
        return queue_pause_error, insert_astdb_error

    def unpause_agent(self, agente_profile, pause_id):
        queue_unpause_error = self.queue_pause_unpause(agente_profile, pause_id, 'unpause')
        insert_astdb_error = self.insert_astdb(agente_profile, 'unpause')
        return queue_unpause_error, insert_astdb_error

    def get_pause_id(self, pause_id):
        return pause_id

    def get_astdb_data(self, agente_profile, action):
        agente_family = AgenteFamily()
        tiempo_actual = int(time.time())
        family = agente_family._get_nombre_family(agente_profile)
        key = 'STATUS'
        if action == 'login' or action == 'unpause':
            value = 'READY:' + str(tiempo_actual)
        elif action == 'logout':
            value = 'OFFLINE:' + str(tiempo_actual)
        elif 'PAUSE' in action:
            value = action + ':' + str(tiempo_actual)
        content = [family, key, value]
        return content

    def get_queue_data(self, agente_profile):
        agent_id = agente_profile.id
        member_name = agente_profile.get_asterisk_caller_id()
        queues = QueueMember.objects.obtener_queue_por_agent(agent_id)
        penalties = QueueMember.objects.obtener_penalty_por_agent(agent_id)
        sip_extension = agente_profile.sip_extension
        interface = "SIP/" + str(sip_extension).strip('[]')
        content = [agent_id, member_name, queues, penalties, interface]
        return content

    def queue_add_remove(self, agente_profile, action):
        content = self.get_queue_data(agente_profile)
        data_returned, error = self.manager._ami_manager(action, content)
        return error

    def queue_pause_unpause(self, agente_profile, pause_id, action):
        if action == 'unpause':
            pause_state = 'false'
        elif action == 'pause':
            pause_state = 'true'
        content = self.get_queue_data(agente_profile)
        content.append(pause_id)
        content.append(pause_state)
        data_returned, error = self.manager._ami_manager('QueuePause', content)

    def insert_astdb(self, agente_profile, action):
        content = self.get_astdb_data(agente_profile, action)
        data_returned, error = self.manager._ami_manager('dbput', content)
        return error
