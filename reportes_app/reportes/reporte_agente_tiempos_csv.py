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

"""
Servicio para generar reporte csv de las reportes de los agentes
"""

from __future__ import unicode_literals

import csv
import logging
import os
import datetime

from django.conf import settings
from django.utils.translation import gettext as _

from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text


logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, nombre_reporte):
        self._nombre_reporte = nombre_reporte
        hoy_ahora = datetime.datetime.today()
        hoy = hoy_ahora.date()
        self.nombre_del_directorio = 'reporte_agente'
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
            logger.warn(_("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                          "reporte para la campana {0}. Archivo: {1}. "
                          "El archivo sera sobreescrito".format(self._nombre_reporte,
                                                                self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_tiempos_csv(self, estadisticas):

        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Agente"))
            encabezado.append(_("Tiempo de sesion"))
            encabezado.append(_("Tiempo de hold"))
            encabezado.append(_("Tiempo de pausa"))
            encabezado.append(_("Tiempos en llamada"))
            encabezado.append(_("Porcentaje en llamada"))
            encabezado.append(_("Porcentaje en pausa"))
            encabezado.append(_("Porcentaje en espera"))
            encabezado.append(_("Cantidad de llamadas procesadas"))
            encabezado.append(_("Transferidas a Agente"))
            encabezado.append(_("Tiempo promedio de llamadas"))
            encabezado.append(_("Cantidad de intentos fallidos"))
            encabezado.append(_("Entrantes No Atendidas"))
            encabezado.append(_("Entrantes Rechazadas"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item) for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for agente in estadisticas["agentes_tiempos"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(agente.get_nombre_agente())
                tiempo_sesion = "Ohs"
                if agente.get_string_tiempo_sesion():
                    tiempo_sesion = agente.get_string_tiempo_sesion() + "hs"
                lista_opciones.append(tiempo_sesion)
                tiempo_hold = "0hs"
                if agente.get_string_tiempo_hold():
                    tiempo_hold = agente.get_string_tiempo_hold() + "hs"
                lista_opciones.append(tiempo_hold)
                tiempo_pausa = "Ohs"
                if agente.get_string_tiempo_pausa():
                    tiempo_pausa = agente.get_string_tiempo_pausa() + "hs"
                lista_opciones.append(tiempo_pausa)
                tiempo_llamada = str(agente.tiempo_llamada) + "hs"
                lista_opciones.append(tiempo_llamada)
                porcentaje_llamada = "O%"
                if agente.tiempo_porcentaje_llamada:
                    porcentaje_llamada = str(round(agente.tiempo_porcentaje_llamada, 2)) + "%"
                lista_opciones.append(porcentaje_llamada)
                porcentaje_pausa = "O%"
                if agente.tiempo_porcentaje_pausa:
                    porcentaje_pausa = str(round(agente.tiempo_porcentaje_pausa, 2)) + "%"
                lista_opciones.append(porcentaje_pausa)
                porcentaje_wait = "O%"
                if agente.tiempo_porcentaje_wait:
                    porcentaje_wait = str(round(agente.tiempo_porcentaje_wait, 2)) + "%"
                lista_opciones.append(porcentaje_wait)
                lista_opciones.append(agente.cantidad_llamadas_procesadas)
                lista_opciones.append(agente.transferidas_a_agente)
                lista_opciones.append(str(agente.get_promedio_llamadas()) + "s")
                lista_opciones.append(agente.cantidad_intentos_fallidos)
                lista_opciones.append(agente.cantidad_entrantes_no_atendidas)
                lista_opciones.append(agente.cantidad_entrantes_rechazadas)

                # --- Finalmente, escribimos la linea
                lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_pausas_csv(self, estadisticas):

        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Agente"))
            encabezado.append(_("Pausa"))
            encabezado.append(_("Tipo de pausa"))
            encabezado.append(_("Tiempo de pausa"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item) for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for agente in estadisticas["agente_pausa"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(agente['nombre_agente'])
                lista_opciones.append(agente['pausa'])
                lista_opciones.append(agente['tipo_de_pausa'])
                lista_opciones.append(agente['tiempo'] + "hs")

                # --- Finalmente, escribimos la linea
                lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_llamadas_csv(self, estadisticas):

        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Agente"))
            encabezado.append(_("Cola"))
            encabezado.append(_("Tiempo de llamadas"))
            encabezado.append(_("Cantidad de llamadas procesadas"))
            encabezado.append(_("Transferidas a agente"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item) for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for agente in estadisticas["count_llamada_campana"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(agente['agente'])
                lista_opciones.append(agente['campana'])
                lista_opciones.append(agente['tiempo_llamadas'] + "hs")
                lista_opciones.append(agente['llamadas_procesadas'])
                lista_opciones.append(agente['transferidas_a_agente'])

                # --- Finalmente, escribimos la linea
                lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def escribir_archivo_llamadas_tipo_csv(self, estadisticas):

        with open(self.ruta, 'w', newline='', encoding='utf-8') as csvfile:
            # Creamos encabezado
            encabezado = []

            encabezado.append(_("Agente"))
            encabezado.append(_("Total"))
            encabezado.append(_("ICS"))
            encabezado.append(_("DIALER"))
            encabezado.append(_("INBOUND"))
            encabezado.append(_("MANUAL"))
            encabezado.append(_("TRANSFERIDAS A AGENTE"))
            encabezado.append(_("TRANSFERIDAS A CAMPAÑA"))
            encabezado.append(_("TRANSFERIDAS A CX SURVEY"))
            encabezado.append(_("FUERA DE CAMPAÑA"))

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item) for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de las metadata de la gestion del formulario
            for (agente, total_campana, total_ics, total_dialer, total_inbound,
                 total_manual, total_transferidas_agente, total_transferidas_campana,
                 total_transferidas_encuesta, total_fuera_campana
                 ) in estadisticas["dict_agente_counter"]:
                lista_opciones = []

                # --- Buscamos datos

                lista_opciones.append(agente)
                lista_opciones.append(total_campana)
                lista_opciones.append(total_ics)
                lista_opciones.append(total_dialer)
                lista_opciones.append(total_inbound)
                lista_opciones.append(total_manual)
                lista_opciones.append(total_transferidas_agente)
                lista_opciones.append(total_transferidas_campana)
                lista_opciones.append(total_transferidas_encuesta)
                lista_opciones.append(total_fuera_campana)

                # --- Finalmente, escribimos la linea
                lista_opciones_utf8 = [force_text(item) for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ReporteAgenteCSVService(object):

    def crea_reporte_csv(self, estadisticas):

        # Reporte de tiempos de agente
        archivo_de_reporte = ArchivoDeReporteCsv("tiempos_agentes")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_tiempos_csv(estadisticas)

        # Reporte de tiempos de pausa de los agentes
        archivo_de_reporte = ArchivoDeReporteCsv("pausas_agentes")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_pausas_csv(estadisticas)

        # Reporte de tiempos de llamadas de los agentes
        archivo_de_reporte = ArchivoDeReporteCsv("llamadas_agentes")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_llamadas_csv(estadisticas)

        # Reporte de cantidad de llamadas por tipo de los agentes
        archivo_de_reporte = ArchivoDeReporteCsv("llamadas_tipo_agentes")
        archivo_de_reporte.crear_archivo_en_directorio()
        archivo_de_reporte.escribir_archivo_llamadas_tipo_csv(estadisticas)

    def obtener_url_reporte_csv_descargar(self, nombre_reporte):

        archivo_de_reporte = ArchivoDeReporteCsv(nombre_reporte)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error(_("obtener_url_reporte_csv_descargar(): NO existe archivo"
                       " CSV de descarga para la campana {0}".format(nombre_reporte)))
        assert os.path.exists(archivo_de_reporte.url_descarga)
