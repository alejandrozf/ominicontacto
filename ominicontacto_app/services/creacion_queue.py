# -*- coding: utf-8 -*-

"""
Servicio vinculado a la creacion de una cola pero principalmente con generacion de los
archivos extensions_fts_queues.conf y queues_fts.conf
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, QueuesCreator, QueuesConfigFile)
from ominicontacto_app.services.asterisk_database import CampanaFamily

logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class ActivacionQueueService(object):

    def __init__(self):
        self.queues_config_creator = QueuesCreator()
        self.config_queues_file = QueuesConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()
        self.asterisk_database = CampanaFamily()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.queues_config_creator.create_dialplan()
        except:
            logger.exception("ActivacionQueueService: error al "
                             "intentar queues_config_creator()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del queues de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))
        else:
            self.config_queues_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()
            self.asterisk_database.regenerar_families()

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()
