# -*- coding: utf-8 -*-

"""
Servicio de reportes de campanas
"""

from __future__ import unicode_literals

import csv
import logging
import os
import datetime
import json

from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text


logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, agente):
        self._agente = agente
        self.nombre_del_directorio = 'reporte_agente'
        self.prefijo_nombre_de_archivo = "{0}-reporte_calificacion".format(
            self._agente.id)
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
                        "reporte para el agente %s. Archivo: %s. "
                        "El archivo sera sobreescrito", self._agente.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, calificaciones):

        with open(self.ruta, 'wb') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append("Telefono")
            encabezado.append("Id Cliente")
            encabezado.append("Es una venta")
            encabezado.append("Calificacion No venta")
            encabezado.append("Observaciones")
            encabezado.append("datos del cliente")



            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de los contactos, con los eventos de TODOS los intentos
            for calificacion in calificaciones:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(calificacion.contacto.telefono)
                lista_opciones.append(calificacion.contacto.id_cliente)

                if calificacion.es_venta:
                    lista_opciones.append("SI")
                else:
                    lista_opciones.append("NO")
                if calificacion.calificacion:
                    lista_opciones.append(calificacion.calificacion.nombre)
                else:
                    lista_opciones.append("N/A")
                lista_opciones.append(calificacion.observaciones)
                datos = json.loads(calificacion.contacto.datos)
                for dato in datos:
                    lista_opciones.append(dato)
                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteAgenteService(object):

    def crea_reporte_csv(self, agente, fecha_desde, fecha_hasta):
        #assert campana.estado == Campana.ESTADO_ACTIVA

        archivo_de_reporte = ArchivoDeReporteCsv(agente)

        archivo_de_reporte.crear_archivo_en_directorio()

        calificaciones = self._obtener_listado_calificaciones_fecha(agente,
                                                                    fecha_desde,
                                                                    fecha_hasta)

        archivo_de_reporte.escribir_archivo_csv(calificaciones)

    def obtener_url_reporte_csv_descargar(self, agente):
        #assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteCsv(agente)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para el agente %s", agente.pk)
        assert os.path.exists(archivo_de_reporte.url_descarga)

    def _obtener_listado_calificaciones_fecha(self, agente,fecha_desde,
                                              fecha_hasta):
        fecha_desde = datetime.datetime.combine(fecha_desde, datetime.time.min)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, datetime.time.max)
        return agente.calificaciones.filter(fecha__range=(fecha_desde,
                                                          fecha_hasta))
