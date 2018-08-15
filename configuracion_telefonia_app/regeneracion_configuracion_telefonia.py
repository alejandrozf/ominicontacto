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
from ominicontacto_app.services.asterisk_database import (
    RutaSalienteFamily, TrunkFamily, RutaEntranteFamily, IVRFamily, ValidacionFechaHoraFamily,
    GrupoHorarioFamily, PausaFamily
)

logger = logging.getLogger(__name__)


class SincronizadorDeConfiguracionTelefonicaEnAsterisk(object):

    def __init__(self):
        self.sincronizador_troncales = SincronizadorDeConfiguracionTroncalSipEnAsterisk()
        self.sincronizador_ruta_saliente = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        self.sincronizador_ruta_entrante = SincronizadorDeConfiguracionRutaEntranteAsterisk()
        self.sincronizador_grupo_horario = SincronizadorDeConfiguracionGrupoHorarioAsterisk()
        self.sincronizador_validacion_fh = SincronizadorDeConfiguracionValidacionFechaHoraAsterisk()
        self.sincronizador_ivr = SincronizadorDeConfiguracionIVRAsterisk()

    def sincronizar_en_asterisk(self):
        self.sincronizador_troncales.regenerar_troncales()
        self.sincronizador_ruta_saliente.regenerar_rutas_salientes()
        self.sincronizador_ruta_entrante.regenerar_asterisk()
        self.sincronizador_grupo_horario.regenerar_asterisk()
        self.sincronizador_validacion_fh.regenerar_asterisk()
        self.sincronizador_ivr.regenerar_asterisk()


class RestablecerConfiguracionTelefonicaError(OmlError):
    """Indica que se produjo un error al crear regenerar archivos de asterisk ó insetar en
    asterisk."""
    pass


# TODO: Refactorizar para que extienda de AbstractConfiguracionAsterisk
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
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk: error al "
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
            if ruta is None:
                self.generador_rutas_en_astdb.regenerar_families()
            else:
                self.generador_rutas_en_astdb.regenerar_family(ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk: error al "
                             "intentar regenerar_familys_rutas()")

            mensaje_error += ("Hubo un inconveniente al insertar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_ruta_en_astdb(self, ruta):
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.delete_family(ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk: error al "
                             "intentar delete_family_ruta()")

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _regenerar_troncales_ruta_en_astdb(self, ruta):
        mensaje_error = ""

        try:
            self.generador_rutas_en_astdb.regenerar_family_trunk_ruta(ruta)
        except:
            logger.exception("SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk: error al "
                             "intentar delete_family_ruta()")

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de las rutas en "
                              "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def regenerar_rutas_salientes(self, ruta=None):
        """regenera la ruta saliente pasada por parametro y si la ruta es none regenera todas las
        rutas salientes """
        self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb(ruta)

    def eliminar_ruta_y_regenerar_asterisk(self, ruta):
        self._generar_y_recargar_archivos_conf_asterisk(ruta_exclude=ruta)
        self._eliminar_ruta_en_astdb(ruta)

    def regenerar_troncales_en_ruta_asterisk(self, ruta):
        self._regenerar_troncales_ruta_en_astdb(ruta)


# TODO: Refactorizar para que extienda de AbstractConfiguracionAsterisk
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
        mensaje_error = ""

        try:
            if trunk is None:
                self.generador_trunk_en_astdb.regenerar_families()
            else:
                self.generador_trunk_en_astdb.regenerar_family(trunk)
        except:
            logger.exception("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error al "
                             "intentar regenerar_familys_rutas()")
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


class AbstractConfiguracionAsterisk(object):

    def _obtener_generador_family(self):
        raise (NotImplementedError())

    def _generar_e_insertar_en_astdb(self, family_member=None):
        mensaje_error = ""
        generador_family = self._obtener_generador_family()
        nombre_families = generador_family.get_nombre_families()
        try:
            if family_member is None:
                generador_family.regenerar_families()
            else:
                generador_family.regenerar_family(family_member)
        except:
            logger.exception("Error en la families {0} "
                             "intentar regenerar_family()".format(nombre_families))
            mensaje_error += ("Hubo un inconveniente al insertar los registros de la family {0} "
                              "la base de datos de Asterisk. ".format(nombre_families))
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_family_en_astdb(self, family_member):
        mensaje_error = ""
        generador_family = self._obtener_generador_family()
        nombre_families = generador_family.get_nombre_families()
        try:
            generador_family.delete_family(family_member)
        except:
            logger.exception("Error en la families {0} "
                             "intentar delete_family()".format(nombre_families))

            mensaje_error += ("Hubo un inconveniente al eliminar los registros de la families {0}"
                              "la base de datos de Asterisk. ".format(nombre_families))
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def regenerar_asterisk(self, family_member=None):
        # self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb(family_member)

    def eliminar_y_regenerar_asterisk(self, family_member):
        self._eliminar_family_en_astdb(family_member)


class SincronizadorDeConfiguracionRutaEntranteAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = RutaEntranteFamily()
        return generador


class SincronizadorDeConfiguracionIVRAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = IVRFamily()
        return generador


class SincronizadorDeConfiguracionValidacionFechaHoraAsterisk(AbstractConfiguracionAsterisk):
    def _obtener_generador_family(self):
        generador = ValidacionFechaHoraFamily()
        return generador


class SincronizadorDeConfiguracionGrupoHorarioAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = GrupoHorarioFamily()
        return generador


class SincronizadorDeConfiguracionPausaAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        return PausaFamily()
