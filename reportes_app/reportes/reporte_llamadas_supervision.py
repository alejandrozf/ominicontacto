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
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.db.models import Count

from ominicontacto_app.models import Campana, OpcionCalificacion, CalificacionCliente
from reportes_app.models import LlamadaLog
from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia

INICIALES = {
    'recibidas': 0,
    'atendidas': 0,
    'expiradas': 0,
    'abandonadas': 0,
    'gestiones': 0,     # Contactos gestionados? Respuestas de formulario del dia?
}

EVENTOS_LLAMADA = ['ENTERQUEUE', 'ENTERQUEUE-TRANSFER', 'CONNECT', 'EXITWITHTIMEOUT', 'ABANDON']


class ReporteDeLLamadasEntrantesDeSupervision(object):
    def __init__(self, user_supervisor):
        campanas = self._obtener_campanas(user_supervisor)
        self.campanas_ids = list(campanas.values_list('id', flat=True))

        hoy = now().date()
        self.desde = datetime_hora_minima_dia(hoy)
        self.hasta = datetime_hora_maxima_dia(hoy)

        self.estadisticas = {}
        self._inicializar_conteo_de_estadisticas(campanas)
        self._contabilizar_estadisticas_de_llamadas()
        self._contabilizar_gestiones()

    def _obtener_campanas(self, user_supervisor):
        campanas = Campana.objects.obtener_all_activas_finalizadas()
        campanas = campanas.filter(type=Campana.TYPE_ENTRANTE)
        if not user_supervisor.get_is_administrador():
            return Campana.objects.obtener_campanas_vista_by_user(campanas, user_supervisor)
        else:
            return campanas

    def _inicializar_conteo_de_estadisticas(self, campanas):
        for campana in campanas:
            datos_campana = INICIALES.copy()
            datos_campana['nombre'] = force_text(campana.nombre)
            self.estadisticas[campana.id] = datos_campana

    def _contabilizar_estadisticas_de_llamadas(self):
        # Contabilizo las llamadas
        logs = LlamadaLog.objects.filter(time__gte=self.desde,
                                         time__lte=self.hasta,
                                         campana_id__in=self.campanas_ids,
                                         event__in=EVENTOS_LLAMADA,
                                         tipo_llamada=LlamadaLog.LLAMADA_ENTRANTE)
        for log in logs:
            estadisticas_campana = self.estadisticas[log.campana_id]
            self._contabilizar_tipos_de_llamada_por_campana_entrante(estadisticas_campana, log)

    def _contabilizar_gestiones(self):
        # Contabilizo las gestiones
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gte=self.desde,
            fecha__lte=self.hasta,
            opcion_calificacion__campana_id__in=self.campanas_ids,
            opcion_calificacion__tipo=OpcionCalificacion.GESTION
        ).values('opcion_calificacion__campana_id').annotate(
            cantidad=Count('opcion_calificacion__campana_id'))

        for cantidad in calificaciones:
            campana_id = cantidad['opcion_calificacion__campana_id']
            self.estadisticas[campana_id]['gestiones'] = cantidad['cantidad']

    def _contabilizar_tipos_de_llamada_por_campana_entrante(self, datos_campana, log):
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
