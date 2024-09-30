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
Servicio para generar reporte csv de las gestiones realizada por una campana
"""

from __future__ import unicode_literals

import logging
import json

from django.utils.encoding import force_text
from django.utils.timezone import localtime
from django.utils.translation import gettext as _

from ominicontacto_app.models import CalificacionCliente, OpcionCalificacion, \
    RespuestaFormularioGestion

from ominicontacto_app.services.reporte_campana_csv import ReporteCSV

logger = logging.getLogger(__name__)


class ReporteFormularioGestionCampanaCSV(ReporteCSV):

    def __init__(self, campana, key_task, fecha_desde, fecha_hasta):
        self.campana = campana
        self.campos_formulario_opciones = {}
        self.posicion_opciones = {}
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.datos = []
        respuestas = RespuestaFormularioGestion.history.filter(
            calificacion__opcion_calificacion__campana=self.campana,
            history_date__range=(fecha_desde, fecha_hasta)).select_related(
                'calificacion').prefetch_related(
                    'calificacion__contacto', 'calificacion__agente',
                    'calificacion__agente__user',
                    'calificacion__contacto__bd_contacto',
                    'calificacion__opcion_calificacion')
        cant_respuestas = respuestas.count()
        if cant_respuestas == 0:
            porcentaje_inicial = 100
        else:
            porcentaje_inicial = 0
        analizadas = set()
        self.redis_connection.publish(key_task, porcentaje_inicial)
        self._escribir_encabezado()
        for i, respuesta in enumerate(respuestas, start=1):
            percentage = int((i / cant_respuestas) * 100)
            self.redis_connection.publish(key_task, percentage)
            if respuesta and (respuesta.pk not in analizadas):
                self._escribir_linea_calificacion(respuesta)
                analizadas.add(respuesta.pk)

    def _escribir_encabezado(self):
        encabezado = []
        encabezado.append(_("Fecha-Hora Contacto"))
        encabezado.append(_("Agente"))
        encabezado.append(_("Telefono"))
        nombres = self.campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
        for nombre in nombres:
            encabezado.append(nombre)
        encabezado.append(_("base_datos"))
        encabezado.append(_("Calificación"))

        # Para cada formulario, poner una columna vacia con su nombre seguida de los nombres
        # de las columnas de cada campo
        # if not self.campana.tiene_interaccion_con_sitio_externo:
        for opcion in self.campana.opciones_calificacion.filter(
                tipo=OpcionCalificacion.GESTION).select_related(
                    'formulario').prefetch_related('formulario__campos'):
            if opcion.nombre not in self.posicion_opciones:
                self.posicion_opciones[opcion.id] = len(encabezado)
                campos = opcion.formulario.campos.all()
                self.campos_formulario_opciones[opcion.id] = campos
                encabezado.append(opcion.nombre)
                for campo in campos:
                    nombre = campo.nombre_campo
                    encabezado.append(nombre)

        lista_datos_utf8 = [force_text(item) for item in encabezado]
        self.datos.append(lista_datos_utf8)

    def _escribir_linea_calificacion(self, respuesta):
        lista_opciones = []
        metadata_fecha_local = localtime(respuesta.history_date)
        lista_opciones.append(metadata_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
        lista_opciones.append(respuesta.calificacion.agente)
        lista_opciones.append(respuesta.calificacion.contacto.telefono)
        contacto = respuesta.calificacion.contacto
        datos = json.loads(contacto.datos)
        for dato in datos:
            lista_opciones.append(dato)
        if contacto.es_originario:
            lista_opciones.append(contacto.bd_contacto)
        else:
            lista_opciones.append(_("Fuera de base"))
        lista_opciones.append(respuesta.calificacion.opcion_calificacion.nombre)

        # Datos de la respuesta
        datos = json.loads(respuesta.metadata)
        if respuesta.history_change_reason is not None:
            calif = CalificacionCliente.history.get(
                pk=respuesta.history_change_reason)
            id_opcion = calif.opcion_calificacion_id
            lista_opciones[len(lista_opciones) - 1] = calif.opcion_calificacion.nombre
        else:
            id_opcion = respuesta.calificacion.opcion_calificacion_id
        try:
            posicion = self.posicion_opciones[id_opcion]
        except Exception:
            return
        # Relleno las posiciones vacias anteriores (de columnas de otro formulario)
        posiciones_vacias = posicion - len(lista_opciones)
        lista_opciones = lista_opciones + [''] * posiciones_vacias
        # Columna vacia correspondiente al nombre de la Opcion de calificacion
        lista_opciones.append('')
        campos = self.campos_formulario_opciones[id_opcion]
        for campo in campos:
            lista_opciones.append(str(datos.get(campo.nombre_campo, '')).replace('\r\n', ' '))

        lista_datos_utf8 = [force_text(item) for item in lista_opciones]
        self.datos.append(lista_datos_utf8)
