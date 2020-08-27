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

import json
import os

import pygal

from collections import OrderedDict
from pygal.style import LightGreenStyle, DefaultStyle

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.timezone import localtime, timedelta

from ominicontacto_app.utiles import (datetime_hora_minima_dia_utc,
                                      datetime_hora_maxima_dia_utc)
from ominicontacto_app.models import (AgenteEnContacto, CalificacionCliente, Campana,
                                      Contacto, AgenteProfile, HistoricalCalificacionCliente,
                                      OpcionCalificacion, RespuestaFormularioGestion)
from ominicontacto_app.services.campana_service import CampanaService
from reportes_app.models import LlamadaLog
from reportes_app.reportes.reporte_llamados_contactados_csv import ExportacionCampanaCSV

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


class ReporteCSV:

    def _obtener_datos_contacto(self, contacto_id, campos_contacto, contactos_dict):
        telefono_contacto = ''
        contacto = contactos_dict.get(contacto_id, -1)
        if contacto != -1:
            telefono_contacto = contacto.telefono
            return json.loads(contacto.datos), telefono_contacto
        return [""] * len(campos_contacto), telefono_contacto


class ReporteNoAtendidosCSV(ReporteCSV):
    def __init__(self, bd_metadata):
        self.bd_metadata = bd_metadata
        self.campos_contacto = self.bd_metadata.nombres_de_columnas_de_datos
        self.datos = []
        self._escribir_encabezado()

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Telefono de llamada"))
        encabezado.append(self.bd_metadata.nombre_campo_telefono)
        encabezado.extend(self.campos_contacto)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Agente"))
        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_log(self, log_no_contactado, contactos_dict, agentes_dict):
        lista_opciones = []
        # --- Buscamos datos
        log_no_contactado_fecha_local = localtime(log_no_contactado.time)
        estado = NO_CONECTADO_DESCRIPCION.get(log_no_contactado.event, "")
        lista_opciones.append(log_no_contactado.numero_marcado)
        contacto_id = log_no_contactado.contacto_id
        datos_contacto, telefono_contacto = self._obtener_datos_contacto(
            contacto_id, self.campos_contacto, contactos_dict)
        lista_opciones.append(telefono_contacto)
        lista_opciones.extend(datos_contacto)
        lista_opciones.append(log_no_contactado_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        lista_opciones.append(estado)
        tipo_llamada = log_no_contactado.tipo_llamada
        if tipo_llamada == Campana.TYPE_DIALER:
            agente_info = "DIALER"
        elif tipo_llamada == Campana.TYPE_ENTRANTE:
            agente_info = "IN"
        else:
            agente_info = agentes_dict.get(log_no_contactado.agente_id, -1)
        lista_opciones.append(agente_info)
        # --- Finalmente, escribimos la linea
        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)


