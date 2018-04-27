# -*- coding: utf-8 -*-

"""
Servicio para generar reporte grafico de un agente en particular para una campana
"""

import datetime
import logging as _logging

import pygal
from pygal.style import Style

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

    def obtener_cantidad_calificacion(self, campana, fecha_desde, fecha_hasta,
                                      agente):
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
        opciones_calificacion = campana.opciones_calificacion.all()
        calificaciones_query = CalificacionCliente.objects.filter(
            agente=agente, opcion_calificacion__campana=campana, fecha__range=(
                fecha_desde, fecha_hasta))
        calificaciones_nombre = []
        calificaciones_cantidad = []
        total_asignados = len(calificaciones_query)
        for opcion_calificacion in opciones_calificacion:
            cant = len(calificaciones_query.filter(opcion_calificacion=opcion_calificacion))
            calificaciones_nombre.append(opcion_calificacion.nombre)
            calificaciones_cantidad.append(cant)
        return calificaciones_nombre, calificaciones_cantidad, total_asignados

    def _obtener_tiempo_sesion_agente(self, logs_actividad_agente):
        tiempo_sesion, tiempo_pausa = (0, 0)
        tiempo_actual_sesion, tiempo_actual_pausa = (None, None)
        for log_actividad_agente in logs_actividad_agente:
            # se calculan los tiempos de sesión del agente
            evento = log_actividad_agente.event
            tiempo_log = log_actividad_agente.time
            inicio_dia = tiempo_log.replace(hour=0, minute=0, second=0, microsecond=0)
            if evento == 'REMOVEMEMBER' and tiempo_actual_sesion is None:
                # el agente inicio sesión el día anterior, sumamos el tiempo
                # desde que inicia el día
                tiempo_sesion += (tiempo_log - inicio_dia).total_seconds()
            elif evento == 'REMOVEMEMBER' and tiempo_actual_sesion is not None:
                # se cierra la sesión de un agente que estuvo conectado previamente
                tiempo_sesion += (tiempo_log - tiempo_actual_sesion).total_seconds()
                tiempo_actual_sesion = None
            elif evento == 'ADDMEMBER' and tiempo_actual_sesion is None:
                tiempo_actual_sesion = tiempo_log
            # se calculan los tiempos de pausa del agente
            if evento == 'UNPAUSEALL' and tiempo_actual_pausa is None:
                # el agente estaba en pausa desde el día anterior, sumamos el tiempo
                # desde que inicia el día
                tiempo_pausa += (tiempo_log - inicio_dia).total_seconds()
            elif evento == 'UNPAUSEALL' and tiempo_actual_pausa is not None:
                # se cierra la pausa de un agente que estuvo pausado previamente
                tiempo_pausa += (tiempo_log - tiempo_actual_pausa).total_seconds()
                tiempo_actual_pausa = None
            elif evento == 'PAUSEALL' and tiempo_actual_sesion is None:
                tiempo_actual_pausa = tiempo_log
        final_dia = tiempo_log.replace(hour=23, minute=59, second=59, microsecond=999999)
        if tiempo_actual_sesion is not None:
            # el agente no terminó su sesión en el día, sumamos el tiempo restante hasta el final
            # del día
            tiempo_sesion += (final_dia - tiempo_log).total_seconds()
        if tiempo_actual_pausa is not None:
            # el agente no terminó su pausa en el día, sumamos el tiempo restante hasta el final
            # del día
            tiempo_pausa += (final_dia - tiempo_log).total_seconds()
        return tiempo_sesion, tiempo_pausa

    def calcular_tiempo_agente(self, agente, fecha_inferior, fecha_superior, campana):
        if fecha_inferior and fecha_superior:
            fecha_desde = datetime.datetime.combine(fecha_inferior, datetime.time.min)
            fecha_hasta = datetime.datetime.combine(fecha_superior, datetime.time.max)
        logs_actividad_agente = ActividadAgenteLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta)).order_by('-time')
        logs_llamadas_agente = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk, agente_id=agente.pk)
        agente_tiempos = AgenteTiemposReporte(agente, None, None, None, 0, 0, None, None)

        tiempo_sesion, tiempo_pausa = self._obtener_actividad_agente(logs_actividad_agente)

        for log_llamada_agente in logs_llamadas_agente:
            pass
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
