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