class ReporteCalificadosCSV(ReporteCSV):

    def __init__(
            self, campana, metadata, opciones_calificacion, respuestas_formulario_gestion_dict):
        self.campana = campana
        self.respuestas_formulario_gestion_dict = respuestas_formulario_gestion_dict
        self.bd_metadata = metadata
        self.opciones_calificacion = opciones_calificacion
        self.datos = []
        self.campos_formularios_opciones = {}
        self.posiciones_opciones = {}
        self._escribir_encabezado()

    def _escribir_encabezado(self):
        # Creamos encabezado
        encabezado = []
        encabezado.append(self.bd_metadata.nombre_campo_telefono)
        campos_contacto = self.bd_metadata.nombres_de_columnas_de_datos
        encabezado.extend(campos_contacto)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Tel contactado"))
        encabezado.append(_("Calificado"))
        encabezado.append(_("Observaciones"))
        encabezado.append(_("Agente"))
        encabezado.append(_("base de datos"))

        # agrego el encabezado para los campos de los formularios
        if self.campana.tipo_interaccion is Campana.FORMULARIO:
            for opcion in self.opciones_calificacion:
                if opcion.id not in self.posiciones_opciones and \
                   opcion.tipo == OpcionCalificacion.GESTION:
                    self.posiciones_opciones[opcion.id] = len(encabezado)
                    campos = opcion.formulario.campos.all()
                    self.campos_formularios_opciones[opcion.id] = campos
                    encabezado.append(opcion.nombre)
                    for campo in campos:
                        nombre = campo.nombre_campo
                        encabezado.append(nombre)
        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_calificacion(self, calificacion_val, log_llamada):
        lista_opciones = []
        # --- Buscamos datos
        if self.campana.es_entrante:
            calificacion = calificacion_val.history_object
            calificacion_fecha_local = localtime(calificacion_val.history_date)
        else:
            calificacion = calificacion_val
            calificacion_fecha_local = localtime(calificacion.fecha)
        lista_opciones.append(calificacion.contacto.telefono)
        datos = json.loads(calificacion.contacto.datos)
        lista_opciones.extend(datos)
        lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        lista_opciones.append(_("Contactado"))
        numero_marcado = log_llamada.numero_marcado
        lista_opciones.append(numero_marcado)
        lista_opciones.append(calificacion.opcion_calificacion.nombre)
        lista_opciones.append(calificacion.observaciones.replace('\r\n', ' '))
        lista_opciones.append(calificacion.agente)
        if calificacion.contacto.es_originario:
            lista_opciones.append(calificacion.contacto.bd_contacto)
        else:
            lista_opciones.append(_("Fuera de base"))
        if isinstance(calificacion_val, HistoricalCalificacionCliente) and \
           calificacion_val.history_date == calificacion.modified:
            # Es una calificacion historica que no es la ultima sobre el contacto
            # (campaña entrante)
            respuesta_formulario_gestion = None
        else:
            respuesta_formulario_gestion = self.respuestas_formulario_gestion_dict.get(
                calificacion.pk)
        if (calificacion.es_gestion() and
            self.campana.tipo_interaccion is Campana.FORMULARIO and
                respuesta_formulario_gestion is not None):
            datos = json.loads(respuesta_formulario_gestion.metadata)

            # Agrego Datos de la respuesta del formulario
            datos = json.loads(respuesta_formulario_gestion.metadata)
            id_opcion = respuesta_formulario_gestion.calificacion.opcion_calificacion_id
            posicion = self.posiciones_opciones[id_opcion]
            # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
            posiciones_vacias = posicion - len(lista_opciones)
            lista_opciones = lista_opciones + [''] * posiciones_vacias
            # Columna vacia correspondiente al nombre de la Opcion de calificacion
            lista_opciones.append('')
            campos = self.campos_formularios_opciones[id_opcion]
            for campo in campos:
                lista_opciones.append(
                    datos.get(campo.nombre_campo, '').replace('\r\n', ' '))

        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)


