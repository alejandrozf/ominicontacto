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

from __future__ import unicode_literals

import os

import pygal

from collections import OrderedDict
from pygal.style import LightGreenStyle, DefaultStyle

from django.conf import settings

from django.utils.translation import ugettext as _

from ominicontacto_app.models import (AgenteEnContacto, CalificacionCliente, Campana,
                                      AgenteProfile, HistoricalCalificacionCliente,
                                      RespuestaFormularioGestion)
from ominicontacto_app.services.campana_service import CampanaService
from reportes_app.models import LlamadaLog

from utiles_globales import adicionar_render_unicode

import logging as _logging

logger = _logging.getLogger(__name__)

NO_CONECTADO_DESCRIPCION = {
    'NOANSWER': _('Cliente no atiende'),
    'CANCEL': _('Se corta antes que atienda el cliente'),
    'BUSY': _('Ocupado'),
    'CHANUNAVAIL': _('Canales Saturados'),
    'OTHER': _('Motivo no especificado'),
    'FAIL': _('Fallo'),
    'AMD': _('Contestador'),
    'BLACKLIST': _('Blacklist'),
    'ABANDON': _('Abandonada por cliente'),
    'EXITWITHTIMEOUT': _('Expirada'),
    'CONGESTION': _('Canal congestionado'),
    'NONDIALPLAN': _('Problema de enrutamiento'),
    'ABANDONWEL': _('Abandonadas durante anuncio'),
}


class EstadisticasBaseCampana:

    def _obtener_logs_de_llamadas(self):
        logs_llamadas = LlamadaLog.objects.filter(
            campana_id=self.campana.pk, time__range=(self.fecha_desde, self.fecha_hasta)).order_by(
                '-time')
        return logs_llamadas

    def _inicializar_valores_estadisticas(self):
        self.calificaciones_finales_dict = {}

        self.calificaciones_historicas_dict = {}

        self.agentes_dict = {}

        # con el id de la calificacion asociada como clave
        self.respuestas_formulario_gestion_dict = {}

        self.bd_contacto = self.campana.bd_contacto
        self.opciones_calificacion_campana = {opcion.pk: opcion for opcion in
                                              self.campana.opciones_calificacion.all(
                                              ).select_related('formulario').prefetch_related(
                                                  'formulario__campos')}
        self.bd_metadata = self.bd_contacto.get_metadata()
        self._inicializar_valores_calificaciones()
        self._inicializar_respuestas_formulario_gestion()
        self._inicializar_valores_agentes()

    def _inicializar_valores_calificaciones(self):
        calificacion_finales_qs = CalificacionCliente.objects.filter(
            opcion_calificacion__campana=self.campana, fecha__range=(
                self.fecha_desde, self.fecha_hasta)).select_related(
                    'agente', 'agente__user', 'contacto', 'contacto__bd_contacto',
                    'opcion_calificacion')

        for calificacion in calificacion_finales_qs:
            self.calificaciones_finales_dict[calificacion.callid] = calificacion

        calificaciones_historicas_qs = HistoricalCalificacionCliente.objects.filter(
            history_date__range=(self.fecha_desde, self.fecha_hasta),
            opcion_calificacion__campana=self.campana).select_related(
                'agente', 'agente__user', 'contacto', 'contacto__bd_contacto',
                'opcion_calificacion').order_by()

        self.calificaciones_historicas_dict = {calificacion.callid: calificacion for calificacion
                                               in calificaciones_historicas_qs}

    def _inicializar_respuestas_formulario_gestion(self):
        respuestas_formulario_gestion_qs = RespuestaFormularioGestion.objects.filter(
            calificacion__callid__in=self.calificaciones_finales_dict.keys()).select_related(
                'calificacion')
        for respuesta in respuestas_formulario_gestion_qs:
            self.respuestas_formulario_gestion_dict[respuesta.calificacion.pk] = respuesta

    def _inicializar_valores_agentes(self):
        # se crean un diccionario de los agentes de la campaña
        # para evitar accesos a la BD para recuperarlos desde los logs
        agentes_campana = AgenteProfile.objects.obtener_agentes_campana(
            self.campana).select_related('user')
        for agente in agentes_campana:
            self.agentes_dict[agente.pk] = agente


