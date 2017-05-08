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
        eventos_llamadas_atendidas = ['CONNECT']
        eventos_llamadas_abandonadas = ['ABANDON']
        eventos_llamadas_expiradas = ['EXITWITHTIMEOUT']

        nombres_queues = []
        total_atendidas = []
        total_abandonadas = []
        total_expiradas = []

        queues_tiempo = []

        for queue in queues:
            ingresadas = Queuelog.objects.obtener_log_queuename_event_periodo(
                eventos_llamadas_ingresadas, fecha_inferior, fecha_superior,
                queue.campana.nombre)
            atendidas = Queuelog.objects.obtener_log_queuename_event_periodo(
                eventos_llamadas_atendidas, fecha_inferior, fecha_superior,
                queue.campana.nombre)
            abandonadas = Queuelog.objects.obtener_log_queuename_event_periodo(
                eventos_llamadas_abandonadas, fecha_inferior, fecha_superior,
                queue.campana.nombre)
            expiradas = Queuelog.objects.obtener_log_queuename_event_periodo(
                eventos_llamadas_expiradas, fecha_inferior, fecha_superior,
                queue.campana.nombre)
            count_llamadas_ingresadas = ingresadas.count()
            count_llamadas_atendidas = atendidas.count()
            count_llamadas_abandonadas = abandonadas.count()
            count_llamadas_expiradas = expiradas.count()
            count_llamadas_manuales = ingresadas.filter(data4='saliente').count()
            count_manuales_atendidas = atendidas.filter(data4='saliente').count()
            count_manuales_abandonadas = abandonadas.filter(data4='saliente').count()
            cantidad_campana = []
            cantidad_campana.append(queue.campana.nombre)
            cantidad_campana.append(count_llamadas_ingresadas)
            cantidad_campana.append(count_llamadas_atendidas)
            cantidad_campana.append(count_llamadas_expiradas)
            cantidad_campana.append(count_llamadas_abandonadas)
            cantidad_campana.append(count_llamadas_manuales)
            cantidad_campana.append(count_manuales_atendidas)
            cantidad_campana.append(count_manuales_abandonadas)

            queues_tiempo.append(cantidad_campana)

            # para reportes
            nombres_queues.append(queue.campana.nombre)
            total_atendidas.append(count_llamadas_atendidas)
            total_abandonadas.append(count_llamadas_expiradas)
            total_expiradas.append(count_llamadas_abandonadas)

        totales_grafico = {
            'nombres_queues': nombres_queues,
            'total_atendidas': total_atendidas,
            'total_abandonadas': total_abandonadas,
            'total_expiradas': total_expiradas
        }

        return queues_tiempo, totales_grafico

    def obtener_total_llamadas(self, fecha_inferior, fecha_superior):

        eventos_llamadas_ingresadas = ['ENTERQUEUE']
        eventos_llamadas_atendidas = ['CONNECT']
        eventos_llamadas_abandonadas = ['ABANDON']
        eventos_llamadas_expiradas = ['EXITWITHTIMEOUT']

        ingresadas = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_ingresadas, fecha_inferior, fecha_superior)
        atendidas = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_atendidas, fecha_inferior, fecha_superior)
        abandonadas = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_abandonadas, fecha_inferior, fecha_superior)
        expiradas = Queuelog.objects.obtener_log_event_periodo(
            eventos_llamadas_expiradas, fecha_inferior, fecha_superior)
        count_llamadas_ingresadas = ingresadas.count()
        count_llamadas_atendidas = atendidas.count()
        count_llamadas_abandonadas = abandonadas.count()
        count_llamadas_expiradas = expiradas.count()
        count_llamadas_manuales = ingresadas.filter(data4='saliente').count()
        count_manuales_atendidas = atendidas.filter(data4='saliente').count()
        count_manuales_abandonadas = abandonadas.filter(data4='saliente').count()
        cantidad_campana = []
        cantidad_campana.append(count_llamadas_ingresadas)
        cantidad_campana.append(count_llamadas_atendidas)
        cantidad_campana.append(count_llamadas_expiradas)
        cantidad_campana.append(count_llamadas_abandonadas)
        cantidad_campana.append(count_llamadas_manuales)
        cantidad_campana.append(count_manuales_atendidas)
        cantidad_campana.append(count_manuales_abandonadas)

        return cantidad_campana


    def _calcular_estadisticas(self, fecha_inferior, fecha_superior):

        cola = Queue.objects.obtener_all_except_borradas()
        campanas = Campana.objects.obtener_all_except_borradas()

        queues_llamadas, totales_grafico = self.calcular_cantidad_llamadas(
            cola, fecha_inferior, fecha_superior)

        total_llamadas = self.obtener_total_llamadas(fecha_inferior, fecha_superior)

        dic_estadisticas = {
            'queues_llamadas': queues_llamadas,
            'fecha_desde': fecha_inferior,
            'fecha_hasta': fecha_superior,
            'total_llamadas': total_llamadas,
            'totales_grafico': totales_grafico,

        }
        return dic_estadisticas

    def general_campana(self, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(fecha_inferior,
                                                   fecha_superior)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")

        # Barra: Total de llamados atendidos en cada intento por campana.
        barra_campana_llamadas = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_llamadas.title = 'Distribucion por campana'

        barra_campana_llamadas.x_labels = \
            estadisticas['totales_grafico']['nombres_queues']
        barra_campana_llamadas.add('atendidas',
                                   estadisticas['totales_grafico']['total_atendidas'])
        barra_campana_llamadas.add('abandonadas ',
                                   estadisticas['totales_grafico']['total_abandonadas'])
        barra_campana_llamadas.add('expiradas',
                                   estadisticas['totales_grafico']['total_expiradas'])


        return {
            'estadisticas': estadisticas,
            'barra_campana_llamadas': barra_campana_llamadas,

        }
