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
Servicio para generar reporte csv de las gestiones realizada por una campana
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _

from ominicontacto_app.models import RespuestaFormularioGestion
from ominicontacto_app.utiles import crear_archivo_en_media_root


logger = logging.getLogger(__name__)


class ArchivoDeReporteRespuestaFormularioCsv(object):
    def __init__(self, campana):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-reporte_venta".format(
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
            logger.warn("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                        "reporte para la campana {0}. Archivo: {1}. "
                        "El archivo sera sobreescrito".format(self._campana.pk,
                                                              self.ruta))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, campana):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Fecha-Hora Contacto"))
            encabezado.append(_("Agente"))
            encabezado.append(_("Telefono"))
            nombres = campana.bd_contacto.get_metadata().nombres_de_columnas_de_datos
            for nombre in nombres:
                encabezado.append(nombre)
            encabezado.append(_("base_datos"))
            encabezado.append(_("Calificación"))
            campos = []
            if not campana.tiene_interaccion_con_sitio_externo:
                campos = campana.formulario.campos.all()

            for campo in campos:
                encabezado.append(campo.nombre_campo)

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada una de las respuestas de la gestion del formulario
            respuestas = RespuestaFormularioGestion.objects.filter(
                calificacion__opcion_calificacion__campana=campana)
            for respuesta in respuestas:
                lista_opciones = []

                # --- Buscamos datos
                metadata_fecha_local = localtime(respuesta.fecha)
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
                datos = json.loads(respuesta.metadata)
                for campo in campos:
                    lista_opciones.append(datos[campo.nombre_campo])

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteRespuestaFormularioGestionService(object):

    def crea_reporte_csv(self, campana):
        # assert campana.estado == Campana.ESTADO_ACTIVA

        archivo_de_reporte = ArchivoDeReporteRespuestaFormularioCsv(campana)

        archivo_de_reporte.crear_archivo_en_directorio()

        # opciones_por_contacto = self._obtener_opciones_por_contacto(campana)

        archivo_de_reporte.escribir_archivo_csv(campana)

    def obtener_url_reporte_csv_descargar(self, campana):
        # assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteRespuestaFormularioCsv(campana)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga para la campana {0}".format(campana.pk)))
        assert os.path.exists(archivo_de_reporte.url_descarga)
