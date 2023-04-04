# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Servicio para generar reporte csv para todas las calificaciones de una campana
"""

from __future__ import unicode_literals

import logging
import json

from django.utils.encoding import force_text
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from ominicontacto_app.services.reporte_campana_csv import ReporteCSV

logger = logging.getLogger(__name__)


class ReporteCampanaService(object):

    def __init__(self, campana):
        self.campana = campana
        self.calificaciones_qs = campana.obtener_calificaciones().select_related(
            'opcion_calificacion', 'contacto').prefetch_related(
                'contacto__bd_contacto', 'agente__user')
        self.historico_calificaciones_qs = campana.obtener_historico_calificaciones() \
            .select_related(
            'opcion_calificacion', 'contacto').prefetch_related(
                'contacto__bd_contacto', 'agente__user')

    def calificaciones_por_fechas(self, fecha_desde, fecha_hasta):
        self.calificaciones_qs = self.calificaciones_qs.filter(
            fecha__range=(fecha_desde, fecha_hasta))
        self.historico_calificaciones_qs = self.historico_calificaciones_qs.filter(
            fecha__range=(fecha_desde, fecha_hasta))


class ReporteCalificacionesCampanaCSV(ReporteCampanaService, ReporteCSV):

    def __init__(self, campana, key_task, fecha_desde, fecha_hasta):
        ReporteCampanaService.__init__(self, campana)
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.datos = []
        self.calificaciones_por_fechas(fecha_desde, fecha_hasta)
        calificaciones = self.historico_calificaciones_qs
        cant_calificaciones = calificaciones.count()
        if cant_calificaciones == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        calificaciones_analizadas = set()
        self.redis_connection.publish(key_task, porcentaje_inicial)
        self._escribir_encabezado()
        for i, calificacion in enumerate(calificaciones, start=1):
            percentage = int((i / cant_calificaciones) * 100)
            self.redis_connection.publish(key_task, percentage)
            if calificacion and (calificacion.pk not in calificaciones_analizadas):
                self._escribir_linea_calificacion(calificacion, calificacion)
                calificaciones_analizadas.add(calificacion.pk)

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Agente"))
        encabezado.append(_("Tel status"))
        encabezado.append(_("Tel contactado"))
        nombres = self.campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
        for nombre in nombres:
            encabezado.append(nombre)
        encabezado.append(_("Calificado"))
        encabezado.append(_("Observaciones"))
        encabezado.append(_("base de datos"))
        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_calificacion(self, calificacion, log_llamada):
        lista_opciones = []
        calificacion_fecha_local = localtime(calificacion.history_date)
        lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        lista_opciones.append(calificacion.agente)
        lista_opciones.append(_("Contactado"))
        lista_opciones.append(calificacion.contacto.telefono)
        datos = json.loads(calificacion.contacto.datos)
        for dato in datos:
            lista_opciones.append(dato)
        opcion_calificacion_nombre = calificacion.opcion_calificacion.nombre
        if calificacion.opcion_calificacion.es_agenda():
            opcion_calificacion_nombre = "{} {}".\
                format(opcion_calificacion_nombre, calificacion.get_tipo_agenda_display())
        lista_opciones.append(opcion_calificacion_nombre)
        lista_opciones.append(calificacion.observaciones.replace('\r\n', ' '))
        if calificacion.contacto.es_originario:
            lista_opciones.append(calificacion.contacto.bd_contacto)
        else:
            lista_opciones.append(_("Fuera de base"))

        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)
