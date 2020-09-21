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

import redis

from time import time

from django.conf import settings
from django.utils.translation import ugettext as _

from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.models import AgenteProfile

LONGITUD_MINIMA_HEADERS = 4


class SupervisorActivityAmiManager(object):

    EXTENSIONES = ["AGENTLOGOUT", "AGENTUNPAUSE", "AGENTPAUSE", "CHANTAKECALL",
                   "CHANSPYWISHPER", "CHANSPY", "CHANCONFER"]

    def __init__(self, *args, **kwargs):
        self.manager = AMIManagerConnector()
        self.agent_activity = AgentActivityAmiManager()

    def _originate_call(self, originate_data):
        self.manager.connect()
        content = originate_data
        data_returned = self.manager._ami_manager('originate', content)
        self.manager.disconnect()
        return data_returned

    def obtener_agentes_activos(self):
        agentes_activos = []
        redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME, port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        # TODO: cambiar a usar el metodo 'scan' que es mas eficiente con datos muy grandes
        # y realiza una especie de paginación
        keys_agentes = redis_connection.keys('OML:AGENT*')
        agentes_activos = []
        for key in keys_agentes:
            agente_info = redis_connection.hgetall(key)
            status = agente_info.get('STATUS', '')
            id_agente = key.split(':')[-1]
            if status != '' and len(agente_info) >= LONGITUD_MINIMA_HEADERS:
                agente_info['nombre'] = agente_info['NAME']
                agente_info['status'] = status
                agente_info['sip'] = agente_info['SIP']
                agente_info['pause_id'] = agente_info.get('PAUSE_ID', '')
                agente_info['campana_llamada'] = agente_info.get('CAMPAIGN', '')
                agente_info['contacto'] = agente_info.get('CONTACT_NUMBER', '')
                tiempo_actual = int(time())
                tiempo_estado = tiempo_actual - int(agente_info['TIMESTAMP'])
                agente_info['tiempo'] = tiempo_estado
                del agente_info['NAME']
                del agente_info['STATUS']
                del agente_info['TIMESTAMP']
                del agente_info['SIP']
                agente_info['id'] = int(id_agente)
                agentes_activos.append(agente_info)
        return agentes_activos

    def ejecutar_accion_sobre_agente(self, supervisor, agente_id, exten):
        agente_profile = AgenteProfile.objects.get(id=agente_id)
        if exten not in self.EXTENSIONES:
            return _("La acción indicada no existe")
        channel = "PJSIP/{0}".format(supervisor.sip_extension)
        channel_vars = {'OMLAGENTID': str(agente_id), }
        originate_data = [channel, exten, 'oml-sup-actions', channel_vars]
        # Genero la llamada via originate por AMI
        if exten == "AGENTLOGOUT":
            agente_profile.force_logout()
            self.agent_activity.logout_agent(agente_profile, manage_connection=True)
        elif exten == "AGENTPAUSE":
            self.agent_activity.pause_agent(agente_profile, '00', manage_connection=True)
        elif exten == "AGENTUNPAUSE":
            self.agent_activity.unpause_agent(agente_profile, '00', manage_connection=True)
        else:
            self._originate_call(originate_data)

    def escribir_estado_agentes_unavailable(self):
        """ Busca en el queue de Asterisk si hay agentes Unavailable para reportarlo en Redis"""
        self.manager.connect()
        user_activity_list, error = self.manager._ami_manager('command', 'queue show')
        self.manager.disconnect()

        agentes_profiles = []
        for activity_line in user_activity_list.splitlines():
            if activity_line.find("Unavailable") != -1:
                fields_activity = activity_line.split()
                agente_id = fields_activity[1].split('_')[0]
                agente_profile = AgenteProfile.objects.get(id=agente_id)
                if agente_profile not in agentes_profiles:
                    agentes_profiles.append(agente_profile)

        if agentes_profiles:
            for agente_profile in agentes_profiles:
                self.agent_activity.set_agent_as_unavailable(agente_profile)
