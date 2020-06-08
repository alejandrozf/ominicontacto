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

from django.utils.translation import ugettext as _
from api_app.utiles import AgentesParsing
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.models import AgenteProfile


class SupervisorActivityAmiManager(object):

    EXTENSIONES = ["AGENTLOGOUT", "AGENTUNPAUSE", "AGENTPAUSE", "CHANTAKECALL",
                   "CHANSPYWISHPER", "CHANSPY", "CHANCONFER"]

    manager = AMIManagerConnector()
    agent_activity = AgentActivityAmiManager()

    def originate_call(self, originate_data):
        content = originate_data
        data_returned = self.manager._ami_manager('originate', content)
        return data_returned

    def _obtener_agentes_activos(self):
        agentes_parseados = AgentesParsing()
        agentes_activos = []
        data_returned, error = self.manager._ami_manager("command", "database show OML/AGENT")
        agentes_activos = agentes_parseados._parsear_datos_agentes(data_returned)
        return agentes_activos

    def ejecutar_accion_sobre_agente(self, supervisor, agente_id, exten):
        agente_profile = AgenteProfile.objects.get(id=agente_id)
        supervisor_activity = SupervisorActivityAmiManager()
        if exten not in self.EXTENSIONES:
            return _("La acción indicada no existe")
        channel = "PJSIP/{0}".format(supervisor.sip_extension)
        channel_vars = {'OMLAGENTID': str(agente_id), }
        originate_data = [channel, exten, 'oml-sup-actions', channel_vars]
        # Genero la llamada via originate por AMI
        if exten == "AGENTLOGOUT":
            agente_profile.force_logout()
            self.agent_activity.logout_agent(agente_profile)
        elif exten == "AGENTPAUSE":
            self.agent_activity.pause_agent(agente_profile, '00')
        elif exten == "AGENTUNPAUSE":
            self.agent_activity.unpause_agent(agente_profile, '00')
        else:
            supervisor_activity.originate_call(originate_data)

    def escribir_agentes_unavailable_astdb(self):
        agentes_profiles = []
        user_activity_list, error = self.manager._ami_manager('command', 'queue show')
        for activity_line in user_activity_list.splitlines():
            if activity_line.find("Unavailable") != -1:
                fields_activity = activity_line.split()
                agente_id = fields_activity[1].split('_')[0]
                agente_profile = AgenteProfile.objects.get(id=agente_id)
                if agente_profile not in agentes_profiles:
                    agentes_profiles.append(agente_profile)
        for agente_profile in agentes_profiles:
            self.agent_activity._insert_astb_status(agente_profile, 'UNAVAILABLE')
