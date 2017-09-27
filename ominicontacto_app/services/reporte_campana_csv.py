# -*- coding: utf-8 -*-

"""
Servicio para generar reporte csv de las reportes de los agentes
"""

from __future__ import unicode_literals

import os
import datetime
import logging

from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text

logger = logging.getLogger(__name__)


def obtener_datos_total_llamadas_csv(encabezado, datos_reporte):

    # Obtenemos datos del resto de las filas
    datos = []

    datos.append("")

    datos.append(["Total llamadas procesadas por OmniLeads",
                  force_text(datos_reporte['total_llamadas_ingresadas'])])

    datos.append("")

    datos.append(["Total de llamadas Salientes Discador",
                  force_text(datos_reporte['llamadas_ingresadas_dialer'])])
    datos.append(["Cantidad de llamadas gestionadas",
                  force_text(datos_reporte['llamadas_gestionadas_dialer'])])
    datos.append(["Cantidad de llamadas perdidas",
                  force_text(datos_reporte['llamadas_perdidas_dialer'])])

    datos.append("")

    datos.append(["Total llamadas Entrantes",
                  force_text(datos_reporte['llamadas_ingresadas_entrantes'])])
    datos.append(["Cantidad de llamadas atendidas",
                  force_text(datos_reporte['llamadas_atendidas_entrantes'])])
    datos.append(["Cantidad de llamadas expiradas",
                  force_text(datos_reporte['llamadas_expiradas_entrantes'])])
    datos.append(["Cantidad de llamadas abandonadas",
                  force_text(datos_reporte['llamadas_abandonadas_entrantes'])])

    datos.append("")

    datos.append(["Total llamadas Salientes Manuales",
                  force_text(datos_reporte['llamadas_ingresadas_manuales'])])
    datos.append(["Cantidad de llamadas atendidas",
                  force_text(datos_reporte['llamadas_atendidas_manuales'])])
    datos.append(["Cantidad de llamadas abandonadas",
                  force_text(datos_reporte['llamadas_abandonadas_manuales'])])

    filas = [encabezado] + datos

    return filas


def obtener_llamadas_campanas(encabezado, datos_reporte):
    """
    Devuelve el contenido del reporte a csv de una de las tablas de cantidad de llamadas
    de cada campaña por tipo de campaña
    """

    # obtenemos resto de las filas
    datos_reporte_text = []

    for fila_datos in datos_reporte['filas_datos']:
        datos_reporte_text.append([force_text(item) for item in fila_datos])

    filas_csv = [encabezado] + datos_reporte_text

    return filas_csv


class ArchivoDeReporteCsv(object):  # TODO: revisar si deprecar o eliminar esta clase
    def __init__(self, nombre_reporte):
        self._nombre_reporte = nombre_reporte
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
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

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteCampanaCSVService(object):  # TODO: revisar si deprecar o eliminar esta clase

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
        # assert campana.estado == Campana.ESTADO_DEPURADA

        archivo_de_reporte = ArchivoDeReporteCsv(nombre_reporte)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la campana %s", nombre_reporte)
        assert os.path.exists(archivo_de_reporte.url_descarga)
