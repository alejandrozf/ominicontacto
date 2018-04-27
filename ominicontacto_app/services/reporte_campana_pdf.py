# -*- coding: utf-8 -*-

"""
Servicio de reportes de campanas para pdf
"""

from __future__ import unicode_literals

import logging
import os


from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


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
            logger.warn("ArchivoDeReportePDF: Ya existe archivo CSV de "
                        "reporte para la campana %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._campana.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def cabecera(self, pdf, campana):

        # archivo_imagen = settings.STATIC_ROOT + '/ominicontacto/Img/fts.png'
        # pdf.drawImage(archivo_imagen, 40, 750, 120, 90,
        #             preserveAspectRatio=True)
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(180, 790, u"Omnileads")
        pdf.setFont("Helvetica", 14)
        nombre_reporte = u"Reporte de campana: {0}".format(campana.nombre)
        pdf.drawString(200, 770, nombre_reporte)

    def get(self, campana, estadisticas):
        # Canvas nos permite hacer el reporte con coordenadas X y Y

        pdf = canvas.Canvas(self.ruta)
        self.cabecera(pdf, campana)

        self.tabla_calificacion(pdf, estadisticas['dict_campana_counter'],
                                estadisticas['total_asignados']
                                )
        self.tabla_no_atendidos(pdf, estadisticas['dict_no_atendido_counter'],
                                estadisticas['total_no_atendidos']
                                )

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
        pdf.setFont("Helvetica", 10)
        pdf.drawString(0.75 * inch, 740, u"Cantidad por calificacion")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 50, 50)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf, 0.75 * inch, 7.1 * inch)
        archivo_imagen = settings.MEDIA_ROOT + \
            '/reporte_campana/barra_campana_calificacion.png'

        pdf.drawImage(archivo_imagen, 4 * inch, 7.5 * inch, 250, 200,
                      preserveAspectRatio=True, mask="auto")

    def tabla_no_atendidos(self, pdf, dict_no_atendidos, total_no_atendidos):
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
        pdf.drawString(0.75 * inch, 430, u"Cantidad de llamados no atendidos")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf, 0.75 * inch, 4.3 * inch)
        archivo_imagen = settings.MEDIA_ROOT + \
            '/reporte_campana/barra_campana_no_atendido.png'

        pdf.drawImage(archivo_imagen, 4 * inch, 3.5 * inch, 250, 200,
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
        # pdf.drawString(0.75*inch, 9 * inch, u"Calificaciones por agente")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 50, 50)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf, 0.75 * inch, 300)

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
        logger.error("obtener_url_reporte_pdf_descargar(): NO existe archivo"
                     " PDF de descarga para la campana %s", campana.pk)
        assert os.path.exists(archivo_de_reporte.url_descarga)
