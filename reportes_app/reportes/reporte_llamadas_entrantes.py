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

from django.utils.encoding import force_text
from django.utils.timezone import now
from django.db.models import Count

from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import CalificacionCliente, Campana, OpcionCalificacion
# from ominicontacto_app.services.asterisk.redis_database import AbstractRedisFamily
# TODO: Una vez que AbstractRedisFamily ya se encuentre en el modulo redis_database borrar estos
# imports y la clase AbstractRedisFamily de este archivo
from django.utils.translation import ugettext as _
from django.conf import settings
import redis
from redis.exceptions import RedisError
import logging as _logging
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


class ReporteDeLLamadasEntrantesDeSupervision(object):
    INICIALES = {
        'llamadas_atendidas': 0,
        'llamadas_abandonadas': 0,
        'llamadas_expiradas': 0,
        'tiempo_acumulado_abandonadas': 0,
        'tiempo_acumulado_espera': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'EXITWITHTIMEOUT', 'ABANDON',
                       'ABANDONWEL']

    def __init__(self):
        query_campanas = Campana.objects.obtener_actuales().filter(type=Campana.TYPE_ENTRANTE)
        self.campanas = {}
        for campana in query_campanas:
            self.campanas[campana.id] = campana

        hoy = now()
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)
        self.estadisticas = {}
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()

    def _contabilizar_estadisticas_de_llamadas(self):
        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(estadisticas_campana, log)

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA,
                                         tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE)

    def _inicializar_conteo_de_campana(self, campana):
        datos_campana = self.INICIALES.copy()
        datos_campana['nombre'] = force_text(campana.nombre)
        self.estadisticas[campana.id] = datos_campana

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'CONNECT':
            datos_campana['llamadas_atendidas'] += 1
            datos_campana['tiempo_acumulado_espera'] += log.bridge_wait_time
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['llamadas_expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['llamadas_abandonadas'] += 1
            datos_campana['tiempo_acumulado_abandonadas'] += log.bridge_wait_time
        elif log.event == 'ABANDONWEL':
            datos_campana['llamadas_abandonadas'] += 1
            datos_campana['tiempo_acumulado_abandonadas'] += log.bridge_wait_time

    def _contabilizar_gestiones(self):
        # Contabilizo las gestiones
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gte=self.desde,
            fecha__lte=self.hasta,
            opcion_calificacion__campana_id__in=self.campanas.keys(),
            opcion_calificacion__tipo=OpcionCalificacion.GESTION
        ).values('opcion_calificacion__campana_id').annotate(
            cantidad=Count('opcion_calificacion__campana_id')).order_by()

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            self.estadisticas[campana_id]['gestiones'] = cantidad['cantidad']


class ReporteLlamadasEntranteFamily(AbstractRedisFamily):

    def _create_dict(self, family_member):
        return family_member[1]

    def _obtener_todos(self):
        reporte = ReporteDeLLamadasEntrantesDeSupervision()
        return [(campana_id, datos) for campana_id, datos in reporte.estadisticas.items()]

    def _get_nombre_family(self, family_member):
        return "{0}:{1}".format(self.get_nombre_families(), family_member[0])

    def get_nombre_families(self):
        return "OML:SUPERVISION_CAMPAIGN"

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    def regenerar_family(self, family_member):
        """regenera una family"""
        self.delete_family(family_member)
        self._create_family(family_member)
