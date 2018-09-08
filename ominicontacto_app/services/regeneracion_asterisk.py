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

"""
Servicio de regenarción de archivos de asterisk y reload del mismo
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, QueuesCreator, QueuesConfigFile, SipConfigCreator,
    SipConfigFile
)
from ominicontacto_app.services.asterisk_database import RegenerarAsteriskFamilysOML
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTelefonicaEnAsterisk)

logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class RegeneracionAsteriskService(object):

    def __init__(self):
        # Sincroniza Queues de Campañas
        self.queues_config_creator = QueuesCreator()
        self.config_queues_file = QueuesConfigFile()
        # Sincroniza Sip De Agentes
        self.sip_config_creator = SipConfigCreator()
        self.config_sip_file = SipConfigFile()
        # Sincroniza Modelos de Configuracion Telefonica
        self.sincronizador_config_telefonica = SincronizadorDeConfiguracionTelefonicaEnAsterisk()
        # Sincroniza en AstDB las que faltan en el Sincronizador de Configuracion Telefonica
        self.asterisk_database = RegenerarAsteriskFamilysOML()

        # Llama al comando que reinicia Asterisk
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.queues_config_creator.create_dialplan()
        except Exception:
            logger.exception("ActivacionQueueService: error al "
                             "intentar queues_config_creator()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del queues de Asterisk. ")

        try:
            self.sip_config_creator.create_config_sip()
        except Exception:
            logger.exception("ActivacionAgenteService: error al "
                             "intentar create_config_sip()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del config sip de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))
        else:
            self.config_queues_file.copy_asterisk()
            self.config_sip_file.copy_asterisk()
            self.sincronizador_config_telefonica.sincronizar_en_asterisk()
            self.asterisk_database.regenerar_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def regenerar(self):
        self._generar_y_recargar_configuracion_asterisk()
