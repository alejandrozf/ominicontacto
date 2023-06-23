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

import csv
import logging
import os

from django.conf import settings
from django.utils.encoding import force_text


from django.utils.translation import gettext as _


from ominicontacto_app.utiles import crear_archivo_en_media_root

logger = logging.getLogger(__name__)


class CrearArchivoDeReporteCsv(object):
    def __init__(self, nombre_reporte, datos_reporte=None):
        self.nombre_del_directorio = 'reporte_auditoria'
        self.prefijo_nombre_de_archivo = nombre_reporte
        self.datos_reporte = datos_reporte

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
            logger.warn(_("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                          "reporte de auditoria. Archivo: {0}. "
                          "El archivo sera sobreescrito".format(self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def _escribir_csv_writer_utf_8(self, csvwriter, datos):
        lista_datos_utf8 = [force_text(item) for item in datos]
        csvwriter.writerow(lista_datos_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)

    def escribir_archivo_datos_csv(self):
        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            csvwiter = csv.writer(csvfile)
            for registro in self.datos_reporte:
                self._escribir_csv_writer_utf_8(csvwiter, registro)


class ExportacionArchivoCSV(object):
    def __init__(self, nombre_reporte):
        self.nombre_reporte = nombre_reporte

    def obtener_url_reporte_csv_descargar(self):
        archivo_de_reporte = CrearArchivoDeReporteCsv(self.nombre_reporte)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga"))
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def exportar_reportes_csv(self, datos):
        archivo_de_reporte = CrearArchivoDeReporteCsv(self.nombre_reporte, datos)
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_datos_csv()
