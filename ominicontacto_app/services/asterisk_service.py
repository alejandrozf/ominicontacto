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

""" Servicio de interaccion con asterisk"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.asterisk_config import (
    SipConfigCreator, SipConfigFile, AsteriskConfigReloader)
from ominicontacto_app.errors import OmlError
from ominicontacto_app.services.asterisk_database import AgenteFamily
logger = logging.getLogger(__name__)


class RestablecerConfigSipError(OmlError):
    """Indica que se produjo un error al crear el config sip."""
    pass


class ActivacionAgenteService(object):
    """Este servicio regenera y recarga los archivos de configuracion para los agentes"""

    def __init__(self):
        self.sip_config_creator = SipConfigCreator()
        self.config_file = SipConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()
        self.asterisk_database = AgenteFamily()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.sip_config_creator.create_config_sip()
        except:
            logger.exception("ActivacionAgenteService: error al "
                             "intentar create_config_sip()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del config sip de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerConfigSipError(mensaje_error))
        else:
            self.config_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()
            self.asterisk_database.regenerar_families()

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()
