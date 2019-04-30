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

from ominicontacto_app.services.asterisk_ami_http import (
    AsteriskHttpClient, AsteriskHttpOriginateError
)
import logging as _logging


logger = _logging.getLogger(__name__)


ACCIONES = ["AGENTLOGOUT", "AGENTUNPAUSE", "AGENTPAUSE", "CHANTAKECALL",
            "CHANSPYWISHPER", "CHANSPY", "CHANCONFER"]


class AccionesDeSupervisorSobreAgente(object):

    def ejecutar_accion(self, supervisor, agente_id, accion):
        if accion not in ACCIONES:
            return _("La acción indicada no existe")
        channel = "SIP/{0}".format(supervisor.sip_extension)
        # Genero la llamada via originate por AMI
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate(channel=channel,
                             context="oml-sup-actions",
                             es_aplication=False,
                             variables_de_canal={'OMLAGENTID': str(agente_id), },
                             async=True,
                             aplication=None,
                             exten=accion,
                             priority=1,
                             timeout=25000)

        except AsteriskHttpOriginateError:
            error = _("Originate failed - accion: '{0}' - agente_id: {1} ".format(
                      accion, agente_id))
            logger.exception(error)
            return error

        except Exception as e:
            error = _("Originate failed by {0} - accion: '{1}' - agente_id: {2}".format(
                      e, accion, agente_id))
            logger.exception(error)
            return error
