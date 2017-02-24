# -*- coding: utf-8 -*-

import pygal
import datetime
import os

from pygal.style import Style, RedBlueStyle

from django.conf import settings
from django.db.models import Count
from ominicontacto_app.models import CalificacionCliente
from ominicontacto_app.services.campana_service import CampanaService

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
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        calificaciones = campana.calificacion_campana.calificacion.all()
        calificaciones_query = CalificacionCliente.objects.filter(
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

    def obtener_agentes_campana(self, campana):
        member_dict = campana.queue_campana.queuemember.all()
        members_campana = []
        for member in member_dict:
            members_campana.append(member.member)

        return members_campana

    def obtener_venta(self, campana, members_campana, fecha_desde, fecha_hasta):
        agentes_venta = []
        total_calificados = 0
        total_ventas = 0

        for agente in members_campana:
            dato_agente = []
            dato_agente.append(agente)
            total_cal_agente = len(agente.calificaciones.filter(
                campana=campana, fecha__range=(fecha_desde, fecha_hasta)))
            dato_agente.append(total_cal_agente)
            total_calificados += total_cal_agente
            total_ven_agente = len(agente.calificaciones.filter(
                campana=campana, es_venta=True,
                fecha__range=(fecha_desde, fecha_hasta)))
            dato_agente.append(total_ven_agente)
            total_ventas += total_ven_agente
            agentes_venta.append(dato_agente)
        return agentes_venta, total_calificados, total_ventas

    def obtener_cantidad_no_atendidos(self, campana, fecha_desde, fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        campana_log_wombat = campana.logswombat.filter(
            fecha_hora__range=(fecha_desde, fecha_hasta))
        campana_log_wombat = campana_log_wombat.exclude(estado="TERMINATED")
        campana_log_wombat = campana_log_wombat.values('estado').annotate(
            Count('estado'))

        resultado_nombre = []
        resultado_cantidad = []
        total_no_atendidos = 0
        for resultado in campana_log_wombat:
            estado = resultado['estado']
            if estado == "RS_LOST" and resultado['calificacion'] == "":
                estado = "Agente no disponible"
            elif estado == "RS_BUSY":
                estado = "Ocupado"
            elif estado == "RS_NOANSWER":
                estado = "No contesta"
            resultado_nombre.append(estado)
            resultado_cantidad.append(resultado['estado__count'])
            total_no_atendidos += resultado['estado__count']
        return resultado_nombre, resultado_cantidad, total_no_atendidos

    def obtener_total_llamadas(self, campana):
        campana_service = CampanaService()
        dato_campana = campana_service.obtener_dato_campana_run(campana)
        llamadas_pendientes = dato_campana['n_est_remaining_calls']
        llamadas_realizadas = dato_campana['n_calls_attempted']
        return llamadas_pendientes, llamadas_realizadas

    def obtener_total_calificacion_agente(self, campana, members_campana,
                                          fecha_desde, fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        agentes_venta = []
        total_calificados = 0
        total_ventas = 0

        calificaciones = campana.calificacion_campana.calificacion.all()

        dict_calificaciones = {}

        for calificacion in calificaciones:
            dict_calificaciones.update({calificacion.pk: 0})

        for agente in members_campana:
            dato_agente = []
            dato_agente.append(agente)
            agente_calificaciones = agente.calificaciones.filter(
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
                es_venta=True).count()
            dato_agente.append(total_ven_agente)
            total_ventas += total_ven_agente
            agentes_venta.append(dato_agente)

        return agentes_venta, total_calificados, total_ventas, calificaciones

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta):
        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde,
                                               fecha_hasta)

        resultado_nombre, resultado_cantidad, total_no_atendidos = \
            self.obtener_cantidad_no_atendidos(campana, fecha_desde,
                                               fecha_hasta)

        members_campana = self.obtener_agentes_campana(campana)
        #agentes_venta, total_calificados, total_ventas = self.obtener_venta(
         #   campana, members_campana, fecha_desde, fecha_hasta)

        total_calificacion_agente = self.obtener_total_calificacion_agente(
            campana, members_campana, fecha_desde, fecha_hasta
        )
        agentes_venta = total_calificacion_agente[0]
        total_calificados = total_calificacion_agente[1]
        total_ventas = total_calificacion_agente[2]
        calificaciones = total_calificacion_agente[3]

        llamadas_pendientes, llamadas_realizadas = self.obtener_total_llamadas(
            campana)

        dic_estadisticas = {
            'agentes_venta': agentes_venta,
            'total_asignados': total_asignados,
            'total_ventas': total_ventas,
            'calificaciones_nombre': calificaciones_nombre,
            'calificaciones_cantidad': calificaciones_cantidad,
            'total_calificados': total_calificados,
            'resultado_nombre': resultado_nombre,
            'resultado_cantidad': resultado_cantidad,
            'total_no_atendidos': total_no_atendidos,
            'llamadas_pendientes': llamadas_pendientes,
            'llamadas_realizadas': llamadas_realizadas,
            'calificaciones': calificaciones
        }
        return dic_estadisticas

    def general_campana(self, campana, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(campana, fecha_inferior,
                                                   fecha_superior)

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
        barra_campana_calificacion.render_to_png(os.path.join(settings.MEDIA_ROOT,
            "reporte_campana", "barra_campana_calificacion.png"))

        # Barra: Total de llamados no atendidos en cada intento por campana.
        barra_campana_no_atendido = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=ESTILO_AZUL_ROJO_AMARILLO)
        barra_campana_no_atendido.title = 'Cantidad de llamadas no atendidos '

        barra_campana_no_atendido.x_labels = \
            estadisticas['resultado_nombre']
        barra_campana_no_atendido.add('cantidad',
                                      estadisticas['resultado_cantidad'])
        barra_campana_no_atendido.render_to_png(
            os.path.join(settings.MEDIA_ROOT,
                         "reporte_campana", "barra_campana_no_atendido.png"))

        return {
            'estadisticas': estadisticas,
            'barra_campana_calificacion': barra_campana_calificacion,
            'dict_campana_counter': zip(estadisticas['calificaciones_nombre'],
                                        estadisticas['calificaciones_cantidad'])
            ,
            'total_asignados': estadisticas['total_asignados'],
            'agentes_venta': estadisticas['agentes_venta'],
            'total_calificados': estadisticas['total_calificados'],
            'total_ventas': estadisticas['total_ventas'],
            'barra_campana_no_atendido': barra_campana_no_atendido,
            'dict_no_atendido_counter': zip(estadisticas['resultado_nombre'],
                                            estadisticas['resultado_cantidad']),
            'total_no_atendidos': estadisticas['total_no_atendidos'],
            'calificaciones': estadisticas['calificaciones']
        }
