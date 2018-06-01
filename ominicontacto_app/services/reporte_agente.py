# -*- coding: utf-8 -*-

"""
Servicio para generar reporte grafico de un agente en particular para una campana
"""

import datetime
import logging as _logging

import pygal
from pygal.style import Style

from django.db.models import Count
from django.utils.translation import ugettext as _
from django.utils import timezone

from ominicontacto_app.models import CalificacionCliente
from ominicontacto_app.services.queue_log_service import AgenteTiemposReporte
from reportes_app.models import LlamadaLog, ActividadAgenteLog

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
        total_llamadas_campanas_qs = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk,
            agente_id=agente.pk, event__in=['CONNECT', 'ANSWER'])
        total_llamadas_campanas = total_llamadas_campanas_qs.count()
        return total_llamadas_campanas - total_calificados

    def obtener_cantidad_calificacion(self, campana, fecha_desde, fecha_hasta, agente):
        """
        Obtiene el total por calificacipn para el agente por la campana
        :param campana: campana las cual se obtendran las calificaciones
        :param fecha_desde: fecha desde la cual se obtendran las calificaciones
        :param fecha_hasta: fecha hasta la cual se obtendran las calificaciones
        :param agente: agente el cual se evaluara
        :return: retorna el nombre y cantidades de la calificaiones y el total de
        calificaciones
        """
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
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
            elif evento == 'ADDMEMBER' and tiempo_actual_sesion is None:
                tiempo_actual_sesion = tiempo_log
            # se calculan los tiempos de pausa del agente
            if evento == 'UNPAUSEALL' and tiempo_actual_pausa is None:
                # el agente estaba en pausa desde el día anterior, sumamos el tiempo desde el
                # inicio del día
                tiempo_pausa += tiempo_log - inicio_dia
            elif evento == 'UNPAUSEALL' and tiempo_actual_pausa is not None:
                # se cierra la pausa de un agente que estuvo pausado previamente
                tiempo_pausa += tiempo_log - tiempo_actual_pausa
                tiempo_actual_pausa = None
            elif evento == 'PAUSEALL':
                # comienza una pausa del agente se marca el tiempo en que comienza
                tiempo_actual_pausa = tiempo_log
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
            if evento in ['COMPLETEAGENT', 'COMPLETECALLER'] and not es_llamada_manual:
                tiempo_en_llamada += duracion_llamada
            if evento in ['COMPLETEAGENT', 'COMPLETECALLER'] and es_llamada_manual:
                tiempo_en_llamada += duracion_llamada
                tiempo_en_llamada_manual += duracion_llamada
            elif evento in ['ANSWER', 'CONNECT'] and not es_llamada_manual:
                cantidad_llamadas_procesadas += 1
            elif evento in ['ANSWER', 'CONNECT'] and es_llamada_manual:
                cantidad_llamadas_procesadas += 1
                cantidad_llamadas_manuales += 1
            elif evento in LlamadaLog.EVENTOS_NO_CONEXION:
                cantidad_llamadas_perdidas += 1
        return (tiempo_en_llamada, tiempo_en_llamada_manual, cantidad_llamadas_procesadas,
                cantidad_llamadas_perdidas, cantidad_llamadas_manuales)

    def calcular_tiempo_agente(self, agente, fecha_inferior, fecha_superior, campana):
        if fecha_inferior and fecha_superior:
            # se obtienen las fechas en formato datetime desde el inicio y hasta el final
            # respectivamente
            fecha_desde = datetime.datetime.combine(fecha_inferior, datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_superior, datetime.time.max)
        ahora = timezone.now()
        if fecha_superior.date() == ahora.date():
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
