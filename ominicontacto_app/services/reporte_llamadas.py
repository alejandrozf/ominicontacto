# -*- coding: utf-8 -*-

import pygal
import datetime
import os

from pygal.style import Style, RedBlueStyle

from django.conf import settings
from django.db.models import Count
from ominicontacto_app.models import AgenteProfile, Queuelog
from ominicontacto_app.services.queue_log_service import QueueLogService

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


class EstadisticasService():

    def _obtener_agentes(self):
        agentes = []
        for agente in Queuelog.objects.all().distinct('agent'):
            agentes.append(agente.agent)
        return agentes

    def calcular_tiempo_sesion(self, agentes):

        eventos_sesion = ['ADDMEMBER', 'REMOVEMEMBER']

        logs_queue = Queuelog.objects.filter(event__in=eventos_sesion).order_by(
            '-time')

        agentes_tiempo = []
        print logs_queue
        print agentes
        for agente in agentes:
            tiempo_agente = []
            logs_time = logs_queue.filter(agent=agente)
            print logs_time
            is_remove = False
            time_actual = None
            for logs in logs_time:
                if is_remove and logs.event == 'ADDMEMBER':
                    resta = time_actual - logs.time
                    print resta
                    tiempo_agente.append(agente)
                    tiempo_agente.append(logs.time.strftime('%Y-%m-%d'))
                    tiempo_string = str(resta) + "hs"
                    tiempo_agente.append(str(tiempo_string))
                    agentes_tiempo.append(tiempo_agente)
                    tiempo_agente = []
                    is_remove = False
                    time_actual = None
                if logs.event == 'REMOVEMEMBER':
                    time_actual = logs.time
                    is_remove = True
        print agentes_tiempo
        return agentes_tiempo

    def _calcular_estadisticas(self):
        agentes = self._obtener_agentes()
        agentes_tiempo = self.calcular_tiempo_sesion(agentes)

        dic_estadisticas = {
            'agentes_tiempo': agentes_tiempo

        }
        return dic_estadisticas

    def general_campana(self):
        estadisticas = self._calcular_estadisticas()

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")



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