class ReporteContactadosCSV(ReporteCSV):
    def __init__(
            self, campana, bd_metadata, opciones_calificacion, contactos_dict,
            respuestas_formulario_gestion_dict):
        self.campana = campana
        self.respuestas_formulario_gestion_dict = respuestas_formulario_gestion_dict
        self.contactos_dict = contactos_dict
        self.bd_metadata = bd_metadata
        self.opciones_calificacion = opciones_calificacion
        self.campos_contacto_datos = self.bd_metadata.nombres_de_columnas_de_datos
        self.datos = []
        self.campos_formulario_opciones = {}
        self.posiciones_opciones = {}
        self._escribir_encabezado()

    def _obtener_datos_contacto_contactados(self, llamada_log, calificacion, datos_contacto):
        tel_status = _('Fuera de base')
        bd_contacto = _('Fuera de base')
        telefono_contacto = ''
        contacto = calificacion.contacto if calificacion else None
        if contacto is None:
            contacto = self.contactos_dict.get(llamada_log.contacto_id)
        if contacto is not None:
            telefono_contacto = contacto.telefono
            tel_status = _('Contactado')
            datos_contacto = json.loads(contacto.datos)
            if contacto.es_originario:
                bd_contacto = contacto.bd_contacto
        return tel_status, bd_contacto, datos_contacto, telefono_contacto

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Telefono contactado"))
        campos_contacto = self.bd_metadata.nombres_de_columnas
        # TODO: hacer más prolija esta parte, para evitar futuros desfasajes
        encabezado.extend(campos_contacto)
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Duración"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Calificado"))
        encabezado.append(_("Observaciones"))
        encabezado.append(_("Agente"))
        encabezado.append(_("base de datos"))

        # agrego el encabezado para los campos de los formularios
        if self.campana.tipo_interaccion is Campana.FORMULARIO:
            cant_campos_gestion = 0
            for opcion in self.opciones_calificacion:
                if opcion.id not in self.posiciones_opciones and \
                   opcion.tipo == OpcionCalificacion.GESTION:
                    self.posiciones_opciones[opcion.id] = cant_campos_gestion
                    campos = opcion.formulario.campos.all()
                    self.campos_formulario_opciones[opcion.id] = campos
                    encabezado.append(opcion.nombre)
                    cant_campos_gestion += 1
                    for campo in campos:
                        nombre = campo.nombre_campo
                        encabezado.append(nombre)
                        cant_campos_gestion += 1

        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_log(self, llamada_log, datos_calificacion, calificacion_historica):
        datos_contacto = [''] * len(self.campos_contacto_datos)
        calificacion = calificacion_historica
        tel_status, bd_contacto, datos_contacto, telefono_contacto = self.\
            _obtener_datos_contacto_contactados(llamada_log, calificacion, datos_contacto)
        datos_gestion = []
        if calificacion:
            calificacion_final = calificacion_historica.history_object
            # TODO: ver la forma de relacionar con respuestas vieja.
            if calificacion_historica.history_date == calificacion_final.modified:
                es_ultima_calificacion_historica = True
            else:
                es_ultima_calificacion_historica = False
            if hasattr(calificacion, 'es_gestion'):
                es_gestion = calificacion.es_gestion()
            else:
                es_gestion = (calificacion.opcion_calificacion.tipo ==
                              OpcionCalificacion.GESTION)
            if es_gestion:
                respuesta_formulario_gestion = self.respuestas_formulario_gestion_dict.get(
                    calificacion.history_object.pk)
            else:
                respuesta_formulario_gestion = None
            if (es_gestion and es_ultima_calificacion_historica and
                self.campana.tipo_interaccion is Campana.FORMULARIO and
                    respuesta_formulario_gestion is not None):
                # si es la ultima calificacion historica, que coincide con el valor
                # final de la calificacion y es de gestion, entonces mostramos el valor de
                # la gestión (si existe) y se muestran Datos de la respuesta del formulario
                datos = json.loads(respuesta_formulario_gestion.metadata)
                id_opcion = respuesta_formulario_gestion.calificacion.opcion_calificacion_id
                posicion = self.posicion_opciones[id_opcion]
                # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
                posiciones_vacias = posicion - len(datos_gestion)
                datos_gestion = datos_gestion + [''] * posiciones_vacias
                # Columna vacia correspondiente al nombre de la Opcion de calificacion
                datos_gestion.append('')
                campos = self.campos_formulario_opciones[id_opcion]
                for campo in campos:
                    datos_gestion.append(
                        datos.get(campo.nombre_campo, '').replace('\r\n', ' '))

        fecha_local_llamada = localtime(llamada_log.time)
        duracion_llamada = llamada_log.duracion_llamada
        if duracion_llamada > 0:
            duracion_llamada = timedelta(0, duracion_llamada)
        else:
            duracion_llamada = 'N/A'

        registro = []
        registro.append(llamada_log.numero_marcado)
        registro.append(telefono_contacto)
        registro.extend(datos_contacto)
        registro.append(fecha_local_llamada.strftime("%Y/%m/%d %H:%M:%S"))
        registro.append(str(duracion_llamada))
        registro.append(tel_status)
        registro.extend(datos_calificacion)
        registro.append(bd_contacto)
        registro.extend(datos_gestion)

        lista_datos_utf8 = [force_text(item) for item in registro]
        self.datos.append(lista_datos_utf8)


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


