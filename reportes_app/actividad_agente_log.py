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
Empezo siendo un servicio ahora siemplemente tiene un objecto para guardar
los tiempo del agente
"""

from __future__ import unicode_literals, division

import datetime
import logging
from django.utils.translation import ugettext as _


logger = logging.getLogger(__name__)


class AgenteTiemposReporte(object):
    """Encapsula los datos de los tiempos de sesion, pausa y llamada del agente.
    """

    def __init__(self, agente, tiempo_sesion, tiempo_pausa, tiempo_llamada,
                 cantidad_llamadas_procesadas, cantidad_intentos_fallidos,
                 tiempo_llamada_saliente, cantidad_llamadas_saliente):

        self._agente = agente
        self._tiempo_sesion = tiempo_sesion
        self._tiempo_pausa = tiempo_pausa
        self._tiempo_llamada = tiempo_llamada
        self._cantidad_llamadas_procesadas = cantidad_llamadas_procesadas
        self._cantidad_intentos_fallidos = cantidad_intentos_fallidos
        self._tiempo_llamada_saliente = tiempo_llamada_saliente
        self._cantidad_llamadas_saliente = cantidad_llamadas_saliente

    @property
    def agente(self):
        return self._agente

    @property
    def tiempo_sesion(self):
        return self._tiempo_sesion

    @property
    def tiempo_pausa(self):
        return self._tiempo_pausa

    @property
    def tiempo_llamada(self):
        return self._tiempo_llamada

    @property
    def cantidad_llamadas_procesadas(self):
        return self._cantidad_llamadas_procesadas

    @property
    def cantidad_intentos_fallidos(self):
        return self._cantidad_intentos_fallidos

    def tiempo_promedio_llamadas(self):
        if self._cantidad_llamadas_procesadas:
            return float('%.2f' %
                         (self._tiempo_llamada.total_seconds() /
                          self._cantidad_llamadas_procesadas))
        return None

    @property
    def tiempo_llamada_saliente(self):
        return self._tiempo_llamada_saliente

    @property
    def cantidad_llamadas_saliente(self):
        return self._cantidad_llamadas_saliente

    @property
    def tiempo_porcentaje_llamada(self):
        if self.tiempo_llamada and self.tiempo_sesion:
            return self.tiempo_llamada.total_seconds() / self.tiempo_sesion.total_seconds() * 100
        return None

    @property
    def tiempo_porcentaje_pausa(self):
        if self.tiempo_pausa and self.tiempo_sesion:
            return self.tiempo_pausa.total_seconds() / self.tiempo_sesion.total_seconds() * 100
        return None

    @property
    def tiempo_wait(self):
        if self.tiempo_sesion:
            tiempo_wait = self.tiempo_sesion.total_seconds()
            if self.tiempo_pausa:
                tiempo_wait -= self.tiempo_pausa.total_seconds()
            if self.tiempo_llamada:
                tiempo_wait -= self.tiempo_llamada.total_seconds()
            return tiempo_wait
        else:
            return None

    @property
    def tiempo_porcentaje_wait(self):
        if self.tiempo_wait is not None and self.tiempo_wait > 0.0 and self.tiempo_sesion:
            return self.tiempo_wait / self.tiempo_sesion.total_seconds() * 100
        return None

    def _get_string(self, delta):
        if delta:
            dias = ''
            n_dias = delta.days
            if n_dias == 1:
                dias = _('1 día, ')
            elif n_dias > 1:
                dias = str(n_dias) + _(' días, ')
            return dias + str(datetime.timedelta(seconds=delta.seconds))
        return delta

    def get_string_tiempo_sesion(self):
        return self._get_string(self.tiempo_sesion)

    def get_string_tiempo_pausa(self):
        return self._get_string(self.tiempo_pausa)

    def get_string_tiempo_llamada(self):
        if self.tiempo_llamada:
            return datetime.timedelta(0, self.tiempo_llamada)
        return self.tiempo_llamada

    def get_promedio_llamadas(self):
        tiempo_llamada = self.tiempo_llamada.total_seconds()
        if tiempo_llamada > 0:
            promedio_llamadas = tiempo_llamada / self.cantidad_llamadas_procesadas
            return float('%.2f' % promedio_llamadas)
        return 0

    def get_nombre_agente(self):
        return self.agente.user.get_full_name()

    def get_media_asignada(self):
        if self.tiempo_llamada and self.tiempo_llamada_saliente:

            tiempo_asignadas = self.tiempo_llamada - self.tiempo_llamada_saliente
            media_asignadas = 0
            cantidad_asignadas = self._cantidad_llamadas_procesadas -\
                self._cantidad_llamadas_saliente
            if tiempo_asignadas > 0:
                media_asignadas = tiempo_asignadas / cantidad_asignadas
            return media_asignadas
        return 0

    def get_media_salientes(self):
        if self.tiempo_llamada_saliente:
            media_salientes = 0
            if self.tiempo_llamada_saliente > 0:
                media_salientes = self.tiempo_llamada_saliente /\
                    self._cantidad_llamadas_saliente
            return media_salientes
        return 0
