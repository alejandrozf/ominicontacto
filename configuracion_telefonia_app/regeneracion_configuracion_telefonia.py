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
Servicio de regenarción de la configuracion de telefonia
"""

from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, RutasSalientesConfigCreator,
    SipTrunksConfigCreator, SipRegistrationsConfigCreator,
)
from ominicontacto_app.services.asterisk.redis_database import (
    RutaSalienteFamily, IVRFamily, ValidacionFechaHoraFamily, GrupoHorarioFamily,
    IdentificadorClienteFamily, PausaFamily, TrunkFamily, RutaEntranteFamily,
    DestinoPersonalizadoFamily
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
        self.sincronizador_ruta_saliente.regenerar_asterisk()
        self.sincronizador_ruta_entrante.regenerar_asterisk()
        self.sincronizador_grupo_horario.regenerar_asterisk()
        self.sincronizador_validacion_fh.regenerar_asterisk()
        self.sincronizador_ivr.regenerar_asterisk()


class RestablecerConfiguracionTelefonicaError(OmlError):
    """Indica que se produjo un error al crear regenerar archivos de asterisk ó insetar en
    asterisk."""
    pass


# TODO: Refactorizar para que extienda de AbstractConfiguracionAsterisk
class SincronizadorDeConfiguracionTroncalSipEnAsterisk(object):

    def __init__(self):
        self.generador_trunk_en_astdb = TrunkFamily()
        self.generador_trunk_sip_en_asterisk_conf = SipTrunksConfigCreator()
        self.generador_trunks_registration_en_asterisk_conf = SipRegistrationsConfigCreator()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_archivos_conf_asterisk(self, trunk_exclude=None):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_trunk_sip_en_asterisk_conf.create_config_asterisk(
                trunk_exclude=trunk_exclude)
        except Exception as e:
            msg = _("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error {0} al ".format(
                e)) + _("intentar create_config_asterisk()")
            logger.exception(msg)
            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion de trunks de Asterisk. ")

        try:
            self.generador_trunks_registration_en_asterisk_conf.create_config_asterisk(
                trunk_exclude=trunk_exclude)
        except Exception as e:
            msg = _("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error {0} al ".format(
                e)) + _("intentar create_config_asterisk()")
            logger.exception(msg)
            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion de trunks registration de Asterisk. ")

        if not proceso_ok:
            raise(RestablecerConfiguracionTelefonicaError(mensaje_error))
        else:
            self.reload_asterisk_config.reload_asterisk()

    def _generar_e_insertar_en_astdb(self, trunk):
        mensaje_error = ""

        try:
            if trunk is None:
                self.generador_trunk_en_astdb.regenerar_families()
            else:
                self.generador_trunk_en_astdb.regenerar_family(trunk)
        except Exception as e:
            msg = _("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error {0} al ".format(
                e)) + _("intentar regenerar_familys_rutas()")
            logger.exception(msg)
            mensaje_error += _("Hubo un inconveniente al insertar los registros del troncal en "
                               "la base de datos de Asterisk. ")
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_trunk_en_astdb(self, trunk):
        mensaje_error = ""

        try:
            self.generador_trunk_en_astdb.delete_family(trunk)
        except Exception as e:
            msg = _("SincronizadorDeConfiguracionTroncalSipEnAsterisk: error {0} al ".format(
                e)) + _("intentar delete_family_trunk()")
            logger.exception(msg)
            mensaje_error += _("Hubo un inconveniente al eliminar los registros de los troncales"
                               " en la base de datos de Asterisk. ")
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
        except Exception as e:
            logger.exception(_("Error {0} en la family {1} "
                               "al intentar regenerar_family()".format(e, nombre_families)))
            mensaje_error += _("Hubo un inconveniente al insertar los registros de la family {0} "
                               "en la base de datos de Asterisk. ".format(nombre_families))
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _eliminar_family_en_astdb(self, family_member):
        mensaje_error = ""
        generador_family = self._obtener_generador_family()
        nombre_families = generador_family.get_nombre_families()
        try:
            generador_family.delete_family(family_member)
        except Exception as e:
            logger.exception(_("Error {0} en la family {1} al "
                               "intentar delete_family()".format(e, nombre_families)))
            mensaje_error += _("Hubo un inconveniente al eliminar los registros de la family {0} "
                               "en la base de datos de Asterisk. ".format(nombre_families))
            raise (RestablecerConfiguracionTelefonicaError(mensaje_error))

    def _generar_y_recargar_archivos_conf_asterisk(self, family_member_exclude=None):
        # Por defecto no tienen archivos conf.
        pass

    def regenerar_asterisk(self, family_member=None):
        self._generar_y_recargar_archivos_conf_asterisk()
        self._generar_e_insertar_en_astdb(family_member)

    def eliminar_y_regenerar_asterisk(self, family_member):
        self._generar_y_recargar_archivos_conf_asterisk(family_member_exclude=family_member)
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


class SincronizadorDeConfiguracionIdentificadorClienteAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = IdentificadorClienteFamily()
        return generador


class SincronizadorDeConfiguracionPausaAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        return PausaFamily()


class SincronizadorDeConfiguracionDestinoPersonalizadoAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = DestinoPersonalizadoFamily()
        return generador


class SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk(AbstractConfiguracionAsterisk):

    def _obtener_generador_family(self):
        generador = RutaSalienteFamily()
        return generador

    def __init__(self):
        super(SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk).__init__()
        self.generador_rutas_en_asterisk_conf = RutasSalientesConfigCreator()
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_archivos_conf_asterisk(self, family_member_exclude=None):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.generador_rutas_en_asterisk_conf.create_config_asterisk(
                ruta_exclude=family_member_exclude)
        except Exception as e:
            msg = _("SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk: error {0} al".format(
                e)) + _("intentar create_config_asterisk()")
            logger.exception(msg)

            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion de rutas de Asterisk. ")
        if not proceso_ok:
            raise(RestablecerConfiguracionTelefonicaError(mensaje_error))
        else:
            self.reload_asterisk_config.reload_asterisk()
