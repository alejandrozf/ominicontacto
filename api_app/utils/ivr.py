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
from configuracion_telefonia_app.models import DestinoEntrante
from .logger import set_logger_message
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    RestablecerConfiguracionTelefonicaError, SincronizadorDeConfiguracionIVRAsterisk)


def escribir_nodo_ivr_config(self, ivr):
    try:
        sincronizador = SincronizadorDeConfiguracionIVRAsterisk()
        sincronizador.regenerar_asterisk(ivr)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False


def eliminar_nodo_ivr_config(self, ivr):
    try:
        sincronizador = SincronizadorDeConfiguracionIVRAsterisk()
        sincronizador.eliminar_y_regenerar_asterisk(ivr)
        return True
    except RestablecerConfiguracionTelefonicaError as e:
        set_logger_message(self, e)
        return False


def eliminar_nodos_y_asociaciones(self, ivr):
    destino_entrante = DestinoEntrante.get_nodo_ruta_entrante(ivr)
    # Eliminar OpcionDestino que lo tienen como destino_anterior
    destino_entrante.destinos_siguientes.all().delete()
    # Eliminar DestinoEntrante
    destino_entrante.delete()
