# -*- coding: utf-8 -*-

"""
Servicio para generar reporte grafico de un agente en particular para una campana
"""

import pygal
import datetime
from pygal.style import Style

from ominicontacto_app.models import CalificacionCliente, OpcionCalificacion, Queuelog
from ominicontacto_app.services.queue_log_service import AgenteTiemposReporte
import logging as _logging

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

    def obtener_venta(self, campana, agente, fecha_desde, fecha_hasta):
        """
        Obtiene total de calificado como no gestion y el total de los calificado como
        gestion(venta)
        :param campana: campana la cual se evaluara las calificaciones
        :param agente: agente el caul se evauluara sus calificaciones
        :param fecha_desde: fecha desde el cual se obtendran las calificaciones
        :param fecha_hasta: fecha hasta la cual se obtendran las calificaciones
        :return: los totales calificados como no gestion y los calificado como gestion
        """
        dato_agente = []
        dato_agente.append(agente)
        total_cal_agente = len(agente.calificaciones.filter(
            opcion_calificacion__campana=campana, fecha__range=(fecha_desde, fecha_hasta)))
        dato_agente.append(total_cal_agente)
        total_ven_agente = len(agente.calificaciones.filter(
            opcion_calificacion__campana=campana,
            opcion_calificacion__tipo=OpcionCalificacion.GESTION,
            fecha__range=(
                fecha_desde,
                fecha_hasta)))
        dato_agente.append(total_ven_agente)
        return dato_agente

    def calcular_tiempo_agente(self, agente, fecha_inferior, fecha_superior, campana):
        eventos_pausa = ['PAUSEALL', 'UNPAUSEALL']
        agente_nuevo = AgenteTiemposReporte(agente, None, None, None, 0, 0, None, None)

        logs_time = Queuelog.objects.obtener_log_agente_pk_event_periodo_all(
            eventos_pausa, fecha_inferior, fecha_superior, agente.id)
        is_unpause = False
        time_actual = None
        for logs in logs_time:
            if is_unpause and logs.event == 'PAUSEALL':
                resta = time_actual - logs.time

                if agente_nuevo.tiempo_pausa:
                    agente_nuevo._tiempo_pausa += resta
                else:
                    agente_nuevo._tiempo_pausa = resta

                is_unpause = False
                time_actual = None
            if logs.event == 'UNPAUSEALL':
                time_actual = logs.time
                is_unpause = True

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']

        logs_time = Queuelog.objects.obtener_log_agente_pk_event_periodo_all(
            eventos_sesion, fecha_inferior, fecha_superior, agente.id)
        is_remove = False
        time_actual = None
        for logs in logs_time:
            if is_remove and logs.event == 'ADDMEMBER':
                resta = time_actual - logs.time

                if agente_nuevo.tiempo_sesion:
                    agente_nuevo._tiempo_sesion += resta
                else:
                    agente_nuevo._tiempo_sesion = resta

                is_remove = False
                time_actual = None
            if logs.event == 'REMOVEMEMBER':
                time_actual = logs.time
                is_remove = True

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        logs_time = Queuelog.objects.obtener_log_agente_campana_event_periodo(
            eventos_llamadas, fecha_inferior, fecha_superior, agente.id, campana.id)
        lista_tiempo_llamada = [int(log.data2) for log in logs_time]

        agente_nuevo._tiempo_llamada = sum(lista_tiempo_llamada)

        eventos_llamadas_perdidas = ['RINGNOANSWER']

        logs_time = Queuelog.objects.obtener_log_agente_campana_event_periodo(
            eventos_llamadas, fecha_inferior, fecha_superior, agente.id, campana.id)
        logs_time_perdidas = Queuelog.objects.obtener_log_agente_campana_event_periodo(
            eventos_llamadas_perdidas, fecha_inferior, fecha_superior, agente.id,
            campana.id)

        agente_nuevo._cantidad_llamadas_procesadas = logs_time.count()
        agente_nuevo._cantidad_llamadas_perdidas = logs_time_perdidas.count()

        eventos_llamadas = ['COMPLETECALLER', 'COMPLETEAGENT']

        logs_time = Queuelog.objects.obtener_log_agente_campana_event_periodo(
            eventos_llamadas, fecha_inferior, fecha_superior, agente.id, campana.id)
        lista_tiempo_llamada = [int(log.data2) for log in logs_time]
        logs_saliente = logs_time.filter(data4='saliente')
        lista_tiempo_saliente = [int(log.data2) for log in logs_saliente]
        cantidad_llamadas = logs_time.count()
        cantidad_saliente = logs_saliente.count()
        cantidad_asignadas = cantidad_llamadas - cantidad_saliente
        tiempo_llamadas = sum(lista_tiempo_llamada)
        tiempo_saliente = sum(lista_tiempo_saliente)
        tiempo_asignadas = tiempo_llamadas - tiempo_saliente
        media_asignadas = 0
        if tiempo_asignadas > 0:
            media_asignadas = tiempo_asignadas / cantidad_asignadas
        media_salientes = 0
        if tiempo_saliente > 0:
            media_salientes = tiempo_saliente / cantidad_saliente

        agente_nuevo._media_asignada = media_asignadas
        agente_nuevo._media_saliente = media_salientes
        return agente_nuevo

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta, agente):
        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde,
                                               fecha_hasta, agente)
        agentes_venta = self.obtener_venta(campana, agente, fecha_desde,
                                           fecha_hasta)

        agente_tiempo = self.calcular_tiempo_agente(agente, fecha_desde, fecha_hasta,
                                                    campana)

        dic_estadisticas = {
            'agentes_venta': agentes_venta,
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
