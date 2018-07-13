# -*- coding: utf-8 -*-

"""
Servicio de regenarción de la configuracion de telefonia
"""

from __future__ import unicode_literals

import logging

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, RutasSalientesConfigCreator, RutasSalientesConfigFile,
    SipTrunksConfigCreator, SipRegistrationsConfigCreator, SipTrunksConfigFile,
    SipRegistrationsConfigFile
)
from ominicontacto_app.services.asterisk_database import RutaSalienteFamily, TrunkFamily

logger = logging.getLogger(__name__)


class RestablecerConfiguracionTelefonicaError(OmlError):
    """Indica que se produjo un error al crear regenerar archivos de asterisk ó insetar en
    asterisk."""
    pass


class SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk(object):

    def __init__(self):
        self.generador_rutas_en_astdb = RutaSalienteFamily()
        self.generador_rutas_en_asterisk_conf = RutasSalientesConfigCreator()
        self.config_rutas_file = RutasSalientesConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_archivos_conf_asterisk(self, ruta_exclude=None):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_rutas_en_asterisk_conf.create_config_asterisk(ruta_exclude=ruta_exclude)
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

    def _generar_e_insertar_en_astdb(self, ruta):
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.create_families(modelo=ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAstDB: error al "
                             "intentar regenerar_familys_rutas()")

            mensaje_error += ("Hubo un inconveniente al insertar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_ruta_en_astdb(self, ruta):
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.delete_family_ruta(ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAstDB: error al "
                             "intentar delete_family_ruta()")

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _regenerar_troncales_ruta_en_astdb(self, ruta):
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.regenerar_family_trunk_ruta(ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAstDB: error al "
                             "intentar delete_family_ruta()")

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def regenerar_rutas_salientes(self, ruta=None):
        self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb(ruta)

    def eliminar_ruta_y_regenerar_asterisk(self, ruta):
        self._generar_y_recargar_archivos_conf_asterisk(ruta_exclude=ruta)
        self._eliminar_ruta_en_astdb(ruta)

    def regenerar_troncales_en_ruta_asterisk(self, ruta):
        self._regenerar_troncales_ruta_en_astdb(ruta)


class SincronizadorDeConfiguracionTroncalSipEnAsterisk(object):

    def __init__(self):
        self.generador_trunk_en_astdb = TrunkFamily()
        self.generador_trunk_sip_en_asterisk_conf = SipTrunksConfigCreator()
        self.config_trunk_file = SipTrunksConfigFile()
        self.generador_trunks_registration_en_asterisk_conf = SipRegistrationsConfigCreator()
        self.config_trunk_registration_file = SipRegistrationsConfigFile()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_archivos_conf_asterisk(self, trunk_exclude=None):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_trunk_sip_en_asterisk_conf.create_config_asterisk(
                trunk_exclude=trunk_exclude)
        except:
            logger.exception("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error al "
                             "intentar create_config_asterisk()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion de trunks de Asterisk. ")

        try:
            self.generador_trunks_registration_en_asterisk_conf.create_config_asterisk(
                trunk_exclude=trunk_exclude)
        except:
            logger.exception("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error al "
                             "intentar create_config_asterisk()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al crear el archivo de "
                              "configuracion de trunks registration de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerConfiguracionTelefonicaError(mensaje_error))
        else:
            self.config_trunk_file.copy_asterisk()
            self.config_trunk_registration_file.copy_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def _generar_e_insertar_en_astdb(self, trunk):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_trunk_en_astdb.create_families(modelo=trunk)
        except:
            logger.exception("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error al "
                             "intentar regenerar_familys_rutas()")

            proceso_ok = False
            mensaje_error += ("Hubo un inconveniente al insertar los registros del troncal en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_trunk_en_astdb(self, trunk):
        mensaje_error = ""

        try:
            self.generador_trunk_en_astdb.delete_family(trunk)
        except:
            logger.exception("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error al "
                             "intentar delete_family_trunk()")

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de los troncales en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def regenerar_troncales(self, trunk=None):
        self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb(trunk)

    def eliminar_troncal_y_regenerar_asterisk(self, trunk):
        self._generar_y_recargar_archivos_conf_asterisk(trunk_exclude=trunk)
        self._eliminar_trunk_en_astdb(trunk)
