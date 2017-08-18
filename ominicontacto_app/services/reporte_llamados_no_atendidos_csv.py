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
    def __init__(self, campana):
        self._campana = campana
        self.nombre_del_directorio = 'reporte_campana'
        self.prefijo_nombre_de_archivo = "{0}-reporte_llamadas".format(
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
                        "reporte para la campana %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._campana.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, no_atendidos, contestador):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Telefono")
            encabezado.append("Estado")

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for contacto in no_atendidos:
                lista_opciones = []

                # --- Buscamos datos
                estado = ""
                valido = False
                if contacto.estado == "RS_LOST" and contacto.calificacion == "":
                    estado = "Agente no disponible"
                    valido = True
                elif contacto.estado == "RS_BUSY":
                    estado = "Ocupado"
                    valido = True
                elif contacto.estado == "RS_NOANSWER":
                    estado = "No contesta"
                    valido = True
                elif contacto.estado == "RS_NUMBER":
                    estado = "Numero erroneo"
                    valido = True
                elif contacto.estado == "RS_ERROR":
                    estado = "Error de sistema"
                    valido = True
                elif contacto.estado == "RS_REJECTED":
                    estado = "Congestion"
                    valido = True
                if valido:
                    lista_opciones.append(contacto.telefono)
                    lista_opciones.append(estado)

                    # --- Finalmente, escribimos la linea

                    lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                           for item in lista_opciones]
                    csvwiter.writerow(lista_opciones_utf8)

            for contacto in contestador:
                lista_opciones = []

                # --- Buscamos datos
                lista_opciones.append(contacto.telefono)
                lista_opciones.append("Contestador Detectado")

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaCSVService(object):

    def crea_reporte_csv(self, campana, fecha_desde, fecha_hasta):
        # Reporte de distribucion campana
        archivo_de_reporte = ArchivoDeReporteCsv(campana)
        archivo_de_reporte.crear_archivo_en_directorio()
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        no_atendidos = self._obtener_listado_no_atendidos_fecha(campana, fecha_desde,
                                                                fecha_hasta)
        contestador = self._obtener_listado_contestador_fecha(campana, fecha_desde,
                                                              fecha_hasta)

        archivo_de_reporte.escribir_archivo_csv(no_atendidos, contestador)

    def obtener_url_reporte_csv_descargar(self, campana):
        #assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteCsv(campana)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la campana %s", nombre_reporte)
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def _obtener_listado_no_atendidos_fecha(self, campana, fecha_desde, fecha_hasta):
        return campana.logswombat.filter(
            fecha_hora__range=(fecha_desde, fecha_hasta))

    def _obtener_listado_contestador_fecha(self, campana, fecha_desde, fecha_hasta):
        return campana.logswombat.filter(fecha_hora__range=(fecha_desde, fecha_hasta),
                                         estado="TERMINATED", calificacion='CONTESTADOR')