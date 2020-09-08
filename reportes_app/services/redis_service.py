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
from __future__ import unicode_literals

import redis
from django.conf import settings


class RedisService(object):
    def __init__(self) -> None:
        self.redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME, port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)

    def obtener_estadisticas_campanas_entrantes(self, campanas_id_list) -> dict:
        estadisticas = {}
        campanas_keys = self._obtener_lista_keys("OML:SUPERVISION_CAMPAIGN:*")
        for campana_r in campanas_keys:
            estadisticas.update(self._obtener_estadisticas_campana(campana_r))
        return estadisticas

    def _obtener_lista_keys(self, pattern) -> list:
        return self.redis_connection.keys(pattern)

    def _obtener_estadisticas_campana(self, redis_key) -> dict:
        estadistica_campana = {}
        campana_info = self.redis_connection.hgetall(redis_key)
        campana_id = int(redis_key.split(':')[-1])
        atendidas = campana_info.get('llamadas_atendidas', 0)
        abandonadas = campana_info.get('llamadas_abandonadas', 0)
        expiradas = campana_info.get('llamadas_expiradas', 0)
        gestiones = campana_info.get('numero_gestiones', 0)
        llamadas_en_espera = campana_info.get('llamadas_en_espera', 0)
        t_promedio_abandono = float(campana_info.get('tiempo_acumulado_abandonadas', 0))
        t_promedio_espera = float(campana_info.get('tiempo_acumulado_espera', 0))

        if atendidas != 0 or abandonadas != 0 or expiradas != 0 or llamadas_en_espera != 0 \
                or gestiones != 0 or t_promedio_abandono != 0 or t_promedio_espera != 0:

            estadistica_campana[campana_id] = {}
            estadistica_campana[campana_id]['atendidas'] = atendidas
            estadistica_campana[campana_id]['abandonadas'] = abandonadas
            estadistica_campana[campana_id]['expiradas'] = expiradas
            estadistica_campana[campana_id]['gestiones'] = gestiones
            estadistica_campana[campana_id]['llamadas_en_espera'] = llamadas_en_espera
            estadistica_campana[campana_id]['t_promedio_abandono'] = t_promedio_abandono
            estadistica_campana[campana_id]['t_promedio_espera'] = t_promedio_espera

        return estadistica_campana
