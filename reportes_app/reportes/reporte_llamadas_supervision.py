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
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import CalificacionCliente, Campana, OpcionCalificacion

from reportes_app.models import LlamadaLog
from reportes_app.services.redis_service import RedisService

import logging as _logging

from datetime import datetime

from django.db.models import Count
from django.utils.encoding import force_text
from collections import defaultdict

logger = _logging.getLogger(__name__)


class ReporteDeLlamadasDeSupervision(object):
    def __init__(self, user_supervisor):
        query_campanas = self._obtener_campanas(user_supervisor)
        self.campanas = {}
        for campana in query_campanas:
            self.campanas[campana.id] = campana

        hoy = datetime.now()
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)

        self.estadisticas = {}
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()

    def _inicializar_conteo_de_campana(self, campana):
        datos_campana = self.INICIALES.copy()
        datos_campana['nombre'] = force_text(campana.nombre)
        self.estadisticas[campana.id] = datos_campana

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

    def _contabilizar_estadisticas_de_llamadas(self):
        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(
                    self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(
                estadisticas_campana, log)

    @property
    def INICIALES(self):
        raise NotImplementedError

    def _obtener_campanas(self, user_supervisor):
        raise NotImplementedError

    def _obtener_logs_de_llamadas(self):
        raise NotImplementedError

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        raise NotImplementedError


class ReporteDeLLamadasEntrantesDeSupervision(object):
    INICIALES = {
        'agentes_online': 0,
        'agentes_llamada': 0,
        'agentes_pausa': 0,
        'llamadas_en_espera': 0,
        'atendidas': 0,
        'abandonadas': 0,
        'expiradas': 0,
        't_promedio_abandono': 0,
        't_promedio_espera': 0,
        'gestiones': 0,
    }

    def __init__(self, user_supervisor):
        self.campanas = {campana.id: campana for campana in self._obtener_campanas(user_supervisor)}
        self.estadisticas = {}

        self._contabilizar_agentes()
        self._contabilizar_datos_campanas()

    def _inicializar_conteo_de_campana(self, campana_id):
        self.estadisticas.update({campana_id: self.INICIALES.copy()})
        self.estadisticas[campana_id]['nombre'] = force_text(self.campanas[campana_id].nombre)

    def _contabilizar_datos_campanas(self):
        redis_service = RedisService()
        estadisticas_redis = redis_service.obtener_estadisticas_campanas_entrantes(
            self.campanas.keys())
        for st in estadisticas_redis.keys():
            if not self.estadisticas.get(st, False):
                self._inicializar_conteo_de_campana(st)
            self.estadisticas[st].update(estadisticas_redis[st])

    def _obtener_campanas(self, user_supervisor):
        if user_supervisor.get_is_administrador():
            campanas = Campana.objects.obtener_actuales()
        else:
            supervisor = user_supervisor.get_supervisor_profile()
            campanas = supervisor.campanas_asignadas_actuales()

        campanas = campanas.filter(type=Campana.TYPE_ENTRANTE).order_by('id')
        return campanas

    def _contabilizar_agentes(self):
        agentes_activos_dict = {
            agente['id']: agente for agente in SupervisorActivityAmiManager()
            .obtener_agentes_activos()}
        # TODO: Revisar si es más eficiente usar el prefetch_related de campanas que obtener
        # tupla de (campana_id, agente_id) y construir agentes_activos_campana_id_dict
        agentes_activos_campana_id_dict = self._genera_agentes_activos_campana_dict(
            agentes_activos_dict.keys())
        for campana_id in agentes_activos_campana_id_dict.keys():
            self._contabiliza_agentes_campana(
                campana_id, agentes_activos_campana_id_dict[campana_id], agentes_activos_dict)

    def _contabiliza_agentes_campana(self, campana_id, lista_agentes_campana, agentes_activos):
        agentes_pausa = 0
        agentes_llamada = 0
        agentes_online = 0
        for agente in lista_agentes_campana:
            agente_status = agentes_activos[agente]['status']
            if str(agente_status).startswith("PAUSE"):
                agentes_pausa += 1
            elif str(agente_status).startswith("ONCALL"):
                agentes_llamada += 1
            if str(agente_status) != 'OFFLINE':
                agentes_online += 1
        if agentes_pausa != 0 or agentes_llamada != 0 or agentes_online != 0:
            if not self.estadisticas.get(campana_id, False):
                self._inicializar_conteo_de_campana(campana_id)
            self.estadisticas[campana_id]['agentes_online'] = agentes_online
            self.estadisticas[campana_id]['agentes_llamada'] = agentes_llamada
            self.estadisticas[campana_id]['agentes_pausa'] = agentes_pausa

    def _genera_agentes_activos_campana_dict(self, agentes_activos_list):
        tuplas = Campana.objects.filter(
            queue_campana__members__id__in=agentes_activos_list)\
            .filter(id__in=self.campanas.keys()).values_list('id', 'queue_campana__members__id')

        res = defaultdict(list)
        for campana_id, agente_id in tuplas:
            res[campana_id].append(agente_id)
        return res


class ReporteDeLLamadasSalientesDeSupervision(ReporteDeLlamadasDeSupervision):
    INICIALES = {
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ('DIAL', 'CONNECT', 'ANSWER') + \
        LlamadaLog.EVENTOS_NO_CONEXION

    def _obtener_campanas(self, user_supervisor):
        if user_supervisor.get_is_administrador():
            campanas = Campana.objects.obtener_actuales()
        else:
            supervisor = user_supervisor.get_supervisor_profile()
            campanas = supervisor.campanas_asignadas_actuales()

        campanas = campanas.filter(type__in=[Campana.TYPE_DIALER,
                                             Campana.TYPE_PREVIEW,
                                             Campana.TYPE_MANUAL])
        return campanas

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA)

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'DIAL':
            datos_campana['efectuadas'] += 1
        elif log.event in LlamadaLog.EVENTOS_NO_CONEXION:
            datos_campana['no_conectadas'] += 1
        # Si es DIALER:
        elif log.tipo_campana == Campana.TYPE_DIALER:
            # Si es CONNECT en DIALER
            if log.event == 'CONNECT':
                datos_campana['conectadas'] += 1
            elif log.event == 'ANSWER' and log.tipo_llamada == Campana.TYPE_MANUAL:
                datos_campana['conectadas'] += 1
        # Si es MANUAL o PREVIEW
        elif log.event == 'ANSWER':
            datos_campana['conectadas'] += 1
