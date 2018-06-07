# -*- coding: utf-8 -*-

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
            self.asterisk_database.regenerar_familys_agente()

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()
