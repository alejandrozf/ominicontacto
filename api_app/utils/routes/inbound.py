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
from .outbound import set_logger_message
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    RestablecerConfiguracionTelefonicaError, SincronizadorDeConfiguracionRutaEntranteAsterisk)


def escribir_ruta_entrante_config(self, ruta_entrante):
    try:
        sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
        sincronizador.regenerar_asterisk(ruta_entrante)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False


def eliminar_ruta_entrante_config(self, ruta_entrante):
    try:
        sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
        sincronizador.eliminar_y_regenerar_asterisk(ruta_entrante)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False
