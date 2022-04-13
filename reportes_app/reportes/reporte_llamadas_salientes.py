
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
from redis.exceptions import RedisError
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from django.utils.timezone import now, localtime
from django.db.models import Count
import json

from ominicontacto_app.services.asterisk.redis_database import AbstractRedisFamily
from ominicontacto_app.models import CalificacionCliente, Campana, OpcionCalificacion
from reportes_app.models import LlamadaLog


class ReporteDeLLamadasSalientesDeSupervision(object):
    INICIALES = {
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        'gestiones': 0,
        'porcentaje_objetivo': 0,
    }
    EVENTOS_LLAMADA = ('DIAL', 'ANSWER') + LlamadaLog.EVENTOS_NO_CONEXION

    def __init__(self):
        query_campanas = Campana.objects.obtener_all_dialplan_asterisk().filter(
            type__in=[Campana.TYPE_PREVIEW, Campana.TYPE_MANUAL])
        self.campanas = {}
        for campana in query_campanas:
            self.campanas[campana.id] = campana
        hoy = localtime(now())
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)
        self.estadisticas = {}
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()
        self._calcular_porcentaje_objetivo()

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.using('replica')\
            .filter(time__gte=self.desde,
                    time__lte=self.hasta,
                    campana_id__in=self.campanas.keys(),
                    event__in=self.EVENTOS_LLAMADA)

    def _inicializar_conteo_de_campana(self, campana):
        datos_campana = self.INICIALES.copy()
        datos_campana['nombre'] = force_text(campana.nombre)
        self.estadisticas[campana.id] = datos_campana

    def _contabilizar_gestiones(self):
        # Contabilizo las gestiones
        calificaciones = CalificacionCliente.objects.using('replica').filter(
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

    def _calcular_porcentaje_objetivo(self):
        # Contabilizo el porcentaje alcanzado del objetivo
        calificaciones = CalificacionCliente.objects.using('replica').filter(
            opcion_calificacion__campana_id__in=self.campanas.keys(),
            opcion_calificacion__positiva=True
        ).values('opcion_calificacion__campana_id').annotate(
            cantidad=Count('opcion_calificacion__campana_id')).order_by()

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            if self.campanas[campana_id].objetivo == 0:
                self.estadisticas[campana_id]['porcentaje_objetivo'] = 0
            else:
                porcentaje_objetivo = cantidad['cantidad'] / self.campanas[campana_id].objetivo
                self.estadisticas[campana_id]['porcentaje_objetivo'] = "{:.1%}".format(
                    porcentaje_objetivo)

    def _contabilizar_estadisticas_de_llamadas(self):

        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(
                    self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(
                estadisticas_campana, log)

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):

        if log.event == 'DIAL':
            datos_campana['efectuadas'] += 1

        elif log.event in LlamadaLog.EVENTOS_NO_CONEXION:
            datos_campana['no_conectadas'] += 1
        # Si es MANUAL o PREVIEW
        elif log.event == 'ANSWER':
            datos_campana['conectadas'] += 1


class ReporteLlamadasSalienteFamily(AbstractRedisFamily):

    def _create_dict(self, datos_saliente):
        dict_saliente = {
            'NOMBRE': datos_saliente['nombre'],
            'ESTADISTICAS': json.dumps(datos_saliente)
        }
        return dict_saliente

    def _create_family(self, campana_id, datos_saliente):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(campana_id)
        variables = self._create_dict(datos_saliente)
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
            campana_id = familia_member[0]
            self._create_family(campana_id, familia_member[1])

    def _obtener_todos(self):
        reporte = ReporteDeLLamadasSalientesDeSupervision()
        return [(campana_id, datos) for campana_id, datos in reporte.estadisticas.items()]

    def get_value(self, campana, key):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(campana.id)
        try:
            value = redis_connection.hget(family, key)
            return value
        except (RedisError) as e:
            raise e

    def _get_nombre_family(self, campana_id):
        return "{0}:{1}".format(self.get_nombre_families(), campana_id)

    def get_nombre_families(self):
        return "OML:SUPERVISION_SALIENTE"

    def get_family(self, campana):
        redis_connection = self.get_redis_connection()
        family = self._get_nombre_family(campana.id)
        try:
            value = redis_connection.hgetall(family)
            return value
        except (RedisError) as e:
            raise e

    def regenerar_families(self):
        """regenera la family"""
        self._delete_tree_family()
        self._create_families()

    # def regenerar_family(self, campana):
    # Necesitaria correr el reporte para regenerarla
    #     """regenera una family"""
    #     self.delete_family(campana.id)
    #     self._create_family(campana.id)
