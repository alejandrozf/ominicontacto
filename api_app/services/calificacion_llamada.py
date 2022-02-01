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

from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification_app.consumers import AgentConsole

import logging as _logging
import redis

from redis.exceptions import RedisError
logger = _logging.getLogger(__name__)


class CalificacionLLamada(object):
    def get_redis_connection(self):
        self.redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        return self.redis_connection

    def _get_nombre_family(self, agente):
        return "OML:CALIFICACION:LLAMADA:{0}".format(agente.id)

    def get_nombre_family(self):
        return "OML:CALIFICACION:LLAMADA"

    def create_family(self, agente, call_data, json_calldata, calificado, gestion, id_calificacion):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(agente)
        if calificado is True:
            llamada_calificada = 'TRUE'
        else:
            llamada_calificada = 'FALSE'
        if gestion is True:
            formulario_gestion = 'TRUE'
        else:
            formulario_gestion = 'FALSE'
        if id_calificacion is None:
            id_calificacion = 'NONE'
        if json_calldata is None:
            json_calldata = 'None'

        variables = {
            'NAME': agente.user.get_full_name(),
            'ID': agente.id,
            'CALLID': call_data['call_id'],
            'CAMPANA': call_data['id_campana'],
            'TELEFONO': call_data['telefono'],
            'CALIFICADA': llamada_calificada,
            'CALLDATA': json_calldata,
            'GESTION': formulario_gestion,
            'IDCALIFICACION': id_calificacion,
        }

        if agente.forzar_despausa():
            async_to_sync(get_channel_layer().group_send)(
                AgentConsole.GROUP_USER_OBJ.format(user_id=agente.user_id), {
                    "type": "broadcast",
                    "payload": {
                        "type": "unpause-call",
                        "args": {
                            "id": call_data['call_id'],
                            "calificada": llamada_calificada == 'TRUE'
                        }
                    }
                })
        try:
            redis_connection.hset(family, mapping=variables)
            ttl = 3600 * 24 * 4  # En 4 dias expira el hash
            redis_connection.expire(family, ttl)
        except (RedisError) as e:
            raise e

    def get_value(self, agente, key):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(agente)
        try:
            value = redis_connection.hget(family, key)
            return value
        except (RedisError) as e:
            raise e

    def get_family(self, agente):
        # Todo: Poner nombre más declarativo para un servicio
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(agente)
        try:
            value = redis_connection.hgetall(family)
            return value
        except (RedisError) as e:
            raise e
