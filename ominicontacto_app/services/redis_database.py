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
from django.utils.translation import ugettext as _

from ominicontacto_app.models import AgenteProfile

import logging as _logging
import redis
from redis.exceptions import RedisError

logger = _logging.getLogger(__name__)


class AgenteFamily(object):
    def _create_dict(self, agente):
        dict_agente = {
            'NAME': agente.user.get_full_name(),
            'SIP': agente.sip_extension,
            'STATUS': ""
        }
        return dict_agente

    def _obtener_todos(self):
        """Obtengo todos los agentes activos"""
        return AgenteProfile.objects.obtener_activos()

    def _get_nombre_family(self, agente):
        return "OML/AGENT/{0}".format(agente.id)

    def get_nombre_families(self):
        return "OML/AGENT"

    def _obtener_una_key(self):
        return "NAME"

    def get_redis_connection(self):
        self.redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        return self.redis_connection

    def _create_family(self, family_member):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(family_member).replace('/', ':')
        logger.info(_("Creando familys para la family  {0}".format(family)))
        variables = self._create_dict(family_member)
        try:
            redis_crea_family = redis_connection.hset(family, mapping=variables)
            return redis_crea_family
        except (RedisError) as e:
            raise e

    def _create_families(self):
        agentes = self._obtener_todos()
        for agente in agentes:
            self._create_family(agente)

    def delete_family(self, family_member):
        redis_connection = self.get_redis_connection()
        try:
            family = self._get_nombre_family(family_member).replace('/', ':')
            variables = redis_connection.hgetall(family)
            if variables != {}:
                redis_connection.hdel(family, *variables)
        except (RedisError) as e:
            raise e

    def _delete_tree_family(self, nombre_families):
        agentes = self._obtener_todos()
        redis_connection = self.get_redis_connection()
        try:
            for agente in agentes:
                family = (nombre_families + '/{0}'.format(agente.id)).replace('/', ':')
                variables = redis_connection.hgetall(family)
                if variables != {}:
                    redis_connection.hdel(family, *variables)
        except (RedisError) as e:
            raise e

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family(self.get_nombre_families())
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