class ReporteDetalleLlamadasPreview:
    """
    Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
    campaña de tipo preview
    :param logs_llamadas_campana: queryset con los logs de las llamadas preview
    recibidas
    :return: dicionario con los totales de cada estado de las llamadas recibidas
    """

    def __init__(self):
        self.reporte = OrderedDict(
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

    def _calcular_detalle(self, evento=None, tipo_llamada=None):
        if evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Conectadas')] += 1
        elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Manuales atendidas')] += 1
        elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
              tipo_llamada != LlamadaLog.LLAMADA_MANUAL):
            self.reporte[_('No conectadas')] += 1
        elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
              tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
            self.reporte[_('Manuales no atendidas')] += 1
        elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Manuales')] += 1
        elif evento == 'DIAL' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Discadas')] += 1


class ReporteDetalleLlamadasManual:
    """
    Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
    campaña de tipo manual
    :param logs_llamadas_campana: queryset con los logs de las llamadas manual
    recibidas
    :return: dicionario con los totales de cada estado de las llamadas recibidas
    """

    def __init__(self):
        self.reporte = OrderedDict(
            # se cuentan todos los eventos DIAL
            [(_('Discadas'), 0),
             # se cuentan todos los eventos ANSWER
             (_('Discadas atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión'
             (_('Discadas no atendidas'), 0)])

    def _calcular_detalle(self, evento=None, tipo_llamada=None):
        if evento == 'DIAL':
            self.reporte[_('Discadas')] += 1
        elif evento == 'ANSWER':
            self.reporte[_('Discadas atendidas')] += 1
        elif evento in LlamadaLog.EVENTOS_NO_CONEXION:
            self.reporte[_('Discadas no atendidas')] += 1


class ReporteDetalleLlamadasDialer:
    """
    Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
    campaña de tipo dialer
    :param logs_llamadas_campana: queryset con los logs de las llamadas dialer
    recibidas
    :return: dicionario con los totales de cada estado de las llamadas recibidas
    """

    def __init__(self):
        self.reporte = OrderedDict(
            # se cuentan todos los eventos DIAL con 'tipo_llamada' no manual
            [(_('Discadas'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' no manual
             (_('Atendidas'), 0),
             # se cuentan todos los eventos CONNECT con 'tipo_llamada' no manual
             (_('Conectadas al agente'), 0),
             # se cuentan todos los eventos EXITWITHTIMEOUT y ABANDON con 'tipo_llamada' no manual
             (_('Perdidas'), 0),
             # se cuentan todos los eventos AMD
             (_('Contestador detectado'), 0),
             # se cuentan todos los eventos DIAL con 'tipo_llamada' manual
             (_('Manuales'), 0),
             # se cuentan todos los eventos ANSWER con 'tipo_llamada' manual
             (_('Manuales atendidas'), 0),
             # se cuentan todos los eventos de 'no-conexión con 'tipo_llamada' manual
             (_('Manuales no atendidas'), 0)])

    def _calcular_detalle(self, evento=None, tipo_llamada=None):
        if evento == 'DIAL' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Discadas')] += 1
        elif evento == 'DIAL' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Manuales')] += 1
        elif evento == 'CONNECT' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Conectadas al agente')] += 1
        elif evento == 'ANSWER' and tipo_llamada != LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Atendidas')] += 1
        elif evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL:
            self.reporte[_('Manuales atendidas')] += 1
        elif evento == 'AMD':
            self.reporte[_('Contestador detectado')] += 1
        elif (evento in ['ABANDON', 'EXITWITHTIMEOUT'] and
              tipo_llamada != LlamadaLog.LLAMADA_MANUAL):
            self.reporte[_('Perdidas')] += 1
        elif ((evento in LlamadaLog.EVENTOS_NO_CONEXION) and
              tipo_llamada == LlamadaLog.LLAMADA_MANUAL):
            self.reporte[_('Manuales no atendidas')] += 1


class ReporteDetalleLlamadasEntrantes:
    """
    Devuelve los datos para tabla con el detalle de las llamadas recibidas para una
    campaña de tipo entrante
    :param logs_llamadas_campana: queryset con los logs de las llamadas entrantes
    recibidas
    :return: dicionario con los totales de cada estado de las llamadas recibidas
    """

    def __init__(self):
        # se cuentan todos los eventos para cada caso
        self.reporte = OrderedDict(
            [(_('Recibidas'), 0),
             (_('Transferencias recibidas'), 0),
             (_('Atendidas'), 0),
             (_('Expiradas'), 0),
             (_('Abandonadas'), 0),
             (_('Abandonadas durante anuncio'), 0),
             (_('Manuales'), 0),
             (_('Manuales atendidas'), 0),
             (_('Manuales no atendidas'), 0)])

        self.eventos_headers = {
            'ENTERQUEUE': _('Recibidas'),
            'ENTERQUEUE-TRANSFER': _('Transferencias recibidas'),
            'CONNECT': _('Atendidas'),
            'EXITWITHTIMEOUT': _('Expiradas'),
            'ABANDON': _('Abandonadas'),
            'ABANDONWEL': _('Abandonadas durante anuncio'),
            'DIAL': _('Manuales'),
            'ANSWER': _('Manuales atendidas')}

    def _calcular_detalle(self, evento=None, tipo_llamada=None):
        evento_header = self.eventos_headers.get(evento, False)
        if evento_header:
            self.reporte[evento_header] += 1
        elif not evento_header and (evento in LlamadaLog.EVENTOS_NO_CONEXION):
            self.reporte[_('Manuales no atendidas')] += 1
        if evento == 'ABANDONWEL':
            self.reporte[_('Recibidas')] += 1


class ReporteNoAtendidos:
    def __init__(self):
        self.reporte = OrderedDict(
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
             # se cuentan todos los eventos ABANDONWEL
             (_('Abandonadas durante anuncio'), 0),
             # se cuentan todos los eventos EXITWITHTIMEOUT
             (_('Expiradas'), 0),
             # se cuentan todos los eventos CONGESTION
             (_('Canal congestionado'), 0),
             # se cuentan todos los eventos NONDIALPLAN
             (_('Problema de enrutamiento'), 0)]
        )
        # LlamadaLog.EVENTOS_NO_CONEXION
        self.eventos_headers = {
            'NOANSWER': _('Cliente no atiende'),
            'CANCEL': _('Cancelado'),
            'AMD': _('Contestador detectado'),
            'BUSY': _('Ocupado'),
            'CHANUNAVAIL': _('Canales No disponibles'),
            'FAIL': _('Fallidas'),
            'OTHER': _('Otro'),
            'BLACKLIST': _('Blacklist'),
            'ABANDON': _('Abandonadas por el cliente'),
            'ABANDONWEL': _('Abandonadas durante anuncio'),
            'EXITWITHTIMEOUT': _('Expiradas'),
            'CONGESTION': _('Canal congestionado'),
            'NONDIALPLAN': _('Problema de enrutamiento'),
        }

        self.total_no_atendidos = 0


class ReporteTotalesCalificacionesAgentes:
    total_calificados = 0
    total_ventas = 0

    def __init__(self, opciones_calificaciones):
        self.dict_calificaciones = OrderedDict({})
        self.dict_agentes = {}
        for opcion_calificacion in opciones_calificaciones.values():
            self.dict_calificaciones[opcion_calificacion.nombre] = 0


class ReporteTotalesCalificaciones:

    dict_calificaciones = OrderedDict({})

    def __init__(self, dict_calificaciones):
        self.dict_calificaciones_atendidas = dict_calificaciones.copy()
        self.dict_calificaciones_no_atendidas = dict_calificaciones.copy()


class ReporteTotalesLlamadas:

    _llamadas_pendientes = 0
    llamadas_realizadas = 0
    _llamadas_recibidas = 0
    _llamadas_conectadas = 0
    _tiempo_acumulado_espera = 0
    _llamadas_abandonadas = 0
    _tiempo_acumulado_abandono = 0

    def __init__(self, campana):
        self.campana = campana

    @property
    def llamadas_recibidas(self):
        if not self.campana.es_entrante:
            return None
        return self._llamadas_recibidas

    @property
    def llamadas_pendientes(self):
        if not self.campana.es_preview:
            llamadas_pendientes_extra = 0
        else:
            llamadas_pendientes_extra = AgenteEnContacto.objects.filter(
                estado=AgenteEnContacto.ESTADO_INICIAL, campana_id=self.campana.pk,
                es_originario=True).count()
        if self.campana.es_dialer:
            campana_service = CampanaService()
            dato_campana = campana_service.obtener_dato_campana_run(self.campana)
            llamadas_pendientes_extra = 0
            if dato_campana:
                llamadas_pendientes_extra = dato_campana.get(
                    'n_est_remaining_calls', 0)
        return self._llamadas_pendientes + llamadas_pendientes_extra

    @property
    def tiempo_promedio_espera(self):
        if not self.campana.es_entrante:
            return None
        if self._llamadas_conectadas == 0:
            return 0
        return self._tiempo_acumulado_espera / self._llamadas_conectadas

    @property
    def tiempo_promedio_abandono(self):
        if not self.campana.es_entrante:
            return None
        if self._llamadas_abandonadas == 0:
            return 0
        return self._tiempo_acumulado_abandono / self._llamadas_abandonadas


class EstadisticasService(EstadisticasBaseCampana):

    def __init__(self, campana, fecha_desde, fecha_hasta):
        self.campana = campana
        self.bd_contacto = campana.bd_contacto
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta

        self.tipo_campana = campana.type

        self._inicializar_valores_estadisticas()

        # valores del reporte

        self.reporte_no_atendidos = ReporteNoAtendidos()
        self.reporte_calificaciones_agentes = ReporteTotalesCalificacionesAgentes(
            self.opciones_calificacion_campana)
        self.reporte_calificaciones = ReporteTotalesCalificaciones(
            self.reporte_calificaciones_agentes.dict_calificaciones)
        self.reporte_totales_llamadas = ReporteTotalesLlamadas(self.campana)
        self.llamadas_atendidas_sin_calificacion = 0

        if self.campana.es_dialer:
            self.reporte_detalle_llamadas = ReporteDetalleLlamadasDialer()
        elif self.campana.es_entrante:
            self.reporte_detalle_llamadas = ReporteDetalleLlamadasEntrantes()
        elif self.campana._es_manual:
            self.reporte_detalle_llamadas = ReporteDetalleLlamadasManual()
        else:
            # self.campana.es_preview
            self.reporte_detalle_llamadas = ReporteDetalleLlamadasPreview()

    def _obtener_llamadas_atendidas_sin_calificacion(
            self, evento, agente_id, calificacion_final, calificacion_historica):
        # obtener_llamadas_atendidas_sin_calificacion(log_llamada)
        if not calificacion_final and not calificacion_historica:
            # Si es dialer, una misma llamada tiene ANSWER y CONNECT por lo que estaba
            # contabilizando doble
            if evento in LlamadaLog.EVENTOS_INICIO_CONEXION_AGENTE and agente_id != -1:
                # TODO: analizar consecuencias de que los eventos obtenidos
                # cada llamada son los ultimos de cada llamada
                # TODO: ver que pasaría con 'BT-ANSWER', 'CT-ACCEPT'
                self.llamadas_atendidas_sin_calificacion += 1

    def _obtener_total_llamadas(
            self, evento, es_campana_entrante, calificacion_final, callid,
            callids_analizados, bridge_wait_time):
        if calificacion_final and calificacion_final.opcion_calificacion.es_agenda() and \
           callid not in callids_analizados:
            self.reporte_totales_llamadas._llamadas_pendientes += 1
        if evento == 'DIAL':
            self.reporte_totales_llamadas.llamadas_realizadas += 1
        if es_campana_entrante:
            if evento in ['ENTERQUEUE', 'ABANDONWEL', 'ENTERQUEUE-TRANSFER']:
                self.reporte_totales_llamadas._llamadas_recibidas += 1
                if evento == 'ABANDONWEL':
                    self.reporte_totales_llamadas._llamadas_abandonadas += 1
                    self.reporte_totales_llamadas._tiempo_acumulado_abandono += bridge_wait_time
            elif evento == 'ABANDON':
                self.reporte_totales_llamadas._llamadas_abandonadas += 1
                self.reporte_totales_llamadas._tiempo_acumulado_abandono += bridge_wait_time
            elif evento == 'CONNECT':
                self.reporte_totales_llamadas._llamadas_conectadas += 1
                self.reporte_totales_llamadas._tiempo_acumulado_espera += bridge_wait_time

    def _obtener_reporte_no_atendidos(self, log_llamada, evento):
        # obtener_cantidad_no_atendidos(log_llamada) + datos_csv
        if evento in self.reporte_no_atendidos.eventos_headers.keys():
            evento_header = self.reporte_no_atendidos.eventos_headers[evento]
            self.reporte_no_atendidos.reporte[evento_header] += 1
            self.reporte_no_atendidos.total_no_atendidos += 1

    def _obtener_cantidad_calificacion(
            self, es_campana_entrante, calificacion_historica, calificacion_final,
            tipo_llamada, evento):
        if es_campana_entrante and calificacion_historica:
            nombre_opcion = calificacion_historica.opcion_calificacion.nombre
            # agrupamos las calificaciones finales que hayan sido conectadas con el agente
            if (evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL) or \
               evento == 'CONNECT':
                # atendidas en campaña entrante
                self.reporte_calificaciones.dict_calificaciones_atendidas[nombre_opcion] += 1
            elif evento in LlamadaLog.EVENTOS_NO_CONEXION:   # TODO: que busque en set fijo
                # no atendidas en campaña entrante
                self.reporte_calificaciones.dict_calificaciones_no_atendidas[nombre_opcion] += 1
        elif calificacion_final:
            nombre_opcion = calificacion_final.opcion_calificacion.nombre
            if (evento == 'CONNECT' or
                (evento == 'ANSWER' and tipo_llamada == LlamadaLog.LLAMADA_MANUAL
                 and self.campana.es_dialer) or
                    (evento == 'ANSWER' and (self.campana._es_manual
                                             or self.campana.es_preview))):
                # atendidas en campaña no entrante
                self.reporte_calificaciones.dict_calificaciones_atendidas[nombre_opcion] += 1
            elif evento in LlamadaLog.EVENTOS_NO_CONEXION:  # TODO: que busque en set fijo
                # no atendidas en campaña no entrante
                self.reporte_calificaciones.dict_calificaciones_no_atendidas[nombre_opcion] += 1

    def _obtener_total_calificacion_agente_datos_calificaciones(
            self, es_campana_entrante, calificacion_historica, calificacion_final, log_llamada,
            calificaciones_analizadas):
        if es_campana_entrante:
            calificacion = calificacion_historica
        else:
            calificacion = calificacion_final
        if calificacion and (calificacion.pk not in calificaciones_analizadas):
            opcion_calificacion = calificacion.opcion_calificacion
            es_gestion = int(opcion_calificacion.es_gestion())
            self.reporte_calificaciones_agentes.total_calificados += 1
            if es_gestion:
                self.reporte_calificaciones_agentes.total_ventas += 1
            agente = calificacion.agente
            agente_id = agente.pk
            if not self.reporte_calificaciones_agentes.dict_agentes.get(agente_id, False):
                dict_calificaciones = self.reporte_calificaciones_agentes.dict_calificaciones
                self.reporte_calificaciones_agentes.dict_agentes[agente_id] = OrderedDict({
                    'nombre': agente.user.get_full_name(),
                    'totales_calificaciones': dict_calificaciones.copy(),
                    'total_calificados': 1,
                    'total_gestionados': es_gestion,
                })
            else:
                self.reporte_calificaciones_agentes.dict_agentes[
                    agente_id]['total_calificados'] += 1
                self.reporte_calificaciones_agentes.dict_agentes[
                    agente_id]['total_gestionados'] += es_gestion
            self.reporte_calificaciones_agentes.dict_agentes[
                agente_id]['totales_calificaciones'][
                    opcion_calificacion.nombre] += 1
            calificaciones_analizadas.add(calificacion.pk)

    def calcular_estadisticas_totales(self):
        calificaciones_analizadas = set()
        callids_analizados = set()
        logs_llamadas = self._obtener_logs_de_llamadas()
        for log_llamada in logs_llamadas:
            evento = log_llamada.event
            callid = log_llamada.callid
            agente_id = log_llamada.agente_id
            tipo_llamada = log_llamada.tipo_llamada
            bridge_wait_time = log_llamada.bridge_wait_time
            es_campana_entrante = self.campana.es_entrante
            calificacion_historica = self.calificaciones_historicas_dict.get(callid, False)
            calificacion_final = self.calificaciones_finales_dict.get(callid, False)
            self._obtener_llamadas_atendidas_sin_calificacion(
                evento, agente_id, calificacion_final, calificacion_historica)
            # obtener_detalle_llamadas(log_llamada)
            self.reporte_detalle_llamadas._calcular_detalle(evento, tipo_llamada)
            # obtener_cantidad_no_atendidos(log_llamada) + datos_csv
            self._obtener_reporte_no_atendidos(log_llamada, evento)
            # obtener_total_llamadas (log_llamada)
            self._obtener_total_llamadas(
                evento, es_campana_entrante, calificacion_final, callid, callids_analizados,
                bridge_wait_time)
            # obtener_total_calificacion_agente(log_llamada) y reporte csv_calificados
            self._obtener_total_calificacion_agente_datos_calificaciones(
                es_campana_entrante, calificacion_historica, calificacion_final, log_llamada,
                calificaciones_analizadas)
            # obtener_cantidad_calificacion(log_llamada)
            self._obtener_cantidad_calificacion(
                es_campana_entrante, calificacion_historica, calificacion_final, tipo_llamada,
                evento)
            callids_analizados.add(callid)

    def _crear_serie_con_color(self, campana, cantidad_llamadas):
        """ crea la lista del diccionario con los colores de la serie"""

        serie = []

        if campana.type == Campana.TYPE_ENTRANTE:
            serie = [
                {'value': cantidad_llamadas[1][0], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][1], 'color': 'green'},
                {'value': cantidad_llamadas[1][2], 'color': 'green'},
                {'value': cantidad_llamadas[1][3], 'color': 'red'},
                {'value': cantidad_llamadas[1][4], 'color': 'red'},
                {'value': cantidad_llamadas[1][5], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][6], 'color': 'green'},
            ]
        elif campana.type == Campana.TYPE_DIALER:
            serie = [
                {'value': cantidad_llamadas[1][0], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][1], 'color': 'green'},
                {'value': cantidad_llamadas[1][2], 'color': 'green'},
                {'value': cantidad_llamadas[1][3], 'color': 'red'},
                {'value': cantidad_llamadas[1][4], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][5], 'color': 'green'},
                {'value': cantidad_llamadas[1][6], 'color': 'red'},
            ]
        elif campana.type == Campana.TYPE_MANUAL:
            serie = [
                {'value': cantidad_llamadas[1][0], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][1], 'color': 'green'},
                {'value': cantidad_llamadas[1][2], 'color': 'red'},
            ]
        else:
            serie = [
                {'value': cantidad_llamadas[1][0], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][1], 'color': 'green'},
                {'value': cantidad_llamadas[1][2], 'color': 'red'},
                {'value': cantidad_llamadas[1][3], 'color': 'yellow'},
                {'value': cantidad_llamadas[1][4], 'color': 'green'},
                {'value': cantidad_llamadas[1][5], 'color': 'red'},

            ]
        return serie

    def _calcular_estadisticas(self, campana, fecha_desde, fecha_hasta):

        self.calcular_estadisticas_totales()

        # obtener cantidad de calificaciones por campana
        reporte_atendidas_dict = self.reporte_calificaciones.dict_calificaciones_atendidas
        header_no_calificadas = _('Llamadas Atendidas sin calificación')
        reporte_atendidas_dict[header_no_calificadas] = self.llamadas_atendidas_sin_calificacion
        calificaciones_nombre = reporte_atendidas_dict.keys()
        calificaciones_cantidad = reporte_atendidas_dict.values()
        total_asignados = sum(reporte_atendidas_dict.values())
        # obtiene detalle de llamados no atendidos
        resultado_nombre = self.reporte_no_atendidos.reporte.keys()
        resultado_cantidad = self.reporte_no_atendidos.reporte.values()
        total_no_atendidos = self.reporte_no_atendidos.total_no_atendidos

        # obtiene el total de calificaciones por agente
        agentes_venta = self.reporte_calificaciones_agentes.dict_agentes
        total_calificados = self.reporte_calificaciones_agentes.total_calificados
        total_ventas = self.reporte_calificaciones_agentes.total_ventas
        calificaciones = tuple(self.reporte_calificaciones_agentes.dict_calificaciones.keys())

        # obtiene las llamadas pendientes y realizadas por campana
        llamadas_pendientes = self.reporte_totales_llamadas.llamadas_pendientes
        llamadas_realizadas = self.reporte_totales_llamadas.llamadas_realizadas
        llamadas_recibidas = self.reporte_totales_llamadas.llamadas_recibidas
        tiempo_promedio_espera = self.reporte_totales_llamadas.tiempo_promedio_espera
        tiempo_promedio_abandono = self.reporte_totales_llamadas.tiempo_promedio_abandono

        # obtiene las cantidades totales por evento de las llamadas
        reporte = self.reporte_detalle_llamadas.reporte
        cantidad_llamadas = (list(reporte.keys()), list(reporte.values()))

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
            'tiempo_promedio_espera': tiempo_promedio_espera,
            'tiempo_promedio_abandono': tiempo_promedio_abandono,
            'calificaciones': calificaciones,
            'cantidad_llamadas': cantidad_llamadas,
        }
        return dic_estadisticas

    def general_campana(self):
        estadisticas = self._calcular_estadisticas(self.campana, self.fecha_desde, self.fecha_hasta)
        if estadisticas:
            logger.info(_("Generando grafico calificaciones de campana por cliente "))

        # Barra: Cantidad de calificacion de cliente
        barra_campana_calificacion = pygal.Bar(  # @UndefinedVariable
            show_legend=False, style=LightGreenStyle)
        barra_campana_calificacion.title = _('Calificaciones de Clientes Contactados ')

        barra_campana_calificacion.x_labels = \
            estadisticas['calificaciones_nombre']
        barra_campana_calificacion.add('cantidad',
                                       estadisticas['calificaciones_cantidad'])
        barra_campana_calificacion.render_to_png(os.path.join(
            settings.MEDIA_ROOT,
            "reporte_campana", "barra_campana_calificacion.png"))

        barra_campana_calificacion = adicionar_render_unicode(barra_campana_calificacion)

        # Barra: Total de llamados no atendidos en cada intento por campana.
        barra_campana_no_atendido = pygal.Bar(  # @UndefinedVariable
            show_legend=False,
            style=DefaultStyle(colors=('#b93229',)))
        barra_campana_no_atendido.title = _('Cantidad de llamadas no atendidos ')

        barra_campana_no_atendido.x_labels = \
            estadisticas['resultado_nombre']
        barra_campana_no_atendido.add('cantidad',
                                      estadisticas['resultado_cantidad'])
        barra_campana_no_atendido.render_to_png(
            os.path.join(settings.MEDIA_ROOT,
                         "reporte_campana", "barra_campana_no_atendido.png"))

        barra_campana_no_atendido = adicionar_render_unicode(barra_campana_no_atendido)

        # Barra: Detalles de llamadas por evento de llamada.
        barra_campana_llamadas = pygal.Bar(show_legend=False)
        barra_campana_llamadas.title = _('Detalles de llamadas ')

        barra_campana_llamadas.x_labels = \
            estadisticas['cantidad_llamadas'][0]
        barra_campana_llamadas.add('cantidad', self._crear_serie_con_color(
            self.campana, estadisticas['cantidad_llamadas']))
        barra_campana_llamadas = adicionar_render_unicode(barra_campana_llamadas)

        return {
            'estadisticas': estadisticas,
            'barra_campana_calificacion': barra_campana_calificacion,
            'dict_campana_counter': list(zip(estadisticas['calificaciones_nombre'],
                                             estadisticas['calificaciones_cantidad'])),
            'total_asignados': estadisticas['total_asignados'],
            'agentes_venta': estadisticas['agentes_venta'],
            'total_calificados': estadisticas['total_calificados'],
            'total_ventas': estadisticas['total_ventas'],
            'barra_campana_no_atendido': barra_campana_no_atendido,
            'dict_no_atendido_counter': list(zip(estadisticas['resultado_nombre'],
                                                 estadisticas['resultado_cantidad'])),
            'total_no_atendidos': estadisticas['total_no_atendidos'],
            'calificaciones': estadisticas['calificaciones'],
            'barra_campana_llamadas': barra_campana_llamadas,
            'dict_llamadas_counter': list(zip(estadisticas['cantidad_llamadas'][0],
                                              estadisticas['cantidad_llamadas'][1])),
        }
