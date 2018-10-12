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

"""
Servicio para generar reporte grafico de un agente en particular para una campana
"""

import datetime
import logging as _logging

import pygal
from pygal.style import Style

from django.db.models import Count, Q
from django.utils.translation import ugettext as _
from django.utils import timezone

from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import CalificacionCliente, Campana
from reportes_app.actividad_agente_log import AgenteTiemposReporte
from reportes_app.models import LlamadaLog, ActividadAgenteLog

from utiles_globales import obtener_cantidad_no_calificados

logger = _logging.getLogger(__name__)


ESTILO_AZUL_ROJO_AMARILLO = Style(
    background='transparent',
    plot_background='transparent',
    foreground='#555',
    foreground_light='#555',
    foreground_dark='#555',
    opacity='1',
    opacity_hover='.6',
    transition='400ms ease-in',
    colors=('#428bca', '#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f',
            '#a95cb8', '#5cb8b5', '#caca43', '#96ac43', '#ca43ca')
)


class EstadisticasAgenteService():

    def _obtener_cantidad_no_calificados_agente(self, campana, fecha_desde, fecha_hasta,
                                                total_calificados, agente):
        """
        Devuelve la cantidad de llamadas recibidas por agentes pero no calificadas por estos
        """
        """
        Devuelve la cantidad de llamadas recibidas por agentes pero no calificadas por estos.
        Manual y Preview contar logs con ANSWER
        Dialer y Entrante contar logs con CONNECT
        """
        total_llamadas_campanas_qs = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk,
            agente_id=agente.pk).filter(
                Q(event='ANSWER', tipo_campana__in=[Campana.TYPE_MANUAL, Campana.TYPE_PREVIEW]) |
                Q(event='ANSWER', tipo_campana__in=[Campana.TYPE_DIALER, Campana.TYPE_ENTRANTE],
                  tipo_llamada=LlamadaLog.LLAMADA_MANUAL) |
                Q(event='CONNECT'))
        return obtener_cantidad_no_calificados(
            total_llamadas_campanas_qs, fecha_desde, fecha_hasta, campana)

    def obtener_cantidad_calificacion(self, campana, fecha_desde, fecha_hasta, agente):
        """
        Obtiene el total por calificacipn para el agente por la campana
        :param campana: campana las cual se obtendran las calificaciones
        :param fecha_desde: fecha/hora desde la cual se obtendran las calificaciones
        :param fecha_hasta: fecha/hora hasta la cual se obtendran las calificaciones
        :param agente: agente el cual se evaluara
        :return: retorna el nombre y cantidades de la calificaiones y el total de
        calificaciones
        """
        calificaciones_query = CalificacionCliente.objects.filter(
            agente=agente, opcion_calificacion__campana=campana, fecha__range=(
                fecha_desde, fecha_hasta))
        calificaciones_agrupadas_qs = calificaciones_query.values(
            'opcion_calificacion__nombre').annotate(cantidad=Count('opcion_calificacion__nombre'))
        calificaciones_nombre = []
        calificaciones_cantidad = []
        total_calificados = 0
        for calificacion_data in calificaciones_agrupadas_qs:
            cantidad = calificacion_data['cantidad']
            calificaciones_nombre.append(calificacion_data['opcion_calificacion__nombre'])
            calificaciones_cantidad.append(cantidad)
            total_calificados += cantidad
        total_no_calificados = self._obtener_cantidad_no_calificados_agente(
            campana, fecha_desde, fecha_hasta, total_calificados, agente)
        calificaciones_nombre.append(_("Llamadas Atendidas sin calificacion"))
        calificaciones_cantidad.append(total_no_calificados)
        total_asignados = total_calificados + total_no_calificados
        return calificaciones_nombre, calificaciones_cantidad, total_asignados

    def _obtener_actividad_agente(self, logs_actividad_agente):
        tiempo_sesion, tiempo_pausa = (datetime.timedelta(), datetime.timedelta())
        tiempo_actual_sesion, tiempo_actual_pausa = (None, None)
        evento_anterior = None
        for log_actividad_agente in logs_actividad_agente:
            # se calculan los tiempos de sesión del agente
            evento = log_actividad_agente.event
            tiempo_log = log_actividad_agente.time
            inicio_dia = tiempo_log.replace(hour=0, minute=0, second=0, microsecond=0)
            if evento == 'REMOVEMEMBER' and tiempo_actual_sesion is None:
                # el agente inicio sesión el día anterior, sumamos el tiempo desde el inicio del día
                tiempo_sesion += tiempo_log - inicio_dia
            elif evento == 'REMOVEMEMBER' and tiempo_actual_sesion is not None:
                # se cierra la sesión de un agente que estuvo conectado previamente
                tiempo_sesion += tiempo_log - tiempo_actual_sesion
                tiempo_actual_sesion = None
            elif (evento == 'ADDMEMBER' and tiempo_actual_sesion is None and
                  evento_anterior != 'UNPAUSEALL'):
                tiempo_actual_sesion = tiempo_log
            elif (evento == 'ADDMEMBER' and tiempo_actual_sesion is None and
                  evento_anterior == 'UNPAUSEALL'):
                tiempo_actual_sesion = tiempo_log
                # reiniciamos el tiempo que se generó de pausa desde el inicio del día pues no es
                # un evento de día anterior sino que se genera antes de loguearse el agente
                tiempo_pausa = datetime.timedelta()
            # se calculan los tiempos de pausa del agente
            if evento == 'UNPAUSEALL' and evento_anterior is None:
                # al parecer el agente estaba en pausa desde el día anterior, sumamos el tiempo
                # desde el inicio del día
                tiempo_pausa += tiempo_log - inicio_dia
            elif evento == 'UNPAUSEALL' and tiempo_actual_pausa is not None:
                # se cierra la pausa de un agente que estuvo pausado previamente
                tiempo_pausa += tiempo_log - tiempo_actual_pausa
                tiempo_actual_pausa = None
            elif evento == 'PAUSEALL':
                # comienza una pausa del agente se marca el tiempo en que comienza
                tiempo_actual_pausa = tiempo_log
            evento_anterior = evento
        if tiempo_actual_sesion is not None:
            # el agente no terminó su sesión en el día, sumamos el tiempo hasta el final del día
            final_dia = tiempo_log.replace(hour=23, minute=59, second=59, microsecond=999999)
            tiempo_sesion += final_dia - tiempo_actual_sesion
        if tiempo_actual_pausa is not None:
            final_dia = tiempo_log.replace(hour=23, minute=59, second=59, microsecond=999999)
            # el agente no terminó su pausa en el día, sumamos el tiempo hasta el final del día
            tiempo_pausa += final_dia - tiempo_actual_pausa
        return tiempo_sesion, tiempo_pausa

    def _obtener_estadisticas_llamadas_agente(self, logs_llamadas_agente):
        tiempo_en_llamada = 0
        tiempo_en_llamada_manual = 0
        cantidad_llamadas_procesadas = 0
        cantidad_llamadas_perdidas = 0
        cantidad_llamadas_manuales = 0
        for log_llamada_agente in logs_llamadas_agente:
            evento = log_llamada_agente.event
            duracion_llamada = log_llamada_agente.duracion_llamada
            es_llamada_manual = (log_llamada_agente.tipo_llamada == LlamadaLog.LLAMADA_MANUAL)
            if evento in LlamadaLog.EVENTOS_FIN_CONEXION:
                tiempo_en_llamada += duracion_llamada
                if es_llamada_manual:
                    tiempo_en_llamada_manual += duracion_llamada
            elif evento in ['ANSWER', 'CONNECT']:
                cantidad_llamadas_procesadas += 1
                if es_llamada_manual:
                    cantidad_llamadas_manuales += 1
            elif evento in LlamadaLog.EVENTOS_NO_CONEXION:
                cantidad_llamadas_perdidas += 1
        return (tiempo_en_llamada, tiempo_en_llamada_manual, cantidad_llamadas_procesadas,
                cantidad_llamadas_perdidas, cantidad_llamadas_manuales)

    def calcular_tiempo_agente(self, agente, fecha_desde, fecha_hasta, campana):
        ahora = timezone.now()
        if fecha_hasta.date() == ahora.date():
            # estamos calculando hasta el día actual
            fecha_hasta = ahora
        logs_actividad_agente = ActividadAgenteLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta)).order_by('time')
        logs_llamadas_agente = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk, agente_id=agente.pk)
        tiempo_sesion, tiempo_pausa = self._obtener_actividad_agente(logs_actividad_agente)
        (tiempo_en_llamada, tiempo_en_llamada_manual, cantidad_llamadas_procesadas,
         cantidad_llamadas_perdidas,
         cantidad_llamadas_manuales) = self._obtener_estadisticas_llamadas_agente(
             logs_llamadas_agente)
        # los valores de las variables 'tiempo_en_llamada_manual' y 'cantidad_llamadas_manuales'
        # y las estadísticas que a partir de estos se generan no son relevantes en los reportes
        # actualmente, se mantiene su cálculo previendo su uso a futuro
        agente_tiempos = AgenteTiemposReporte(
            agente, tiempo_sesion, tiempo_pausa, tiempo_en_llamada, cantidad_llamadas_procesadas,
            cantidad_llamadas_perdidas, tiempo_en_llamada_manual, cantidad_llamadas_manuales)
        return agente_tiempos

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta, agente):
        fecha_desde = datetime_hora_minima_dia(fecha_desde)
        fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde, fecha_hasta, agente)

        agente_tiempo = self.calcular_tiempo_agente(agente, fecha_desde, fecha_hasta, campana)

        dic_estadisticas = {
            'total_asignados': total_asignados,
            'calificaciones_nombre': calificaciones_nombre,
            'calificaciones_cantidad': calificaciones_cantidad,
            'agente_tiempo': agente_tiempo
        }
        return dic_estadisticas

    def general_campana(self, agente, campana, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(campana, fecha_inferior,
                                                   fecha_superior, agente)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")

        # Barra: Cantidad de calificacion de cliente
        barra_campana_calificacion = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_calificacion.title = 'Cantidad de calificacion de cliente '

        barra_campana_calificacion.x_labels = \
            estadisticas['calificaciones_nombre']
        barra_campana_calificacion.add('cantidad',
                                       estadisticas['calificaciones_cantidad'])

        return {
            'estadisticas': estadisticas,
            'barra_campana_calificacion': barra_campana_calificacion,
            'total_asignados': estadisticas['total_asignados'],
            'dict_campana_counter': zip(estadisticas['calificaciones_nombre'],
                                        estadisticas['calificaciones_cantidad']),
        }
