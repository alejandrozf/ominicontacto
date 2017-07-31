# -*- coding: utf-8 -*-

"""
Servicio para generar reporte csv de las reportes de los agentes
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json
import datetime

from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text


logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, nombre_reporte):
        self._nombre_reporte = nombre_reporte
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        hoy
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-{1}".format(hoy, nombre_reporte)
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
                        "reporte para la campana %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._nombre_reporte,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_distribucion_campana_csv(self, estadisticas):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Campana")
            encabezado.append("Recibidas")
            encabezado.append("Atendidas")
            encabezado.append("Expiradas")
            encabezado.append("Abandonadas")
            encabezado.append("Manuales")
            encabezado.append("Manuales atendidas")
            encabezado.append("Manuales no atendidas")


            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for campana in estadisticas["estadisticas"]["queues_llamadas"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(campana[0])
                lista_opciones.append(campana[1])
                lista_opciones.append(campana[2])
                lista_opciones.append(campana[3])
                lista_opciones.append(campana[4])
                lista_opciones.append(campana[5])
                lista_opciones.append(campana[6])
                lista_opciones.append(campana[7])

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_total_llamadas_csv(self, estadisticas):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Total llamadas")
            encabezado.append("Cantidad")

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)


            lista_opciones = []
            lista_opciones.append("Numero de llamadas recibidas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][0])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas atendidas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][1])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas expiradas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][2])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas abandonadas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][3])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas salientes")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][4])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas salients atendidas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][5])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Numero de llamadas salientes abandonadas")
            lista_opciones.append(estadisticas["estadisticas"]["total_llamadas"][6])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_llamadas_tipo_csv(self, estadisticas):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Cantidades Tipo")
            encabezado.append("Totales")

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            lista_opciones = []
            lista_opciones.append("Cantidad Total Dialer")
            lista_opciones.append(estadisticas["estadisticas"]["total_dialer"])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Cantidad Total Ics")
            lista_opciones.append(estadisticas["estadisticas"]["total_ics"])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Cantidad Total Inbound")
            lista_opciones.append(estadisticas["estadisticas"]["total_inbound"])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

            lista_opciones = []
            lista_opciones.append("Cantidad Total Manual")
            lista_opciones.append(estadisticas["estadisticas"]["total_manual"])

            lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                    for item in lista_opciones]
            csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_llamadas_campana_csv(self, estadisticas):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Campana")
            encabezado.append("Total")
            encabezado.append("ICS")
            encabezado.append("DIALER")
            encabezado.append("INBOUND")
            encabezado.append("MANUAL")

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for campana, total_campana, total_ics, total_dialer, total_inbound, total_manual in estadisticas["dict_campana_counter"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(campana)
                lista_opciones.append(total_campana)
                lista_opciones.append(total_ics)
                lista_opciones.append(total_dialer)
                lista_opciones.append(total_inbound)
                lista_opciones.append(total_manual)

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaCSVService(object):

    def crea_reporte_csv(self, estadisticas):

        # Reporte de distribucion campana
        archivo_de_reporte = ArchivoDeReporteCsv("distribucion_campana")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_distribucion_campana_csv(estadisticas)

        # Reporte de total de llamadas
        archivo_de_reporte = ArchivoDeReporteCsv("total_llamadas")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_total_llamadas_csv(estadisticas)

        # Reporte de totales llamadas por tipo
        archivo_de_reporte = ArchivoDeReporteCsv("llamadas_tipo")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_llamadas_tipo_csv(estadisticas)

        # Reporte de cantidad de llamadas por tipo de los agentes
        archivo_de_reporte = ArchivoDeReporteCsv("llamadas_campana")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_llamadas_campana_csv(estadisticas)

    def obtener_url_reporte_csv_descargar(self, nombre_reporte):
        #assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteCsv(nombre_reporte)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la campana %s", nombre_reporte)
        assert os.path.exists(archivo_de_reporte.url_descarga)
