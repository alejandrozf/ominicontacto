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
Servicio para generar reporte csv para todas las calificaciones de una campana
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from ominicontacto_app.utiles import crear_archivo_en_media_root


logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, campana):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-reporte_calificacion".format(
            self._campana.id)
        self.sufijo_nombre_de_archivo = ".csv"
        self.nombre_de_archivo = "{0}{1}".format(
            self.prefijo_nombre_de_archivo, self.sufijo_nombre_de_archivo)
        self.url_descarga = os.path.join(settings.MEDIA_URL,
                                         self.nombre_del_directorio,
                                         self.nombre_de_archivo)
        self.ruta = os.path.join(settings.MEDIA_ROOT,
                                 self.nombre_del_directorio,
                                 self.nombre_de_archivo)

    def crear_archivo_en_directorio(self):
        if self.ya_existe():
            # Esto puede suceder si en un intento previo de depuracion, el
            # proceso es abortado, y por lo tanto, el archivo puede existir.
            logger.warn(_("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                          "reporte para la campana {0}. Archivo: {1}. "
                          "El archivo sera sobreescrito".format(self._campana.pk, self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, calificaciones_qs):

        with open(self.ruta, 'w', encoding='utf-8') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Fecha-Hora Contacto"))
            encabezado.append(_("Agente"))
            encabezado.append(_("Tel status"))
            encabezado.append(_("Tel contactado"))
            nombres = self._campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
            for nombre in nombres:
                encabezado.append(nombre)
            encabezado.append(_("Calificado"))
            encabezado.append(_("Observaciones"))
            encabezado.append(_("base de datos"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item) for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las calificaciones de la campana
            for calificacion in calificaciones_qs:
                lista_opciones = []

                # --- Buscamos datos
                calificacion_fecha_local = localtime(calificacion.fecha)
                lista_opciones.append(calificacion_fecha_local.strftime("%Y/%m/%d %H:%M:%S"))
                lista_opciones.append(calificacion.agente)
                lista_opciones.append(_("Contactado"))
                lista_opciones.append(calificacion.contacto.telefono)
                datos = json.loads(calificacion.contacto.datos)
                for dato in datos:
                    lista_opciones.append(dato)
                lista_opciones.append(calificacion.opcion_calificacion.nombre)
                lista_opciones.append(calificacion.observaciones.replace('\r\n', ' '))
                if calificacion.contacto.es_originario:
                    lista_opciones.append(calificacion.contacto.bd_contacto)
                else:
                    lista_opciones.append(_("Fuera de base"))

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaService(object):

    def __init__(self, campana):
        self.campana = campana
        self.calificaciones_qs = campana.obtener_calificaciones().select_related(
            'opcion_calificacion', 'contacto').prefetch_related(
                'contacto__bd_contacto', 'agente__user')

    def crea_reporte_csv(self):
        archivo_de_reporte = ArchivoDeReporteCsv(self.campana)

        archivo_de_reporte.crear_archivo_en_directorio()

        archivo_de_reporte.escribir_archivo_csv(self.calificaciones_qs)

    def obtener_url_reporte_csv_descargar(self):
        archivo_de_reporte = ArchivoDeReporteCsv(self.campana)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga para la campana {0}".format(self.campana.pk)))
        assert os.path.exists(archivo_de_reporte.url_descarga)
