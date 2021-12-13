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
Servicio de reportes de campanas para pdf
"""

from __future__ import unicode_literals

import logging
import os


from django.conf import settings
from django.utils.translation import ugettext as _

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from ominicontacto_app.utiles import crear_archivo_en_media_root


logger = logging.getLogger(__name__)


class ArchivoDeReportePDF(object):
    def __init__(self, campana):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-reporte".format(self._campana.id)
        self.sufijo_nombre_de_archivo = ".pdf"
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
            logger.warn(_("ArchivoDeReportePDF: Ya existe archivo CSV de "
                          "reporte para la campana {0}. Archivo: {1}. "
                          "El archivo sera sobreescrito".format(self._campana.pk,
                                                                self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def get(self, campana, estadisticas):
        # Canvas nos permite hacer el reporte con coordenadas X y Y

        pdf = canvas.Canvas(self.ruta)

        self.tabla_calificacion(pdf, estadisticas['dict_campana_counter'],
                                estadisticas['total_asignados'])
        pdf.showPage()

        self.tabla_no_atendidos(pdf, estadisticas['dict_no_atendido_counter'],
                                estadisticas['total_no_atendidos'])
        pdf.showPage()

        self.tabla_agente(pdf, estadisticas['agentes_venta'],
                          estadisticas['calificaciones'])
        pdf.showPage()
        pdf.save()

    def tabla_calificacion(self, pdf, dict_calificacion, total_asignados):

        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Calificacion', 'Cantidad')
        # Creamos una lista de tuplas que van a contener a las personas

        detalles = [(calificaciones_nombre, calificaciones_cantidad)
                    for calificaciones_nombre, calificaciones_cantidad
                    in dict_calificacion]
        detalles.append(('Total asignados', total_asignados))
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles)
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        he, we = detalle_orden.wrapOn(pdf, 0, 0)

        pdf.setPageSize((he + 320, we + 400))

        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada

        # pdf.drawString(he / 2, we + 300, "Omnileads")

        pdf.setFont("Helvetica", 13)
        nombre_reporte = "Reporte de campana: {0}".format(self._campana.nombre)
        pdf.drawString(he / 4, we + 280, nombre_reporte)

        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, we + 260, _("Cantidad por calificacion"))
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 50, 250)
        archivo_imagen = settings.MEDIA_ROOT + \
            '/reporte_campana/barra_campana_calificacion_{}.png'.format(self._campana.id)

        pdf.drawImage(archivo_imagen, he + 51, 251, 250, 200,
                      preserveAspectRatio=True, mask="auto")

    def tabla_no_atendidos(self, pdf, dict_no_atendidos, total_no_atendidos):
        pdf.setPageSize((600, 600))
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Calificacion', 'Cantidad')
        # Creamos una lista de tuplas que van a contener a las personas

        detalles = [(resultado_nombre, resultado_cantidad)
                    for resultado_nombre, resultado_cantidad in dict_no_atendidos]
        detalles.append(('Total no atendidos', total_no_atendidos))
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles)
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]
        ))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(0.75 * inch, 520, _("Cantidad de llamados no atendidos"))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 6.75 mas cercano del margen TOP
        detalle_orden.drawOn(pdf, 0.75 * inch, 270)
        archivo_imagen = settings.MEDIA_ROOT + \
            '/reporte_campana/barra_campana_no_atendido_{}.png'.format(self._campana.id)

        pdf.drawImage(archivo_imagen, 4 * inch, 4.5 * inch, 250, 200,
                      preserveAspectRatio=True, mask="auto")

    def tabla_agente(self, pdf, agentes_venta, nombres_calificaciones):
        # Creamos una tupla de encabezados para nuestra tabla
        encabezados = ('Agente', 'Ventas')
        encabezados = encabezados + nombres_calificaciones

        # Creamos una lista de tuplas que va a contener los datos de los agentes
        detalles = []
        for agente in agentes_venta.values():
            datos_agente = [agente['nombre'], agente['total_gestionados']]
            datos_agente += agente['totales_calificaciones'].values()
            detalles.append(tuple(datos_agente))

        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles)
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]
        ))
        pdf.setFont("Helvetica", 10)
        # Establecemos el tamaño de la hoja que ocupará la tabla
        he, we = detalle_orden.wrapOn(pdf, 0, 0)
        pdf.setPageSize((he + 300, we + 300))
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 6.75 mas cercano del margen TOP
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, we + 200, _("Calificaciones agentes"))
        detalle_orden.drawOn(pdf, 100, we + 150)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaPDFService(object):

    def crea_reporte_pdf(self, campana, estadisticas):

        archivo_de_reporte = ArchivoDeReportePDF(campana)
        archivo_de_reporte.crear_archivo_en_directorio()

        archivo_de_reporte.get(campana, estadisticas)

    def obtener_url_reporte_pdf_descargar(self, campana):
        archivo_de_reporte = ArchivoDeReportePDF(campana)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_pdf_descargar(): NO existe archivo"
                       " PDF de descarga para la campana {0}".format(campana.pk)))
        assert os.path.exists(archivo_de_reporte.url_descarga)
