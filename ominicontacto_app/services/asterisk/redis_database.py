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


class AbstractRedisFamily(object):
    redis_connection = None

    def get_redis_connection(self):
        if not self.redis_connection:
            self.redis_connection = redis.Redis(
                host=settings.REDIS_HOSTNAME,
                port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                decode_responses=True)
        return self.redis_connection

    def _create_family(self, family_member):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(family_member)
        variables = self._create_dict(family_member)
        try:
            redis_crea_family = redis_connection.hset(family, mapping=variables)
            return redis_crea_family
        except (RedisError) as e:
            raise e

    def _create_families(self, modelo=None, modelos=None):
        """ Crea familys en Redis """
        if modelos:
            pass
        elif modelo:
            modelos = [modelo]
        else:
            modelos = self._obtener_todos()

        for familia_member in modelos:
            self._create_family(familia_member)

    def delete_family(self, family_member):
        redis_connection = self.get_redis_connection()
        try:
            family = self._get_nombre_family(family_member)
            redis_connection.delete(family)
        except (RedisError) as e:
            raise e

    def _delete_tree_family(self):
        """Elimina todos los objetos de la family """

        nombre_families = self.get_nombre_families() + ':*'
        finalizado = False
        index = 0
        while not finalizado:
            redis_connection = self.get_redis_connection()
            try:
                result = redis_connection.scan(index, nombre_families)
                index = result[0]
                keys = result[1]
                for key in keys:
                    redis_connection.delete(key)
                if index == 0:
                    finalizado = True
            except RedisError as e:
                logger.exception(_("Error al intentar Eliminar families de {0}. Error: {1}".format(
                    nombre_families, e)))

    def _create_dict(self, family_member):
        raise (NotImplementedError())

    def _obtener_todos(self):
        raise (NotImplementedError())

    def _get_nombre_family(self, family_member):
        raise (NotImplementedError())

    def get_nombre_families(self):
        raise (NotImplementedError())

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)


class AgenteFamily(AbstractRedisFamily):

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
        return "{0}:{1}".format(self.get_nombre_families(), agente.id)

    def get_nombre_families(self):
        return "OML:AGENT"
