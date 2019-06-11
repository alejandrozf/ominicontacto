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


class Click2CallOriginator(object):
    AGENT = 'AGENT'
    EXTERNAL = 'EXTERNAL'

    def call_originate(self, agente, campana_id, tipo_campana,
                       contacto_id, telefono,
                       click2call_type):
        variables = {
            'IdCamp': str(campana_id),
            'codCli': str(contacto_id),
            'origin': click2call_type,
            'Tipocamp': tipo_campana,
            'FTSAGENTE': "{0}_{1}".format(agente.id,
                                          agente.user.get_full_name())
        }
        channel = "Local/{0}@click2call/n".format(agente.sip_extension)
        # Genero la llamada via originate por AMI
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate(channel, "from-internal", False, variables, True,
                             exten=telefono, priority=1, timeout=45000)

        except AsteriskHttpOriginateError:
            error = _("Originate failed - contacto: {0} ".format(telefono))
            logger.exception(error)
            return error

        except Exception as e:
            error = _("Originate failed by {0} - contacto: {1}".format(e, telefono))
            logger.exception(error)
            return error

    def call_agent(self, agente_origen, agente_destino):
        return self._call_without_campaign(agente_origen, self.AGENT, str(agente_destino.id))

    def call_external(self, agente, numero):
        return self._call_without_campaign(agente, self.EXTERNAL, numero)

    def _call_without_campaign(self, agente, tipo_destino, numero):
        variables = {
            'origin': 'withoutCamp',
            'FTSAGENTE': "{0}_{1}".format(agente.id,
                                          agente.user.get_full_name())
        }
        if tipo_destino == self.AGENT:
            context = 'oml-dial-internal'
            exten = self.AGENT
            variables['agent2Call'] = numero
        else:   # tipo_destino == self.EXTERNAL
            context = 'oml-dial-out'
            exten = numero

        channel = "Local/{0}@click2call/n".format(agente.sip_extension)

        # Genero la llamada via originate por AMI
        try:
            client = AsteriskHttpClient()
            client.login()
            client.originate(channel, context, False, variables, True,
                             exten=exten, priority=1, timeout=45000)

        except AsteriskHttpOriginateError:
            error = _("Originate failed - tipo_destino: {0}  - numero {1}".format(
                tipo_destino, numero))
            logger.exception(error)
            return error

        except Exception as e:
            error = _("Originate failed by {0} - tipo_destino: {1}  - numero {2}".format(
                e, tipo_destino, numero))
            logger.exception(error)
            return error
