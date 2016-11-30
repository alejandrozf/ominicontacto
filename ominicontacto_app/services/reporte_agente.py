# -*- coding: utf-8 -*-

import pygal
import datetime
from pygal.style import Style, RedBlueStyle

from django.db.models import Count
from ominicontacto_app.models import CalificacionCliente, Calificacion
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
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        calificaciones = campana.calificacion_campana.calificacion.all()
        calificaciones_query = CalificacionCliente.objects.filter(agente=agente,
            campana=campana, fecha__range=(fecha_desde, fecha_hasta))
        calificaciones_nombre = []
        calificaciones_cantidad = []
        total_asignados = len(calificaciones_query)
        for calificacion in calificaciones:
            cant = len(calificaciones_query.filter(calificacion=calificacion))
            calificaciones_nombre.append(calificacion.nombre)
            calificaciones_cantidad.append(cant)
        cant_venta = len(calificaciones_query.filter(es_venta=True))
        calificaciones_nombre.append('venta')
        calificaciones_cantidad.append(cant_venta)
        return calificaciones_nombre, calificaciones_cantidad, total_asignados

    def obtener_venta(self, campana, agente, fecha_desde, fecha_hasta):
        dato_agente = []
        dato_agente.append(agente)
        total_cal_agente = len(agente.calificaciones.filter(campana=campana,
                                                            fecha__range=(
                                                                fecha_desde,
                                                                fecha_hasta)))
        dato_agente.append(total_cal_agente)
        total_ven_agente = len(agente.calificaciones.filter(campana=campana,
                                                            es_venta=True,
                                                            fecha__range=(
                                                                fecha_desde,
                                                                fecha_hasta)))
        dato_agente.append(total_ven_agente)

        return dato_agente

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta, agente):
        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde,
                                               fecha_hasta, agente)
        agentes_venta = self.obtener_venta(campana, agente, fecha_desde,
                                           fecha_hasta)
        dic_estadisticas = {
            'agentes_venta': agentes_venta,
            'total_asignados': total_asignados,
            'calificaciones_nombre': calificaciones_nombre,
            'calificaciones_cantidad': calificaciones_cantidad,
        }
        return dic_estadisticas

    def general_campana(self, agente,  campana, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(campana, fecha_inferior,
                                                   fecha_superior, agente)

        if estadisticas:
            logger.info("Generando grafico calificaciones de campana por cliente ")



        # Barra: Total de llamados atendidos en cada intento por campana.
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
                                        estadisticas['calificaciones_cantidad'])
            ,
        }
