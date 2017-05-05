# -*- coding: utf-8 -*-

import pygal
import datetime
import os

from pygal.style import Style, RedBlueStyle

from django.conf import settings
from django.db.models import Count
from ominicontacto_app.models import AgenteProfile, Queuelog, Campana, Queue
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


class EstadisticasCampanaLlamadasService():



    def calcular_cantidad_llamadas(self, queues, fecha_inferior, fecha_superior):

        eventos_llamadas_ingresadas = ['ENTERQUEUE']

        queues_tiempo = []

        for queue in queues:
            logs_time = Queuelog.objects.obtener_log_queuename_event_periodo(
                eventos_llamadas_ingresadas, fecha_inferior, fecha_superior,
                queue.campana.nombre)
            count_llamadas_ingresadas = logs_time.count()
            cantidad_campana = []
            cantidad_campana.append(queue.campana.nombre)
            cantidad_campana.append(count_llamadas_ingresadas)

            queues_tiempo.append(cantidad_campana)

        return queues_tiempo



    def _calcular_estadisticas(self, fecha_inferior, fecha_superior):

        cola = Queue.objects.obtener_all_except_borradas()
        campanas = Campana.objects.obtener_all_except_borradas()

        queues_llamadas = self.calcular_cantidad_llamadas(
            cola, fecha_inferior, fecha_superior)


        dic_estadisticas = {
            'queues_llamadas': queues_llamadas,
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,


        }
        return dic_estadisticas

    def general_campana(self, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(fecha_inferior,
                                                   fecha_superior)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")

        return estadisticas



        # # Barra: Total de llamados atendidos en cada intento por campana.
        # barra_campana_calificacion = pygal.Bar(  # @UndefinedVariable
        #     show_legend=False,
        #     style=ESTILO_AZUL_ROJO_AMARILLO)
        # barra_campana_calificacion.title = 'Cantidad de calificacion de cliente '
        #
        # barra_campana_calificacion.x_labels = \
        #     estadisticas['calificaciones_nombre']
        # barra_campana_calificacion.add('cantidad',
        #                                estadisticas['calificaciones_cantidad'])
        # barra_campana_calificacion.render_to_png(os.path.join(settings.MEDIA_ROOT,
        #     "reporte_campana", "barra_campana_calificacion.png"))
        #
        # # Barra: Total de llamados no atendidos en cada intento por campana.
        # barra_campana_no_atendido = pygal.Bar(  # @UndefinedVariable
        #     show_legend=False,
        #     style=ESTILO_AZUL_ROJO_AMARILLO)
        # barra_campana_no_atendido.title = 'Cantidad de llamadas no atendidos '
        #
        # barra_campana_no_atendido.x_labels = \
        #     estadisticas['resultado_nombre']
        # barra_campana_no_atendido.add('cantidad',
        #                               estadisticas['resultado_cantidad'])
        # barra_campana_no_atendido.render_to_png(
        #     os.path.join(settings.MEDIA_ROOT,
        #                  "reporte_campana", "barra_campana_no_atendido.png"))
        #
        # return {
        #     'estadisticas': estadisticas,
        #     'barra_campana_calificacion': barra_campana_calificacion,
        #     'dict_campana_counter': zip(estadisticas['calificaciones_nombre'],
        #                                 estadisticas['calificaciones_cantidad'])
        #     ,
        #     'total_asignados': estadisticas['total_asignados'],
        #     'agentes_venta': estadisticas['agentes_venta'],
        #     'total_calificados': estadisticas['total_calificados'],
        #     'total_ventas': estadisticas['total_ventas'],
        #     'barra_campana_no_atendido': barra_campana_no_atendido,
        #     'dict_no_atendido_counter': zip(estadisticas['resultado_nombre'],
        #                                     estadisticas['resultado_cantidad']),
        #     'total_no_atendidos': estadisticas['total_no_atendidos'],
        #     'calificaciones': estadisticas['calificaciones']
        # }
