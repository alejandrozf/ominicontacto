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

import logging

from django.core.management.base import BaseCommand, CommandError

from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager

from ominicontacto_app.models import AgenteProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Comando para desloguear agentes que no se hayan deslogueado correctamente
    """

    help = u"Comando para desloguear agentes que no se hayan deslogueado correctamente"

    def get_agents_unavailable(self):
        agentes_profiles = []
        manager = AMIManagerConnector()
        agent_activity = AgentActivityAmiManager()
        user_activity_list, error = manager._ami_manager('command', 'queue show')
        for activity_line in user_activity_list.splitlines():
            if activity_line.find("Unavailable") != -1:
                fields_activity = activity_line.split()
                agente_id = fields_activity[1].split('_')[0]
                agente_profile = AgenteProfile.objects.get(id=agente_id)
                if agente_profile not in agentes_profiles:
                    agentes_profiles.append(agente_profile)
        for agente_profile in agentes_profiles:
            agent_activity.logout_agent(agente_profile)

    def handle(self, *args, **options):
        try:
            self.get_agents_unavailable()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
            raise CommandError('Fallo del comando: {0}'.format(e.message))
