# -*- coding: utf-8 -*-

"""
Servicio de regenarción de la configuracion de telefonia
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, RutasSalientesConfigCreator, RutasSalientesConfigFile
)
from ominicontacto_app.services.asterisk_database import RutaSalienteFamily

logger = logging.getLogger(__name__)


class RestablecerConfiguracionTelefonicaError(OmlError):
    """Indica que se produjo un error al crear regenerar archivos de asterisk ó insetar en asterisk."""
    pass


class SincronizadorDeConfiguracionDeRutaSalienteEnAstDB(object):

    def __init__(self):
        self.generador_rutas_en_astdb = RutaSalienteFamily()
        self.generador_rutas_en_asterisk_conf = RutasSalientesConfigCreator()
        self.config_rutas_file = RutasSalientesConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_archivos_conf_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_rutas_en_asterisk_conf.create_config_asterisk()
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAstDB: error al "
                             "intentar create_config_asterisk()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion de rutas de Asterisk. ")
        if not proceso_ok:
            raise(RestablecerConfiguracionTelefonicaError(mensaje_error))
        else:
            self.config_rutas_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def _generar_e_insertar_en_astdb(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.regenerar_familys_rutas()
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAstDB: error al "
                             "intentar regenerar_familys_rutas()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al insertar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def regenerar_rutas_salientes(self):
        self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb()
