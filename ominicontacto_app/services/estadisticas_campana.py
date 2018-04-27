# -*- coding: utf-8 -*-

"""
Servicio para generar reporte grafico de una campana
"""

import pygal
import datetime
import os

from collections import OrderedDict
from pygal.style import Style

from django.conf import settings
from django.db.models import Count
from django.utils.translation import ugettext as _

from ominicontacto_app.models import CalificacionCliente, Campana, OpcionCalificacion
from ominicontacto_app.services.campana_service import CampanaService
from reportes_app.models import LlamadaLog

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
            self, campana, fecha_desde, fecha_hasta, total_calificados):
        """
        Devuelve la cantidad de llamadas recibidas por agentes pero no calificadas por estos
        """
        total_llamadas_campanas_qs = LlamadaLog.objects.filter(
            time__range=(fecha_desde, fecha_hasta), campana_id=campana.pk,
            event__in=['CONNECT', 'ANSWER'])
        total_llamadas_campanas = total_llamadas_campanas_qs.count()
        return total_llamadas_campanas - total_calificados

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
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
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
            campana, fecha_desde, fecha_hasta, total_calificados)
        calificaciones_nombre.append(_("AGENTE NO CALIFICO"))
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
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)

        reporte = OrderedDict(
            # se cuentan todos los eventos NO_ANSWER
            [(_('No atendido'), 0),
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
             (_('Blacklist'), 0)])
        eventos_headers = {
            'NO_ANSWER': _('No atendido'),
            'CANCEL': _('Cancelado'),
            'AMD': _('Contestador detectado'),
            'BUSY': _('Ocupado'),
            'CHANUNAVAIL': _('Canales No disponibles'),
            'FAIL': _('Fallidas'),
            'OTHER': _('Otro'),
            'BLACKLIST': _('Blacklist')}
        llamadas_no_atendidas_campana = LlamadaLog.objects.values('event').annotate(
            cantidad=Count('event'))
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
        campana_service = CampanaService()
        dato_campana = campana_service.obtener_dato_campana_run(campana)
        llamadas_pendientes = 0
        if dato_campana and 'n_est_remaining_calls' in dato_campana.keys():
            llamadas_pendientes = dato_campana['n_est_remaining_calls']
        llamadas_realizadas = 0
        if dato_campana and 'n_calls_attempted' in dato_campana.keys():
            llamadas_realizadas = dato_campana['n_calls_attempted']
        return llamadas_pendientes, llamadas_realizadas

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
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        total_calificados = 0
        total_ventas = 0

        opciones_calificaciones = campana.opciones_calificacion.all()

        dict_calificaciones = OrderedDict({})
        # armo dict de las calificaciones e inicializandolo en 0
        for opcion_calificacion in opciones_calificaciones:
            dict_calificaciones.update({opcion_calificacion.nombre: 0})

        calificaciones_campana_qs = CalificacionCliente.objects.filter(
            opcion_calificacion__campana=campana)

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
        # se cuentan todos los eventos para cada caso
        reporte = OrderedDict(
            [(_('Recibidas'), 0),
             (_('Atendidas'), 0),
             (_('Expiradas'), 0),
             (_('Abandonadas'), 0),
             (_('Manuales'), 0),
             (_('Manuales atendidas'), 0)])
        eventos_headers = {
            'ENTERQUEUE': _('Recibidas'),
            'CONNECT': _('Atendidas'),
            'EXITWITHTIMEOUT': _('Expiradas'),
            'ABANDON': _('Abandonadas'),
            'DIAL': _('Manuales'),
            'ANSWER': _('Manuales atendidas')}
        eventos_no_connect = {
            'BUSY': True,
            'CANCEL': True,
            'CHANUNAVAIL': True,
            'NOANSWER': True}
        logs_campana_agrupados_eventos = logs_llamadas_campana.values('event').annotate(
            cantidad=Count('event'))
        manuales_no_atendidas = 0
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            evento_header = eventos_headers.get(evento, False)
            if evento_header:
                reporte[evento_header] = cantidad
            elif not evento_header and eventos_no_connect(evento, False):
                manuales_no_atendidas += cantidad
        reporte[_('Manuales no atendidas')] = manuales_no_atendidas

        return reporte.keys(), reporte.values()

    def _obtener_detalle_llamadas_dialer(self, logs_llamadas_campana):
        reporte = OrderedDict(
            # se cuentan todos los eventos DIAL
            [(_('Discadas'), 0),
             # se cuentan todos los eventos CONNECT
             (_('Conectadas al agente'), 0),
             # se cuentan todos los eventos ANSWER
             (_('Atendidas'), 0),
             # se cuentan todos los eventos EXITWITHTIMEOUT y ABANDON
             (_('Perdidas'), 0),
             # se cuentan todos los eventos DIAL con 'tipo_llamada' manual
             (_('Manuales'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' manual
             (_('Manuales atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión con 'tipo_llamada' manual
             (_('Manuales no atendidas'), 0)])
        eventos_no_connect = {
            'BUSY': True,
            'CANCEL': True,
            'CHANUNAVAIL': True,
            'NOANSWER': True}
        logs_campana_agrupados_eventos = logs_llamadas_campana.values(
            'event', 'tipo_llamada').annotate(
            cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            tipo_llamada = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            if evento == 'DIAL' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Discadas')] += cantidad
            elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Discadas')] += cantidad
                reporte[_('Manuales')] = cantidad
            elif evento == 'CONNECT':
                reporte[_('Conectadas al agente')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Atendidas')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Atendidas')] += cantidad
                reporte[_('Manuales atendidas')] = cantidad
            elif evento in ['ANSWER', 'EXITWITHTIMEOUT']:
                reporte[_('Perdidas')] += cantidad
            elif (eventos_no_connect.get(evento, False) and
                  tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
                reporte[_('Manuales no atendidas')] += cantidad
        return reporte.keys(), reporte.values()

    def _obtener_detalle_llamadas_manuales(self, logs_llamadas_campana):
        reporte = OrderedDict(
            # se cuentan todos los eventos DIAL
            [(_('Discadas'), 0),
             # se cuentan todos los eventos ANSWER
             (_('Discadas atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión'
             (_('Discadas no atendidas'), 0)])
        eventos_no_connect = {
            'BUSY': True,
            'CANCEL': True,
            'CHANUNAVAIL': True,
            'NOANSWER': True}
        logs_campana_agrupados_eventos = logs_llamadas_campana.values('event').annotate(
            cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            if evento == 'DIAL':
                reporte[_('Discadas')] = cantidad
            elif evento == 'ANSWER':
                reporte[_('Discadas atendidas')] = cantidad
            elif eventos_no_connect.get(evento, False):
                reporte[_('Discadas no atendidas')] = cantidad
        return reporte.keys(), reporte.values()

    def _obtener_detalle_llamadas_preview(self, logs_llamadas_campana):
        reporte = OrderedDict(
            # se cuentan todos los eventos ANSWER
            [(_('Conectadas'), 0),
             # se cuentan todos los eventos 'no-conexión'
             (_('No conectadas'), 0),
             # se cuentan todos los eventos DIAL con 'tipo_llamada' manual
             (_('Manuales'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' manual
             (_('Manuales atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión con 'tipo_llamada' manual
             (_('Manuales no atendidas'), 0)])
        eventos_no_connect = {
            'BUSY': True,
            'CANCEL': True,
            'CHANUNAVAIL': True,
            'NOANSWER': True}
        logs_campana_agrupados_eventos = logs_llamadas_campana.values(
            'event', 'tipo_llamada').annotate(cantidad=Count('pk'))
        for evento_cantidad in logs_campana_agrupados_eventos:
            evento = evento_cantidad['event']
            tipo_llamada = evento_cantidad['event']
            cantidad = evento_cantidad['cantidad']
            if evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Conectadas')] += cantidad
            elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Conectadas')] += cantidad
                reporte[_('Manuales atendidas ')] = cantidad
            elif (eventos_no_connect.get(evento, False) and
                  tipo_llamada != LlamadaLog.LLAMADA_MANUAL):
                reporte[_('No conectadas')] += cantidad
            elif (eventos_no_connect.get(evento, False) and
                  tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
                reporte[_('No conectadas')] += cantidad
                reporte[_('Manuales no atendidas')] += cantidad
            elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
                reporte[_('Manuales')] = cantidad
        return reporte.keys(), reporte.values()

    def calcular_cantidad_llamadas(self, campana, fecha_inferior, fecha_superior):
        """
        Obtiene las cantidades toteles detalladas como resultado de las llamadas
        :param campana: campana la cuales se obtendran el detalle de la llamada
        :param fecha_inferior: fecha desde la cual se obtendran las llamadas
        :param fecha_superior: fecha hasta la cual se obtendran las llamadas
        :return: los eventos de llamadas con sus cantidades totales
        """
        fecha_desde = datetime.datetime.combine(fecha_inferior, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_superior, datetime.time.max)
        logs_llamadas_campana = LlamadaLog.objects.filter(
            campana_id=campana.pk, time__range=(fecha_desde, fecha_hasta))

        if campana.type == Campana.TYPE_ENTRANTE:
            nombres_cantidades, cantidad_campana = self._obtener_detalle_llamadas_entrantes(
                logs_llamadas_campana)
        elif campana.type == Campana.TYPE_DIALER:
            nombres_cantidades, cantidad_campana = self._obtener_detalle_llamadas_dialer(
                logs_llamadas_campana)
        elif campana.type == Campana.TYPE_MANUAL:
            nombres_cantidades, cantidad_campana = self._obtener_detalle_llamadas_manuales(
                logs_llamadas_campana)
        else:
            nombres_cantidades, cantidad_campana = self._obtener_detalle_llamadas_preview(
                logs_llamadas_campana)
        return nombres_cantidades, cantidad_campana

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta):
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
        if campana.type == Campana.TYPE_DIALER:
            llamadas_pendientes, llamadas_realizadas = self.obtener_total_llamadas(
                campana)
        else:
            llamadas_pendientes, llamadas_realizadas = (None, None)

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
            'resultado_nombre': resultado_nombre,
            'resultado_cantidad': resultado_cantidad,
            'total_no_atendidos': total_no_atendidos,
            'llamadas_pendientes': llamadas_pendientes,
            'llamadas_realizadas': llamadas_realizadas,
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
