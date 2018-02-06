# -*- coding: utf-8 -*-

"""
Servicio para generar reporte grafico de una campana
"""

import pygal
import datetime
import os

from pygal.style import Style

from django.conf import settings
from ominicontacto_app.models import Queuelog, CalificacionManual

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

    def obtener_cantidad_calificacion(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene las cantidad de llamadas por calificacion de la campana y el total de
        llamadas calificadas
        :param campana: campana la cual se van obtiene las calificaciones
        :param fecha_desde: fecha desde que se va evaluar las calificaciones
        :param fecha_hasta: fecha hasta que se va evaluar las calificaciones
        :return: calificaciones_nombre - nombre de las calificaciones
        calificaciones_cantidad - cantidad de llamdas por calificacion
        total_asignados - cantidad total de calificaciones
        """
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        calificaciones = campana.calificacion_campana.calificacion.all()
        calificaciones_query = CalificacionManual.objects.filter(
            campana=campana, fecha__range=(fecha_desde, fecha_hasta))
        calificaciones_nombre = []
        calificaciones_cantidad = []
        total_asignados = len(calificaciones_query)
        for calificacion in calificaciones:
            cant = len(calificaciones_query.filter(calificacion=calificacion))
            calificaciones_nombre.append(calificacion.nombre)
            calificaciones_cantidad.append(cant)
        return calificaciones_nombre, calificaciones_cantidad, total_asignados

    def obtener_agentes_campana(self, campana):
        """
        Obtiene los agentes asigandos a esta campana
        :param campana: campana la cual se obtiene los agentes
        :return: los agentes asigandos a la campana
        """
        member_dict = campana.queue_campana.queuemember.all()
        members_campana = []
        for member in member_dict:
            members_campana.append(member.member)

        return members_campana

    def obtener_total_calificacion_agente(self, campana, members_campana,
                                          fecha_desde, fecha_hasta):
        """
        Obtiene el total de las calificaciones por calificacion por agente
        :param campana: campana de las cual se obtiene las campana
        :param members_campana: agentes de la campana
        :param fecha_desde: fecha desde la que se obtendran las calificacioens
        :param fecha_hasta: fecha hasta la que se obtendran las calificaciones
        :return: agentes_venta, un dicionario con el total des las calificaciones,
        una lista con el total de las calificaciones y las calificaciones
        """
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        agentes_venta = []
        total_calificados = 0
        total_ventas = 0

        calificaciones = campana.calificacion_campana.calificacion.all()

        dict_calificaciones = {}
        # armo dict de las calificaciones e inicializandolo en 0
        for calificacion in calificaciones:
            dict_calificaciones.update({calificacion.pk: 0})

        for agente in members_campana:
            dato_agente = []
            dato_agente.append(agente)
            agente_calificaciones = agente.calificacionesmanuales.filter(
                campana=campana, fecha__range=(fecha_desde, fecha_hasta))
            total_cal_agente = agente_calificaciones.count()
            dato_agente.append(total_cal_agente)
            total_calificados += total_cal_agente

            dict_total = dict_calificaciones.copy()

            for calificacion in calificaciones:
                cantidad = agente_calificaciones.filter(
                    calificacion=calificacion).count()
                dict_total[calificacion.pk] = cantidad

            dato_agente.append(dict_total)

            total_ven_agente = agente_calificaciones.filter(
                es_gestion=True).count()
            dato_agente.append(total_ven_agente)
            total_ventas += total_ven_agente
            agentes_venta.append(dato_agente)

        return agentes_venta, total_calificados, total_ventas, calificaciones

    def calcular_cantidad_llamadas(self, campana, fecha_inferior, fecha_superior):
        """
        Obtiene las cantidades toteles detalladas como resultado de las llamadas
        :param campana: campana la cuales se obtendran el detalle de la llamada
        :param fecha_inferior: fecha desde la cual se obtendran las llamadas
        :param fecha_superior: fecha hasta la cual se obtendran las llamadas
        :return: los eventos de llamadas con sus cantidades totales
        """
        eventos_llamadas_ingresadas = ['ENTERQUEUE']
        eventos_llamadas_atendidas = ['CONNECT']
        eventos_llamadas_abandonadas = ['ABANDON']
        eventos_llamadas_expiradas = ['EXITWITHTIMEOUT']

        # obtiene las llamadas recibidas
        ingresadas = Queuelog.objects.obtener_log_campana_id_event_periodo(
            eventos_llamadas_ingresadas, fecha_inferior, fecha_superior, campana.id)
        # obtiene las llamadas atendidas
        atendidas = Queuelog.objects.obtener_log_campana_id_event_periodo(
            eventos_llamadas_atendidas, fecha_inferior, fecha_superior, campana.id)
        # obtiene las llamadas abandonadas
        abandonadas = Queuelog.objects.obtener_log_campana_id_event_periodo(
            eventos_llamadas_abandonadas, fecha_inferior, fecha_superior, campana.id)
        # obtiene las llamadas expiradas
        expiradas = Queuelog.objects.obtener_log_campana_id_event_periodo(
            eventos_llamadas_expiradas, fecha_inferior, fecha_superior, campana.id)
        count_llamadas_ingresadas = ingresadas.count()
        count_llamadas_atendidas = atendidas.count()
        count_llamadas_abandonadas = abandonadas.count()
        count_llamadas_expiradas = expiradas.count()
        count_llamadas_manuales = ingresadas.filter(data4='saliente').count()
        count_manuales_atendidas = atendidas.filter(data4='saliente').count()
        count_manuales_abandonadas = abandonadas.filter(data4='saliente').count()
        cantidad_campana = []
        nombres_cantidades = ["Recibidas", "Atendidas", "Expiradas", "Abandonadas",
                              "Manuales", "Manuales atendidas", "Manuales no atendidas"]
        cantidad_campana.append(count_llamadas_ingresadas)
        cantidad_campana.append(count_llamadas_atendidas)
        cantidad_campana.append(count_llamadas_expiradas)
        cantidad_campana.append(count_llamadas_abandonadas)
        cantidad_campana.append(count_llamadas_manuales)
        cantidad_campana.append(count_manuales_atendidas)
        cantidad_campana.append(count_manuales_abandonadas)

        return nombres_cantidades, cantidad_campana

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta):
        # obtener cantidad de calificaciones por campana
        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde,
                                               fecha_hasta)

        # obtiene los agentes miembros a la campana
        members_campana = self.obtener_agentes_campana(campana)

        # obtiene el total de calificaciones por agente
        total_calificacion_agente = self.obtener_total_calificacion_agente(
            campana, members_campana, fecha_desde, fecha_hasta
        )
        agentes_venta = total_calificacion_agente[0]
        total_calificados = total_calificacion_agente[1]
        total_ventas = total_calificacion_agente[2]
        calificaciones = total_calificacion_agente[3]

        # obtiene las cantidades totales por evento de las llamadas
        cantidad_llamadas = self.calcular_cantidad_llamadas(
            campana, fecha_desde, fecha_hasta)

        dic_estadisticas = {
            'agentes_venta': agentes_venta,
            'total_asignados': total_asignados,
            'total_ventas': total_ventas,
            'calificaciones_nombre': calificaciones_nombre,
            'calificaciones_cantidad': calificaciones_cantidad,
            'total_calificados': total_calificados,
            # 'resultado_nombre': resultado_nombre,
            # 'resultado_cantidad': resultado_cantidad,

            'calificaciones': calificaciones,
            'cantidad_llamadas': cantidad_llamadas,
        }
        return dic_estadisticas

    def general_campana(self, campana, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(campana, fecha_inferior,
                                                   fecha_superior)

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
        barra_campana_calificacion.render_to_png(os.path.join(
            settings.MEDIA_ROOT,
            "reporte_campana", "barra_campana_calificacion.png"))

        # Barra: Total de llamados no atendidos en cada intento por campana.
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

        # Barra: Detalles de llamadas por evento de llamada.
        barra_campana_llamadas = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_llamadas.title = 'Detalles de llamadas '

        barra_campana_llamadas.x_labels = \
            estadisticas['cantidad_llamadas'][0]
        barra_campana_llamadas.add('cantidad',
                                   estadisticas['cantidad_llamadas'][1])

        return {
            'estadisticas': estadisticas,
            'barra_campana_calificacion': barra_campana_calificacion,
            'dict_campana_counter': zip(estadisticas['calificaciones_nombre'],
                                        estadisticas['calificaciones_cantidad']),
            'total_asignados': estadisticas['total_asignados'],
            'agentes_venta': estadisticas['agentes_venta'],
            'total_calificados': estadisticas['total_calificados'],
            'total_ventas': estadisticas['total_ventas'],
            # 'barra_campana_no_atendido': barra_campana_no_atendido,
            # 'dict_no_atendido_counter': zip(estadisticas['resultado_nombre'],
            #                               estadisticas['resultado_cantidad']),

            'calificaciones': estadisticas['calificaciones'],
            'barra_campana_llamadas': barra_campana_llamadas,
            'dict_llamadas_counter': zip(estadisticas['cantidad_llamadas'][0],
                                         estadisticas['cantidad_llamadas'][1]),

        }
