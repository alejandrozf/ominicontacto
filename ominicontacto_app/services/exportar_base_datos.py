# -*- coding: utf-8 -*-

"""
Servicio de exportacion de base de datos de contactos para discador
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json


from django.conf import settings
from ominicontacto_app.utiles import crear_archivo_en_media_root
from django.utils.encoding import force_text
from ominicontacto_app.models import Contacto, Campana
from ominicontacto_app.services.base_de_datos_contactos import BaseDatosService
from ominicontacto_app.services.wombat_config import CampanaListContactoConfigFile

logger = logging.getLogger(__name__)


class ArchivoDeReporteCsv(object):
    def __init__(self, base_datos):
        self._base_datos = base_datos
        self.nombre_del_directorio = 'base_datos_contacto'
        self.prefijo_nombre_de_archivo = "{0}-exportar".format(
            self._base_datos.id)
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
                        "El archivo sera sobreescrito", self._base_datos.pk,
                        self.ruta)

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, contactos, metadata, campana, telefonos,
                             usa_contestador, prefijo_discador):

        with open(self.ruta, 'wb') as csvfile:
            nombres_de_columnas = metadata.nombres_de_columnas

            # Creamos encabezado
            encabezado = []
            encabezado.append("telefono")
            encabezado.append("pk_contacto")
            encabezado.append("campana")
            encabezado.append("timeout")
            encabezado.append("id_campana")
            encabezado.append("usa_contestador")
            encabezado.append("id_contacto")
            for columna in telefonos:
                encabezado.append(nombres_de_columnas[int(columna)])

            # Creamos csvwriter
            csvwiter = csv.writer(csvfile)

            # guardamos encabezado
            lista_encabezados_utf8 = [force_text(item).encode('utf-8')
                                      for item in encabezado]
            csvwiter.writerow(lista_encabezados_utf8)

            # Iteramos cada uno de los contactos, con los eventos de TODOS los intentos
            for contacto in contactos:
                lista_opciones = []

                # --- Buscamos datos
                lista_opciones.append(prefijo_discador + contacto.telefono)
                lista_opciones.append(contacto.pk)
                lista_opciones.append(campana.nombre)
                lista_opciones.append(campana.queue_campana.timeout)
                lista_opciones.append(campana.id)
                lista_opciones.append(usa_contestador)
                lista_opciones.append(contacto.pk)
                if contacto.datos:
                    datos = json.loads(contacto.datos)
                    for col_telefono in telefonos:
                        indice_columna_dato = int(col_telefono) - 7
                        lista_opciones.append(datos[indice_columna_dato])

                # --- Finalmente, escribimos la linea

                lista_opciones_utf8 = [force_text(item).encode('utf-8')
                                       for item in lista_opciones]
                csvwiter.writerow(lista_opciones_utf8)

    def ya_existe(self):
        return os.path.exists(self.ruta)


class ExportarBaseDatosContactosService(object):

    def crea_reporte_csv(self, base_datos, campana, telefonos, usa_contestador,
                         evitar_duplicados, evitar_sin_telefono,
                         prefijo_discador):
        archivo_de_reporte = ArchivoDeReporteCsv(base_datos)
        archivo_de_reporte.crear_archivo_en_directorio()

        if evitar_duplicados:
            service_base_datos = BaseDatosService()
            service_base_datos.eliminar_contactos_duplicados(base_datos)

        contactos = Contacto.objects.contactos_by_bd_contacto(base_datos)

        if evitar_sin_telefono:
            contactos = contactos.exclude(telefono__isnull=True).exclude(
                telefono__exact='')

        metadata = base_datos.get_metadata()
        campana = Campana.objects.get(pk=campana)
        archivo_de_reporte.escribir_archivo_csv(contactos, metadata, campana,
                                                telefonos, usa_contestador,
                                                prefijo_discador)

    def obtener_url_reporte_csv_descargar(self, base_datos):
        archivo_de_reporte = ArchivoDeReporteCsv(base_datos)
        if archivo_de_reporte.ya_existe():
            return archivo_de_reporte.url_descarga

        # Esto no debería suceder.
        logger.error("obtener_url_reporte_csv_descargar(): NO existe archivo"
                     " CSV de descarga para la base de datos %s", base_datos.pk)
        assert os.path.exists(archivo_de_reporte.url_descarga)


class SincronizarBaseDatosContactosService(object):

    def __init__(self):
        self._campana_list_contacto_config_file = CampanaListContactoConfigFile()

    def crear_lista(self, campana, telefonos, usa_contestador,
                    evitar_duplicados, evitar_sin_telefono, prefijo_discador):

        base_datos = campana.bd_contacto

        # no tiene sentido ya que esto hace un filtro por pk
        if evitar_duplicados:
            service_base_datos = BaseDatosService()
            service_base_datos.eliminar_contactos_duplicados(base_datos)

        contactos = Contacto.objects.contactos_by_bd_contacto(base_datos)

        if evitar_sin_telefono:
            contactos = contactos.exclude(telefono__isnull=True).exclude(
                telefono__exact='')

        metadata = base_datos.get_metadata()

        lista_contacto = self.escribir_lista(contactos, metadata, campana,
                                             telefonos, usa_contestador,
                                             prefijo_discador)

        logger.info("Creando archivo para asociacion lista %s campana",
                    campana.nombre)

        self._campana_list_contacto_config_file.write(lista_contacto)
        #return lista_contacto

    def escribir_lista(self, contactos, metadata, campana, telefonos,
                             usa_contestador, prefijo_discador):

        nombres = metadata.nombres_de_columnas
        nombres.remove('telefono')
        list_multinum = []
        for columna in nombres:
            if "MULTINUM" in columna:
                list_multinum.append((columna, nombres.index(columna)))

        lista_contactos = "numbers="
        for contacto in contactos:
            dato_contacto = ""

            # --- Buscamos datos
            dato_contacto += prefijo_discador + contacto.telefono + ","
            dato_contacto += "id_cliente:" + str(contacto.pk) + ","
            dato_contacto += "campana:" + campana.nombre + ","
            dato_contacto += "timeout:" + str(campana.queue_campana.wait)
            dato_contacto += ",id_campana:" + str(campana.id) + ","
            dato_contacto += "usa_contestador:" + str(usa_contestador)
            if list_multinum:
                datos = json.loads(contacto.datos)
                for item in list_multinum:
                    dato_contacto += "," + item[0] + ":" + datos[item[1]]
            dato_contacto += "|"

            lista_contactos += dato_contacto

        return lista_contactos

