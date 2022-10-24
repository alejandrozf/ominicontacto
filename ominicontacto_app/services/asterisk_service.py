# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

""" Servicio de interaccion con asterisk"""

from __future__ import unicode_literals

import logging

from django.utils.translation import gettext as _

from ominicontacto_app.asterisk_config import (
    SipConfigCreator, AsteriskConfigReloader)
from ominicontacto_app.errors import OmlError
from ominicontacto_app.services.asterisk.redis_database import AgenteFamily
logger = logging.getLogger(__name__)


class RestablecerConfigSipError(OmlError):
    """Indica que se produjo un error al crear el config sip."""
    pass


class ActivacionAgenteService(object):
    """Este servicio regenera y recarga los archivos de configuracion para los agentes"""

    def __init__(self):
        self.sip_config_creator = SipConfigCreator()
        self.reload_asterisk_config = AsteriskConfigReloader()
        self.asterisk_database = AgenteFamily()

    def _generar_y_recargar_configuracion_asterisk(self, regenerar_families=True, agente=None,
                                                   preservar_status=False):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.sip_config_creator.create_config_sip()
        except Exception as e:
            msg = _("Error {0}: ActivacionAgenteService: error al ".format(e) +
                    "intentar create_config_sip()")
            logger.exception(msg)

            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion del config sip de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerConfigSipError(mensaje_error))
        else:
            self.reload_asterisk_config.reload_asterisk()
            if regenerar_families:
                if agente is None:
                    self.asterisk_database.regenerar_families()
                else:
                    self.asterisk_database.regenerar_family(
                        agente, preservar_status=preservar_status)

    def activar(self, regenerar_families=True):
        self._generar_y_recargar_configuracion_asterisk(regenerar_families=regenerar_families)

    def activar_agente(self, agente, preservar_status=False):
        self._generar_y_recargar_configuracion_asterisk(
            regenerar_families=True, agente=agente, preservar_status=preservar_status)
