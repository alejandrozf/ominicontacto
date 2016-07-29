# -*- coding: utf-8 -*-

"""
Servicio de activación de Campañas y Templates.
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (QueueDialplanConfigCreator,
    QueueConfigFile, AsteriskConfigReloader)

logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class ActivacionQueueService(object):

    def __init__(self):
        self.dialplan_config_creator = QueueDialplanConfigCreator()
        self.config_file = QueueConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.dialplan_config_creator.create_dialplan()
        except:
            logger.exception("ActivacionCampanaTemplateService: error al "
                             "intentar dialplan_config_creator()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion del dialplan de Asterisk. ")

        try:
            ret = self.reload_asterisk_config.reload_config()
            if ret != 0:
                proceso_ok = False
                mensaje_error += ("Hubo un inconveniente al intenar recargar "
                                  "la configuracion de Asterisk. ")
        except:
            logger.exception("ActivacionQueueService: error al "
                             " intentar reload_config()")
            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion de colas de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))
        else:
            self.config_file.copy_asterisk()

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()
