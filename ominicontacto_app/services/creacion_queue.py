# -*- coding: utf-8 -*-

"""
Servicio de activación de Campañas y Templates.
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import QueueDialplanConfigCreator

logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class ActivacionQueueService(object):

    def __init__(self):
        self.dialplan_config_creator = QueueDialplanConfigCreator()

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

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))

    def activar(self):
        self._generar_y_recargar_configuracion_asterisk()