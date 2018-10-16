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
Servicio para generar reporte grafico de una campana
"""

import pygal
import os

from collections import OrderedDict
from pygal.style import Style

from django.conf import settings
from django.db.models import Count, Q
from django.utils.translation import ugettext as _

from ominicontacto_app.utiles import datetime_hora_maxima_dia, datetime_hora_minima_dia
from ominicontacto_app.models import (AgenteEnContacto, CalificacionCliente, Campana,
                                      OpcionCalificacion)
from ominicontacto_app.services.campana_service import CampanaService
from reportes_app.models import LlamadaLog

from utiles_globales import obtener_cantidad_no_calificados

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

    def _obtener_cantidad_no_calificados(
            self, campana, fecha_desde, fecha_hasta):
        """
        Devuelve la cantidad de llamadas recibidas por agentes pero no calificadas por estos.
        Manual y Preview contar logs con ANSWER
        Dialer y Entrante contar logs con CONNECT
        """
        total_llamadas_campanas_qs = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk).filter(
                Q(event='ANSWER', tipo_campana__in=[Campana.TYPE_MANUAL, Campana.TYPE_PREVIEW]) |
                Q(event='ANSWER', tipo_campana__in=[Campana.TYPE_DIALER, Campana.TYPE_ENTRANTE],
                  tipo_llamada=LlamadaLog.LLAMADA_MANUAL) |
                Q(event='CONNECT'))
        return obtener_cantidad_no_calificados(
            total_llamadas_campanas_qs, fecha_desde, fecha_hasta, campana)

    def obtener_cantidad_calificacion(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene las cantidades de llamadas por calificacion de la campana y el total de
        llamadas calificadas
        :param campana: campana la cual se van obtiene las calificaciones
        :param fecha_desde: fecha desde que se va evaluar las calificaciones
        :param fecha_hasta: fecha hasta que se va evaluar las calificaciones
        :return: calificaciones_nombre - nombre de las calificaciones
        calificaciones_cantidad - cantidad de llamadas por calificacion
        total_asignados - cantidad total de calificaciones
        """
        calificaciones_query = CalificacionCliente.objects.filter(
            opcion_calificacion__campana=campana,
            fecha__range=(fecha_desde, fecha_hasta)).values('opcion_calificacion__nombre').annotate(
                cantidad=Count('opcion_calificacion__nombre'))
        calificaciones_nombre = []
        calificaciones_cantidad = []
        total_calificados = 0
        for opcion_calificacion_cantidad in calificaciones_query:
            nombre = opcion_calificacion_cantidad['opcion_calificacion__nombre']
            cantidad = opcion_calificacion_cantidad['cantidad']
            total_calificados += cantidad
            calificaciones_nombre.append(nombre)
            calificaciones_cantidad.append(cantidad)
        total_no_calificados = self._obtener_cantidad_no_calificados(
            campana, fecha_desde, fecha_hasta)
        calificaciones_nombre.append(_("Llamadas Atendidas sin calificacion"))
        calificaciones_cantidad.append(total_no_calificados)
        total_asignados = total_calificados + total_no_calificados
        return calificaciones_nombre, calificaciones_cantidad, total_asignados

    def obtener_cantidad_no_atendidos(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene los llamados no atendidos por campana
        :param campana: campana a la cual se van obtener los llamados no atendidos
        :param fecha_desde: fecha desde la cual se obtener los llamados no atendidos
        :param fecha_hasta: fehca hasta la cual se va obtener los llamados no atendidos
        :return: nombre del evento no atendidos, la cantidad por ese evento y el total
        de  llamados no atendidos
        """

        reporte = OrderedDict(
            # se cuentan todos los eventos NOANSWER
            [(_('Cliente no atiende'), 0),
             # se cuentan todos los eventos CANCEL
             (_('Cancelado'), 0),
             # se cuentan todos los eventos AMD
             (_('Contestador detectado'), 0),
             # se cuentan todos los eventos BUSY
             (_('Ocupado'), 0),
             # se cuentan todos los evento CHANUNAVAIL
             (_('Canales No disponibles'), 0),
             # se cuentan todos los eventos FAIL
             (_('Fallidas'), 0),
             # se cuentan todos los eventos OTHER
             (_('Otro'), 0),
             # se cuentan todos los eventos BLACKLIST
             (_('Blacklist'), 0),
             # se cuentan todos los eventos ABANDON
             (_('Abandonadas por el cliente'), 0),
             # se cuentan todos los eventos EXITWITHTIMEOUT
             (_('Expiradas'), 0)]
        )
        # LlamadaLog.EVENTOS_NO_CONEXION
        eventos_headers = {
            'NOANSWER': _('Cliente no atiende'),
            'CANCEL': _('Cancelado'),
            'AMD': _('Contestador detectado'),
            'BUSY': _('Ocupado'),
            'CHANUNAVAIL': _('Canales No disponibles'),
            'FAIL': _('Fallidas'),
            'OTHER': _('Otro'),
            'BLACKLIST': _('Blacklist'),
            'ABANDON': _('Abandonadas por el cliente'),
            'EXITWITHTIMEOUT': _('Expiradas'),
            'CONGESTION': _('Canal congestionado'),
            'NONDIALPLAN': _('Problema de enrutamiento'),
        }
        llamadas_no_atendidas_campana = LlamadaLog.objects.filter(
            campana_id=campana.pk, time__range=(fecha_desde, fecha_hasta)).values(
                'event').annotate(cantidad=Count('event'))
        total_no_atendidos = 0
        for evento_cantidad in llamadas_no_atendidas_campana:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            evento_header = eventos_headers.get(evento, False)
            if evento_header:
                reporte[evento_header] = cantidad
                total_no_atendidos += cantidad
        return reporte.keys(), reporte.values(), total_no_atendidos

    def obtener_total_llamadas(self, campana):
        """
        Obtiene los totales de llamadas realizadas y pendiente por la campana
        :param campana: campana la cual se obtiene los totales
        :return: lso totales de llamadas realizadas y pendiente de la campana
        """
        logs_llamadas_campana = LlamadaLog.objects.filter(campana_id=campana.pk).values(
            'event').annotate(cantidad=Count('event'))
        dict_eventos_campana = {}
        for evento_cantidad in logs_llamadas_campana:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            dict_eventos_campana[evento] = cantidad
        llamadas_pendientes, llamadas_realizadas, llamadas_recibidas = (None,) * 3
        llamadas_realizadas = dict_eventos_campana.get('DIAL', 0)
        if campana.type == Campana.TYPE_DIALER:
            campana_service = CampanaService()
            dato_campana = campana_service.obtener_dato_campana_run(campana)
            llamadas_pendientes = 0
            if dato_campana:
                llamadas_pendientes = dato_campana.get('n_est_remaining_calls', 0)
        elif campana.type == Campana.TYPE_ENTRANTE:
            llamadas_recibidas = dict_eventos_campana.get('ENTERQUEUE', 0)
            llamadas_recibidas_transferidas = dict_eventos_campana.get('ENTERQUEUE-TRANSFER', 0)
            llamadas_recibidas += llamadas_recibidas_transferidas
        elif campana.type == Campana.TYPE_PREVIEW:
            llamadas_pendientes = AgenteEnContacto.objects.filter(
                estado=AgenteEnContacto.ESTADO_INICIAL, campana_id=campana.pk).count()
        return llamadas_pendientes, llamadas_realizadas, llamadas_recibidas

    def obtener_total_calificacion_agente(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene el total de las calificaciones por calificacion por agente
        :param campana: campana de las cual se obtiene las campana
        :param members_campana: agentes de la campana
        :param fecha_desde: fecha desde la que se obtendran las calificacioens
        :param fecha_hasta: fecha hasta la que se obtendran las calificaciones
        :return: agentes_venta, un dicionario con el total des las calificaciones,
        una lista con el total de las calificaciones y las calificaciones
        """
        total_calificados = 0
        total_ventas = 0

        opciones_calificaciones = campana.opciones_calificacion.all()

        dict_calificaciones = OrderedDict({})
        # armo dict de las calificaciones e inicializandolo en 0
        for opcion_calificacion in opciones_calificaciones:
            dict_calificaciones.update({opcion_calificacion.nombre: 0})

        calificaciones_campana_qs = CalificacionCliente.objects.filter(
            opcion_calificacion__campana=campana, fecha__range=(fecha_desde, fecha_hasta))

        calificaciones_agentes_dict = calificaciones_campana_qs.values(
            'agente__user__first_name', 'agente__user__last_name', 'agente',
            'opcion_calificacion__nombre', 'opcion_calificacion__tipo').annotate(
                cantidad=Count('pk'))
        dict_agentes = {}
        for calificacion_data in calificaciones_agentes_dict:
            agente_id = calificacion_data['agente']
            cantidad = calificacion_data['cantidad']
            opcion_calificacion = calificacion_data['opcion_calificacion__nombre']
            nombre_completo = "{0} {1}".format(
                calificacion_data['agente__user__first_name'],
                calificacion_data['agente__user__last_name'])
            total_calificados += cantidad
            if calificacion_data['opcion_calificacion__tipo'] == OpcionCalificacion.GESTION:
                total_ventas += cantidad
                parcial_calificados_agente_gestion = cantidad
            else:
                parcial_calificados_agente_gestion = 0
            if not dict_agentes.get(agente_id, False):
                dict_agentes[agente_id] = OrderedDict({
                    'nombre': nombre_completo,
                    'totales_calificaciones': dict_calificaciones.copy(),
                    'total_calificados': cantidad,
                    'total_gestionados': parcial_calificados_agente_gestion,
                })
            else:
                dict_agentes[agente_id]['total_calificados'] += cantidad
                dict_agentes[agente_id]['total_gestionados'] += parcial_calificados_agente_gestion
            dict_agentes[agente_id]['totales_calificaciones'][opcion_calificacion] = cantidad
        return dict_agentes, total_calificados, total_ventas, tuple(dict_calificaciones.keys())

    def _obtener_detalle_llamadas_entrantes(self, logs_llamadas_campana):
        """
        Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
        campaña de tipo entrante
        :param logs_llamadas_campana: queryset con los logs de las llamadas entrantes
        recibidas
        :return: dicionario con los totales de cada estado de las llamadas recibidas
        """
        # se cuentan todos los eventos para cada caso
        reporte = OrderedDict(
            [(_('Recibidas'), 0),
             (_('Transferencias recibidas'), 0),
             (_('Atendidas'), 0),
             (_('Expiradas'), 0),
             (_('Abandonadas'), 0),
             (_('Manuales'), 0),
             (_('Manuales atendidas'), 0)])
        eventos_headers = {
            'ENTERQUEUE': _('Recibidas'),
            'ENTERQUEUE-TRANSFER': _('Transferencias recibidas'),
            'CONNECT': _('Atendidas'),
            'EXITWITHTIMEOUT': _('Expiradas'),
            'ABANDON': _('Abandonadas'),
            'DIAL': _('Manuales'),
            'ANSWER': _('Manuales atendidas')}
        logs_campana_agrupados_eventos = logs_llamadas_campana.values('event').annotate(
            cantidad=Count('event'))
        manuales_no_atendidas = 0
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            evento_header = eventos_headers.get(evento, False)
            if evento_header:
                reporte[evento_header] = cantidad
            elif not evento_header and (evento in LlamadaLog.EVENTOS_NO_CONEXION):
                manuales_no_atendidas += cantidad
        reporte[_('Manuales no atendidas')] = manuales_no_atendidas

        return reporte

    def _obtener_detalle_llamadas_dialer(self, logs_llamadas_campana):
        """
        Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
        campaña de tipo dialer
        :param logs_llamadas_campana: queryset con los logs de las llamadas dialer
        recibidas
        :return: dicionario con los totales de cada estado de las llamadas recibidas
        """
        reporte = OrderedDict(
            # se cuentan todos los eventos DIAL con 'tipo_llamada' no manual
            [(_('Discadas'), 0),
             # se cuentan todos los eventos CONNECT con 'tipo_llamada' no manual
             (_('Conectadas al agente'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' no manual
             (_('Atendidas'), 0),
             # se cuentan todos los eventos EXITWITHTIMEOUT y ABANDON con 'tipo_llamada' no manual
             (_('Perdidas'), 0),
             # se cuentan todos los eventos DIAL con 'tipo_llamada' manual
             (_('Manuales'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' manual
             (_('Manuales atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión con 'tipo_llamada' manual
             (_('Manuales no atendidas'), 0)])
        logs_campana_agrupados_eventos = logs_llamadas_campana.values(
            'event', 'tipo_llamada').annotate(
            cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            tipo_llamada = evento_cantidad['tipo_llamada']
            cantidad = evento_cantidad['cantidad']
            if evento == 'DIAL' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Discadas')] += cantidad
            elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Manuales')] = cantidad
            elif evento == 'CONNECT' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Conectadas al agente')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Atendidas')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Manuales atendidas')] = cantidad
            elif (evento in ['ABANDON', 'EXITWITHTIMEOUT'] and
                  tipo_llamada != LlamadaLog.LLAMADA_MANUAL):
                reporte[_('Perdidas')] += cantidad
            elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
                  tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
                reporte[_('Manuales no atendidas')] += cantidad
        return reporte

    def _obtener_detalle_llamadas_manuales(self, logs_llamadas_campana):
        """
        Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
        campaña de tipo manual
        :param logs_llamadas_campana: queryset con los logs de las llamadas manual
        recibidas
        :return: dicionario con los totales de cada estado de las llamadas recibidas
        """
        reporte = OrderedDict(
            # se cuentan todos los eventos DIAL
            [(_('Discadas'), 0),
             # se cuentan todos los eventos ANSWER
             (_('Discadas atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión'
             (_('Discadas no atendidas'), 0)])
        logs_campana_agrupados_eventos = logs_llamadas_campana.values('event').annotate(
            cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            if evento == 'DIAL':
                reporte[_('Discadas')] = cantidad
            elif evento == 'ANSWER':
                reporte[_('Discadas atendidas')] = cantidad
            elif evento in LlamadaLog.EVENTOS_NO_CONEXION:
                reporte[_('Discadas no atendidas')] += cantidad
        return reporte

    def _obtener_detalle_llamadas_preview(self, logs_llamadas_campana):
        """
        Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
        campaña de tipo preview
        :param logs_llamadas_campana: queryset con los logs de las llamadas preview
        recibidas
        :return: dicionario con los totales de cada estado de las llamadas recibidas
        """
        reporte = OrderedDict(
            # se cuentan todos los eventos DIAL  con 'tipo_llamada' no manual
            [(_('Discadas'), 0),
             # se cuentan todos los eventos ANSWER  con 'tipo_llamada' no manual
             (_('Conectadas'), 0),
             # se cuentan todos los eventos 'no-conexión' con 'tipo_llamada' no manual
             (_('No conectadas'), 0),
             # se cuentan todos los eventos DIAL con 'tipo_llamada' manual
             (_('Manuales'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' manual
             (_('Manuales atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión con 'tipo_llamada' manual
             (_('Manuales no atendidas'), 0)])
        logs_campana_agrupados_eventos = logs_llamadas_campana.values(
            'event', 'tipo_llamada').annotate(cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            tipo_llamada = evento_cantidad['tipo_llamada']
            cantidad = evento_cantidad['cantidad']
            if evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Conectadas')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Manuales atendidas')] = cantidad
            elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
                  tipo_llamada != LlamadaLog.LLAMADA_MANUAL):
                reporte[_('No conectadas')] += cantidad
            elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
                  tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
                reporte[_('Manuales no atendidas')] += cantidad
            elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Manuales')] = cantidad
            elif evento == 'DIAL' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Discadas')] = cantidad
        return reporte

    def calcular_cantidad_llamadas(self, campana, fecha_desde, fecha_hasta):
        """
        Obtiene las cantidades toteles detalladas como resultado de las llamadas
        :param campana: campana la cuales se obtendran el detalle de la llamada
        :param fecha_desde: fecha desde la cual se obtendran las llamadas
        :param fecha_hasta: fecha hasta la cual se obtendran las llamadas
        :return: los eventos de llamadas con sus cantidades totales
        """
        fecha_desde = datetime_hora_minima_dia(fecha_desde)
        fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        logs_llamadas_campana = LlamadaLog.objects.filter(
            campana_id=campana.pk, time__range=(fecha_desde, fecha_hasta))

        if campana.type == Campana.TYPE_ENTRANTE:
            reporte = self._obtener_detalle_llamadas_entrantes(logs_llamadas_campana)
        elif campana.type == Campana.TYPE_DIALER:
            reporte = self._obtener_detalle_llamadas_dialer(logs_llamadas_campana)
        elif campana.type == Campana.TYPE_MANUAL:
            reporte = self._obtener_detalle_llamadas_manuales(logs_llamadas_campana)
        else:
            reporte = self._obtener_detalle_llamadas_preview(logs_llamadas_campana)
        return reporte

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta):
        fecha_desde = datetime_hora_minima_dia(fecha_desde)
        fecha_hasta = datetime_hora_maxima_dia(fecha_hasta)

        # obtener cantidad de calificaciones por campana
        calificaciones_nombre, calificaciones_cantidad, total_asignados = \
            self.obtener_cantidad_calificacion(campana, fecha_desde,
                                               fecha_hasta)

        # obtiene detalle de llamados no atendidos
        resultado_nombre, resultado_cantidad, total_no_atendidos = \
            self.obtener_cantidad_no_atendidos(campana, fecha_desde,
                                               fecha_hasta)

        # obtiene el total de calificaciones por agente
        (agentes_venta, total_calificados, total_ventas,
         calificaciones) = self.obtener_total_calificacion_agente(
             campana, fecha_desde, fecha_hasta)

        # obtiene las llamadas pendientes y realizadas por campana
        llamadas_pendientes, llamadas_realizadas, llamadas_recibidas = self.obtener_total_llamadas(
            campana)

        # obtiene las cantidades totales por evento de las llamadas
        reporte = self.calcular_cantidad_llamadas(campana, fecha_desde, fecha_hasta)
        cantidad_llamadas = (reporte.keys(), reporte.values())

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
            'llamadas_recibidas': llamadas_recibidas,
            'calificaciones': calificaciones,
            'cantidad_llamadas': cantidad_llamadas,
        }
        return dic_estadisticas

    def general_campana(self, campana, fecha_inferior, fecha_superior):
        estadisticas = self._calcular_estadisticas(campana, fecha_inferior, fecha_superior)

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
            'barra_campana_no_atendido': barra_campana_no_atendido,
            'dict_no_atendido_counter': zip(estadisticas['resultado_nombre'],
                                            estadisticas['resultado_cantidad']),
            'total_no_atendidos': estadisticas['total_no_atendidos'],
            'calificaciones': estadisticas['calificaciones'],
            'barra_campana_llamadas': barra_campana_llamadas,
            'dict_llamadas_counter': zip(estadisticas['cantidad_llamadas'][0],
                                         estadisticas['cantidad_llamadas'][1]),

        }
