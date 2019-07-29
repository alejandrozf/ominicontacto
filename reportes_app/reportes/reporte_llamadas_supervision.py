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

from datetime import datetime

from django.utils.encoding import force_text
from django.db.models import Count

from ominicontacto_app.models import Campana, OpcionCalificacion, CalificacionCliente
from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia


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
            cantidad=Count('opcion_calificacion__campana_id'))

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            if campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[campana_id])
            self.estadisticas[campana_id]['gestiones'] = cantidad['cantidad']

    def _contabilizar_estadisticas_de_llamadas(self):
        logs = self._obtener_logs_de_llamadas()
        for log in logs:
            if log.campana_id not in self.estadisticas:
                self._inicializar_conteo_de_campana(self.campanas[log.campana_id])
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana(estadisticas_campana, log)

    @property
    def INICIALES(self):
        raise NotImplementedError

    def _obtener_campanas(user_supervisor):
        raise NotImplementedError

    def _obtener_logs_de_llamadas(self):
        raise NotImplementedError

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        raise NotImplementedError


class ReporteDeLLamadasEntrantesDeSupervision(ReporteDeLlamadasDeSupervision):
    INICIALES = {
        'recibidas': 0,
        'atendidas': 0,
        'expiradas': 0,
        'abandonadas': 0,
        'abandonadas_anuncio': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'EXITWITHTIMEOUT', 'ABANDON',
                       'ABANDONWEL']

    def _obtener_campanas(self, user_supervisor):
        campanas = Campana.objects.obtener_all_activas_finalizadas()
        campanas = campanas.filter(type=Campana.TYPE_ENTRANTE)
        if not user_supervisor.get_is_administrador():
            return Campana.objects.obtener_campanas_vista_by_user(campanas, user_supervisor)
        else:
            return campanas

    def _obtener_logs_de_llamadas(self):
        return LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas.keys(),
                                         event__in=self.EVENTOS_LLAMADA,
                                         tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE)

    def _contabilizar_tipos_de_llamada_por_campana(self, datos_campana, log):
        if log.event == 'ENTERQUEUE':
            datos_campana['recibidas'] += 1
        elif log.event == 'ENTERQUEUE-TRANSFER':
            datos_campana['recibidas'] += 1
        elif log.event == 'CONNECT':
            datos_campana['atendidas'] += 1
        elif log.event == 'EXITWITHTIMEOUT':
            datos_campana['expiradas'] += 1
        elif log.event == 'ABANDON':
            datos_campana['abandonadas'] += 1
        elif log.event == 'ABANDONWEL':
            datos_campana['abandonadas_anuncio'] += 1
            datos_campana['recibidas'] += 1


class ReporteDeLLamadasSalientesDeSupervision(ReporteDeLlamadasDeSupervision):
    INICIALES = {
        'efectuadas': 0,
        'conectadas': 0,
        'no_conectadas': 0,
        'gestiones': 0,
    }
    EVENTOS_LLAMADA = ('DIAL', 'CONNECT', 'ANSWER') + LlamadaLog.EVENTOS_NO_CONEXION

    def _obtener_campanas(self, user_supervisor):
        campanas = Campana.objects.obtener_all_activas_finalizadas()
        campanas = campanas.filter(type__in=[Campana.TYPE_DIALER,
                                             Campana.TYPE_PREVIEW,
                                             Campana.TYPE_MANUAL])
        if not user_supervisor.get_is_administrador():
            return Campana.objects.obtener_campanas_vista_by_user(campanas, user_supervisor)
        else:
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
