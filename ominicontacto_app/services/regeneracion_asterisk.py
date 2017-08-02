# -*- coding: utf-8 -*-

"""
Servicio de regenarción de archivos de asterisk y reload del mismo
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    QueueDialplanConfigCreator, QueueConfigFile, AsteriskConfigReloader,
    QueuesCreator, QueuesConfigFile, SipConfigCreator, SipConfigFile,
    GlobalsVariableConfigCreator, GlobalsConfigFile)

logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class RegeneracionAsteriskService(object):

    def __init__(self):
        self.dialplan_config_creator = QueueDialplanConfigCreator()
        self.config_file = QueueConfigFile()
        self.queues_config_creator = QueuesCreator()
        self.config_queues_file = QueuesConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()
        self.sip_config_creator = SipConfigCreator()
        self.config_sip_file = SipConfigFile()
        self.globals_config_creator = GlobalsVariableConfigCreator()
        self.config_globals_file = GlobalsConfigFile()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.dialplan_config_creator.create_dialplan()
        except:
            logger.exception("ActivacionQueueService: error al "
                             "intentar dialplan_config_creator()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del dialplan de Asterisk. ")

        try:
            self.queues_config_creator.create_dialplan()
        except:
            logger.exception("ActivacionQueueService: error al "
                             "intentar queues_config_creator()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del queues de Asterisk. ")

        try:
            self.sip_config_creator.create_config_sip()
        except:
            logger.exception("ActivacionAgenteService: error al "
                             "intentar create_config_sip()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del config sip de Asterisk. ")

        try:
            self.globals_config_creator.create_config_sip()
        except:
            logger.exception("ActivacionAgenteService: error al "
                             "intentar create_config_sip()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del config sip de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))
        else:
            self.config_file.copy_asterisk()
            self.config_sip_file.copy_asterisk()
            self.config_queues_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()
            self.config_globals_file.copy_asterisk()

    def regenerar(self):
        self._generar_y_recargar_configuracion_asterisk()
