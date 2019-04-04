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

from __future__ import unicode_literals

import logging
import os
import csv
import json

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.conf import settings

from ominicontacto_app.utiles import crear_archivo_en_media_root

logger = logging.getLogger(__name__)

# TODO: Borrar archivos viejos? De más de 1 día x ej.


class ReporteDeResultadosCSV(object):
    """Generador de archivo CSV para el Reporte de Resultados"""
    def __init__(self, campana):
        self.campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-reporte_resultados".format(self.campana.id)
        self.sufijo_nombre_de_archivo = ".csv"
        self.nombre_de_archivo = "{0}{1}".format(
            self.prefijo_nombre_de_archivo, self.sufijo_nombre_de_archivo)
        self.url_descarga = os.path.join(settings.MEDIA_URL,
                                         self.nombre_del_directorio,
                                         self.nombre_de_archivo)
        self.ruta = os.path.join(settings.MEDIA_ROOT,
                                 self.nombre_del_directorio,
                                 self.nombre_de_archivo)

    def _crear_archivo_en_directorio(self):
        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def generar_archivo_descargable(self, reporte):
        self._crear_archivo_en_directorio()

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            # TODO: Discutir si Poner mismo nombre del campo telefono en la base de datos?
            encabezado.append(_("Teléfono"))
            nombres = self.campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
            for nombre in nombres:
                encabezado.append(nombre)
            encabezado.append(_("Calificación"))
            encabezado.append(_("Contactación"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            for contactacion in reporte.contactaciones.values():
                lista_opciones = []
                lista_opciones.append(contactacion['contacto'].telefono)
                datos = json.loads(contactacion['contacto'].datos)
                for dato in datos:
                    lista_opciones.append(dato)
                if contactacion['calificacion'] is not None:
                    lista_opciones.append(contactacion['calificacion'])
                else:
                    lista_opciones.append('')
                if contactacion['contactacion'] is not None:
                    lista_opciones.append(contactacion['contactacion'])
                else:
                    lista_opciones.append('')

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def archivo_ya_generado(self):
        return os.path.exists(self.ruta)

    def obtener_url_reporte_csv_descargar(self):
        if self.archivo_ya_generado():
            return self.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la campana %s", self.campana.pk)
        assert os.path.exists(self.url_descarga)
