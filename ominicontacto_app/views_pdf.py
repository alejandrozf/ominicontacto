# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

# Importamos settings para poder tener a la mano la ruta de la carpeta media
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import cm
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.views.generic import View
from ominicontacto_app.models import User, Campana
from ominicontacto_app.services.estadisticas_campana import EstadisticasService


class ReportePersonasPDF(View):
    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la
        # carpeta media/imagenes
        archivo_imagen = settings.MEDIA_ROOT + '/imagenes/fts.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas
        # correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90,
                      preserveAspectRatio=True)
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(180, 790, u"Omnileads")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(200, 770, u"Reporte de campana")

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero
        # binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen
        # en la cabecera del reporte.
        self.cabecera(pdf)
        y = 600
        self.tabla(pdf, y)
        # Con show page hacemos un corte de página para pasar a la siguiente
        archivo_imagen = settings.MEDIA_ROOT +\
                         '/imagenes/barra_campana_calificacion.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas
        # correspondientes
        pdf.drawImage(archivo_imagen, 40, 300, 250, 200,
                      preserveAspectRatio=True, mask="auto")
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('username', 'first_name', 'last_name', 'email')
        # Creamos una lista de tuplas que van a contener a las personas
        detalles = [(user.username, user.first_name, user.last_name, user.email)
                    for user in User.objects.all()]
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles,
                              colWidths=[3 * cm, 4 * cm, 5 * cm, 5 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro
                # y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf,  0.75*inch, 7.5*inch)


class ReporteCampanaPDF(View):
    def cabecera(self, pdf, campana):

        #archivo_imagen = settings.STATIC_ROOT + '/ominicontacto/Img/fts.png'
        #pdf.drawImage(archivo_imagen, 40, 750, 120, 90,
         #             preserveAspectRatio=True)
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(180, 790, u"Omnileads")
        pdf.setFont("Helvetica", 14)
        nombre_reporte = u"Reporte de campana: {0}".format(campana.nombre)
        pdf.drawString(200, 770, nombre_reporte)

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        campana = Campana.objects.get(pk=self.kwargs['pk_campana'])
        service = EstadisticasService()
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        hoy = datetime.date(2015, 1, 1)
        estadisticas = service.general_campana(campana, hoy, hoy_ahora)
        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        self.cabecera(pdf, campana)
        y = 600

        self.tabla_calificacion(pdf, estadisticas['dict_campana_counter'],
                                estadisticas['total_asignados']
                                )
        self.tabla_no_atendidos(pdf, estadisticas['dict_no_atendido_counter'],
                                estadisticas['total_no_atendidos']
                                )
        self.tabla_agente(pdf, estadisticas['agentes_venta'],
                          estadisticas['calificaciones'])
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('username', 'first_name', 'last_name', 'email')
        # Creamos una lista de tuplas que van a contener a las personas
        detalles = [(user.username, user.first_name, user.last_name, user.email)
                    for user in User.objects.all()]
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles,
                              colWidths=[3 * cm, 4 * cm, 5 * cm, 5 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 7),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf,  0.75*inch, 7.5*inch)

    def tabla_calificacion(self, pdf, dict_calificacion, total_asignados):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Calificacion', 'Cantidad')
        # Creamos una lista de tuplas que van a contener a las personas

        detalles = [(calificaciones_nombre, calificaciones_cantidad)
                    for calificaciones_nombre, calificaciones_cantidad
                    in dict_calificacion]
        detalles.append(('Total asignados', total_asignados))
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles,
                              colWidths=[3 * cm, 4 * cm])
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
        pdf.drawString(0.75*inch, 740, u"Cantidad por calificacion")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf,  0.75*inch, 8.3*inch)
        archivo_imagen = settings.MEDIA_ROOT + \
                         '/imagenes/barra_campana_calificacion.png'

        pdf.drawImage(archivo_imagen, 4*inch, 7.5*inch, 250, 200,
                      preserveAspectRatio=True, mask="auto")

    def tabla_no_atendidos(self, pdf, dict_no_atendidos, total_no_atendidos):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Calificacion', 'Cantidad')
        # Creamos una lista de tuplas que van a contener a las personas

        detalles = [(resultado_nombre, resultado_cantidad)
                    for resultado_nombre,
                        resultado_cantidad in dict_no_atendidos]
        detalles.append(('Total no atendidos', total_no_atendidos))
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles,
                              colWidths=[3 * cm, 4 * cm])
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
        pdf.drawString(0.75*inch, 520, u"Cantidad de llamados no atendidos")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf,  0.75*inch, 5.8*inch)
        archivo_imagen = settings.MEDIA_ROOT + \
                         '/imagenes/barra_campana_no_atendido.png'

        pdf.drawImage(archivo_imagen, 4*inch, 4.5*inch, 250, 200,
                      preserveAspectRatio=True, mask="auto")

    def tabla_agente(self, pdf, agente_venta, calificaciones):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Agente', 'Ventas')
        nombre_calificaciones = [calificacion.nombre for calificacion in calificaciones]
        nombre_calificaciones = tuple(nombre_calificaciones)
        encabezados = encabezados + nombre_calificaciones

        # Creamos una lista de tuplas que van a contener a las personas

        detalles = []

        for agente in agente_venta:
            dato = [agente[0], agente[3]]
            for calificacion in calificaciones:
                for clave, valor in agente[2].items():
                    if calificacion.pk == clave:
                        dato.append(valor)
                        break

            detalles.append(tuple(dato))

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
        pdf.drawString(0.75*inch, 300, u"Calificaciones por agente")
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        # 0,75 mas cercano del margen derecho
        # 7.5 mas cercano del margen TOP
        detalle_orden.drawOn(pdf,  0.75*inch, 3*inch)