class EstadisticasService:

    def __init__(self, campana, fecha_desde, fecha_hasta):
        self.campana = campana
        self.bd_contacto = campana.bd_contacto
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta

        self.tipo_campana = campana.type

        self.calificaciones_finales_dict = {}

        self.calificaciones_historicas_dict = {}

        self.contactos_dict = {}

        self.agentes_dict = {}

        # con el id de la calificacion asociada como clave
        self.respuestas_formulario_gestion_dict = {}

        self.logs_llamadas_dict = OrderedDict({})

        self.opciones_calificacion_campana = {opcion.pk: opcion for opcion in
                                              self.campana.opciones_calificacion.all(
                                              ).select_related('formulario').prefetch_related(
                                                  'formulario__campos')}
        self.bd_metadata = self.bd_contacto.get_metadata()

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

        # reportes para exportación a csv
        self.reporte_csv_no_atendidos = ReporteNoAtendidosCSV(self.bd_metadata)
        self.reporte_csv_contactados = ReporteContactadosCSV(
            self.campana, self.bd_metadata, self.opciones_calificacion_campana.values(),
            self.contactos_dict, self.respuestas_formulario_gestion_dict)
        self.reporte_csv_calificados = ReporteCalificadosCSV(
            self.campana, self.bd_metadata, self.opciones_calificacion_campana.values(),
            self.respuestas_formulario_gestion_dict)

    def _inicializar_valores_estadisticas(self):
        self._inicializar_valores_logs_llamadas()
        self._inicializar_valores_calificaciones()
        self._inicializar_respuestas_formulario_gestion()
        self._inicializar_valores_contactos()
        self._inicializar_valores_agentes()

    def _inicializar_valores_logs_llamadas(self):
        for log in LlamadaLog.objects.filter(
            campana_id=self.campana.pk, time__range=(self.fecha_desde, self.fecha_hasta)).order_by(
                '-time'):
            self.logs_llamadas_dict[log.pk] = log

    def _inicializar_valores_calificaciones(self):
        calificacion_finales_qs = CalificacionCliente.objects.filter(
            opcion_calificacion__campana=self.campana, fecha__range=(
                self.fecha_desde, self.fecha_hasta)).select_related(
                    'agente', 'contacto', 'opcion_calificacion').prefetch_related(
                        'contacto__bd_contacto', 'agente__user')

        for calificacion in calificacion_finales_qs:
            self.calificaciones_finales_dict[calificacion.callid] = calificacion

        calificaciones_historicas_qs = CalificacionCliente.history.filter(
            history_date__range=(self.fecha_desde, self.fecha_hasta),
            opcion_calificacion__campana=self.campana).select_related(
                'agente', 'contacto', 'opcion_calificacion').prefetch_related(
                    'contacto__bd_contacto', 'agente__user')
        self.calificaciones_historicas_dict = {calificacion.callid: calificacion for calificacion
                                               in calificaciones_historicas_qs}

    def _inicializar_respuestas_formulario_gestion(self):
        respuestas_formulario_gestion_qs = RespuestaFormularioGestion.objects.filter(
            calificacion__callid__in=self.calificaciones_finales_dict.keys()).select_related(
                'calificacion')
        for respuesta in respuestas_formulario_gestion_qs:
            self.respuestas_formulario_gestion_dict[respuesta.calificacion.pk] = respuesta

    def _inicializar_valores_contactos(self):
        contactos_ids = set()
        for llamada_log in self.logs_llamadas_dict.values():
            contacto_id = llamada_log.contacto_id
            if contacto_id != -1:
                contactos_ids.add(contacto_id)
        contactos = Contacto.objects.filter(
            id__in=contactos_ids) | self.bd_contacto.contactos.all()
        self.contactos_dict = {contacto.pk: contacto for contacto in contactos}

    def _inicializar_valores_agentes(self):
        # se crean un diccionario de los agentes de la campaña
        # para evitar accesos a la BD para recuperarlos desde los logs
        agentes_campana = AgenteProfile.objects.obtener_agentes_campana(
            self.campana).select_related('user')
        for agente in agentes_campana:
            self.agentes_dict[agente.pk] = agente

    def _obtener_llamadas_atendidas_sin_calificacion(
            self, evento, calificacion_final, calificacion_historica):
        # obtener_llamadas_atendidas_sin_calificacion(log_llamada)
        if not calificacion_final and not calificacion_historica:
            if evento in LlamadaLog.EVENTOS_INICIO_CONEXION:
                # TODO: analizar consecuencias de que los eventos obtenidos
                # cada llamada son los ultimos de cada llamada
                # TODO: ver que pasaría con 'BT-ANSWER', 'CT-ACCEPT'
                self.llamadas_atendidas_sin_calificacion += 1

    def _obtener_datos_csv_contactados(
            self, evento, calificacion_historica, log_llamada):
        if evento in LlamadaLog.EVENTOS_FIN_CONEXION:
            if not calificacion_historica:
                datos_calificacion = [_("Llamada Atendida sin calificacion"),
                                      '',
                                      self.agentes_dict.get(log_llamada.agente_id, -1)]
            else:
                datos_calificacion = [calificacion_historica.opcion_calificacion.nombre,
                                      calificacion_historica.observaciones.replace('\r\n', ' '),
                                      calificacion_historica.agente]
            self.reporte_csv_contactados._escribir_linea_log(
                log_llamada, datos_calificacion, calificacion_historica)

    def _obtener_total_llamadas(
            self, evento, es_campana_entrante, calificacion_final, callid,
            callids_analizados, fecha, fecha_desde, fecha_hasta, bridge_wait_time):
        if calificacion_final and calificacion_final.opcion_calificacion.es_agenda() and \
           callid not in callids_analizados:
            self.reporte_totales_llamadas._llamadas_pendientes += 1
        if evento == 'DIAL':
            self.reporte_totales_llamadas.llamadas_realizadas += 1
        if es_campana_entrante and fecha > fecha_desde and fecha < fecha_hasta:
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
        if self.campana.es_dialer:
            campana_service = CampanaService()
            dato_campana = campana_service.obtener_dato_campana_run(self.campana)
            self.reporte_totales_llamadas._llamadas_pendientes = 0
            if dato_campana:
                self.reporte_totales_llamadas._llamadas_pendientes = dato_campana.get(
                    'n_est_remaining_calls', 0)

    def _obtener_reporte_no_atendidos(self, log_llamada, evento):
        # obtener_cantidad_no_atendidos(log_llamada) + datos_csv
        if evento in self.reporte_no_atendidos.eventos_headers.keys():
            evento_header = self.reporte_no_atendidos.eventos_headers[evento]
            self.reporte_no_atendidos.reporte[evento_header] += 1
            self.reporte_no_atendidos.total_no_atendidos += 1
            self.reporte_csv_no_atendidos._escribir_linea_log(
                log_llamada, self.contactos_dict, self.agentes_dict)

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
            self.reporte_csv_calificados._escribir_linea_calificacion(calificacion, log_llamada)
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
        for log_llamada in self.logs_llamadas_dict.values():
            evento = log_llamada.event
            callid = log_llamada.callid
            fecha = log_llamada.time
            tipo_llamada = log_llamada.tipo_llamada
            bridge_wait_time = log_llamada.bridge_wait_time
            es_campana_entrante = self.campana.es_entrante
            calificacion_historica = self.calificaciones_historicas_dict.get(callid, False)
            calificacion_final = self.calificaciones_finales_dict.get(callid, False)
            hoy_ahora = timezone.now()
            fecha_desde = datetime_hora_minima_dia_utc(hoy_ahora)
            fecha_hasta = datetime_hora_maxima_dia_utc(hoy_ahora)
            self._obtener_llamadas_atendidas_sin_calificacion(
                evento, calificacion_final, calificacion_historica)
            # obtener_detalle_llamadas(log_llamada)
            self.reporte_detalle_llamadas._calcular_detalle(evento, tipo_llamada)
            # obtener_datos_csv_contactados(log_llamada)
            self._obtener_datos_csv_contactados(evento, calificacion_historica, log_llamada)
            # obtener_cantidad_no_atendidos(log_llamada) + datos_csv
            self._obtener_reporte_no_atendidos(log_llamada, evento)
            # obtener_total_llamadas (log_llamada)
            self._obtener_total_llamadas(
                evento, es_campana_entrante, calificacion_final, callid, callids_analizados,
                fecha, fecha_desde, fecha_hasta, bridge_wait_time)
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

        exportacion_campana_csv = ExportacionCampanaCSV()
        exportacion_campana_csv.exportar_reportes_csv(
            campana, self.reporte_csv_contactados.datos,
            self.reporte_csv_calificados.datos, self.reporte_csv_no_atendidos.datos)

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
        barra_campana_calificacion.title = _('Cantidad de calificacion de cliente ')

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
