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
#

import logging as _logging
from ominicontacto_app.services.redis.connection import create_redis_connection

from django.utils.timezone import now, localtime
from django.db.models import Count

from ominicontacto_app.utiles import datetime_hora_minima_dia
from ominicontacto_app.models import Campana
from reportes_app.models import LlamadaLog

logger = _logging.getLogger(__name__)


class CallDataGenerator(object):
    """  Regenera en Redis estadisticas de llamadas del día actual
         Las Estadísticas se usarán para efectuar cálculos más eficiente sin acceder a psql
    """
    # Keys de los valores en Redis a regenerar
    CAMP_KEY = 'OML:CALLDATA:CAMP:'
    WAIT_TIME_KEY = 'OML:CALLDATA:WAIT-TIME:CAMP:'
    AGENT_KEY = 'OML:CALLDATA:AGENT:'
    SLA_KEY = 'OML:CALLDATA:SLA:CAMP:'

    EVENTOS_FIN_CONEXION_ORIGINAL = [
        'COMPLETEAGENT', 'COMPLETEOUTNUM', 'BT-TRY', 'BTOUT-TRY',
        'CAMPT-COMPLETE', 'CAMPT-FAIL', 'COMPLETE-CAMPT', 'CT-COMPLETE', 'CTOUT-COMPLETE'
    ]

    def __init__(self, redis_connection=None) -> None:
        self.redis_connection = redis_connection
        self._desde = None

    def get_redis_connection(self):
        if not self.redis_connection:
            self.redis_connection = create_redis_connection()
        return self.redis_connection

    def get_camp_key(self, campana_id, event):
        return '{0}{1}:{2}'.format(self.CAMP_KEY, campana_id, event)

    def get_wait_time_key(self, campana_id):
        return '{0}{1}'.format(self.WAIT_TIME_KEY, campana_id)

    def get_agent_key(self, agente_id, event):
        return '{0}{1}:{2}'.format(self.AGENT_KEY, agente_id, event)

    def get_sla_key(self, campana_id):
        return '{0}{1}'.format(self.SLA_KEY, campana_id)

    def eliminar_datos(self):
        base_keys = [self.CAMP_KEY, self.WAIT_TIME_KEY, self.AGENT_KEY, self.SLA_KEY]
        for base_key in base_keys:
            keys = self.redis_connection.keys(base_key + '*')
            if keys:
                self.redis_connection.delete(*keys)

    def regenerar(self):
        self.get_redis_connection()
        self.eliminar_datos()

        self.regenerar_eventos_por_campaña()
        self.regenerar_eventos_por_agente()
        self.regenerar_wait_times_y_sla()

    @property
    def desde(self):
        if self._desde is None:
            hoy = localtime(now())
            self._desde = datetime_hora_minima_dia(hoy)
        return self._desde

    def regenerar_eventos_por_campaña(self):
        """ Cantidad de ocurrencias de eventos "relevantes" en LlamadaLog para cada campaña """
        columna = 'campana_id'
        # TODO: Filtrar eventos "relevantes únicamente"
        cantidades = LlamadaLog.objects.filter(time__gt=self.desde).values(columna, 'event')\
            .annotate(cantidad=Count(columna)).order_by(columna)
        for cantidad in cantidades:
            key = self.get_camp_key(cantidad[columna], cantidad['event'])
            self.redis_connection.set(key, cantidad['cantidad'])

    def regenerar_eventos_por_agente(self):
        """ Cantidad de ocurrencias de eventos "relevantes" en LlamadLog para cada agente """
        columna = 'agente_id'
        # TODO: Filtrar eventos "relevantes únicamente"
        cantidades = LlamadaLog.objects.filter(time__gt=self.desde).values(columna, 'event')\
            .annotate(cantidad=Count(columna)).order_by(columna)
        for cantidad in cantidades:
            key = self.get_agent_key(cantidad[columna], cantidad['event'])
            self.redis_connection.set(key, cantidad['cantidad'])

    def regenerar_wait_times_y_sla(self):
        wait_times_por_campana = {}
        self._regenerar_wait_time(wait_times_por_campana)
        self._regenerar_sla(wait_times_por_campana)

    def _regenerar_wait_time(self, wait_times_por_campana):
        llamadas = LlamadaLog.objects.using('replica')\
            .filter(time__gt=self.desde,
                    event__in=self.EVENTOS_FIN_CONEXION_ORIGINAL)\
            .exclude(agente_id=-1)
        for log in llamadas:
            if log.campana_id not in wait_times_por_campana:
                wait_times_por_campana[log.campana_id] = []
            wait_times_por_campana[log.campana_id].append(log.bridge_wait_time)

        for campana_id, wait_times in wait_times_por_campana.items():
            key = self.get_wait_time_key(campana_id)
            self.redis_connection.sadd(key, *wait_times)

    def _regenerar_sla(self, wait_times_por_campana):
        sla_por_campana = dict(Campana.objects.filter(id__in=wait_times_por_campana.keys())
                               .values_list('id', 'queue_campana__servicelevel'))
        for campana_id, sla in sla_por_campana.items():
            sla_data = self._calcular_sla(sla, wait_times_por_campana[campana_id])
            key = self.get_sla_key(campana_id)
            self.redis_connection.hset(key, mapping=sla_data)

    def _calcular_sla(self, sla, wait_times):
        total = len(wait_times)
        ok = sum(1 for x in wait_times if x <= sla)
        return {
            'OK': ok,
            'BAD': total - ok,
            'SUM': sum(wait_times),
            'MAX': max(wait_times),
        }
