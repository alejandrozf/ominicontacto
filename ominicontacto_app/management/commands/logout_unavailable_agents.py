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
from django.contrib.sessions.models import Session
from django.utils.timezone import now

from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager

from ominicontacto_app.models import AgenteProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Comando para desloguear agentes que no se hayan deslogueado correctamente
    """

    help = u"Comando para desloguear agentes que no se hayan deslogueado correctamente"

    def logout_expired_sessions(self):
        agentes_deslogueados = []
        agent_activity = AgentActivityAmiManager()
        hora_actual = now()
        for agente_profile in AgenteProfile.objects.all():
            session = None
            if agente_profile.user.last_session_key:
                try:
                    session = Session.objects.get(session_key=agente_profile.user.last_session_key)
                except Session.DoesNotExist:
                    pass
            if session and session.expire_date < hora_actual:
                agentes_deslogueados.append(str(agente_profile.id))
                agente_profile.force_logout()
                agent_activity.logout_agent(agente_profile)

        if agentes_deslogueados:
            logger.info("Expired Sessions detected: " + str(agentes_deslogueados))

    """
    Comando para desloguear agentes que no se hayan deslogueado correctamente
    """

    help = u"Comando para desloguear agentes que no se hayan deslogueado correctamente"

    def set_astdb_unavailable_state(self):
        supervisor_activity = SupervisorActivityAmiManager()
        supervisor_activity.escribir_agentes_unavailable_astdb()

    def handle(self, *args, **options):
        try:
            self.logout_expired_sessions()
            self.set_astdb_unavailable_state()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
            raise CommandError('Fallo del comando: {0}'.format(e.message))
