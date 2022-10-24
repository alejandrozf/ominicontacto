# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

import logging
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    RestablecerConfiguracionTelefonicaError,
    SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk)
logger = logging.getLogger(__name__)


def set_logger_message(self, msg):
    logger.error("RestablecerConfiguracionTelefonicaError!: \n"
                 "No se realizo de manera correcta "
                 "la regeneracion de datos en asterisk "
                 "según el siguiente error: {0}".format(msg))


def escribir_ruta_saliente_config(self, ruta_saliente):
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.regenerar_asterisk(ruta_saliente)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False


def eliminar_ruta_saliente_config(self, ruta_saliente):
    try:
        sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
        sincronizador.eliminar_y_regenerar_asterisk(ruta_saliente)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False


def generar_y_recargar_archivos_conf_asterisk(self):
    sincronizador = SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk()
    sincronizador._generar_y_recargar_archivos_conf_asterisk()
