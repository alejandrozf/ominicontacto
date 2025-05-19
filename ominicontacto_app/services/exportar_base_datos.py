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
Servicio para exportar la batos a un csv y para generar la lista en una archivo
para insertar en wombat
"""

from __future__ import unicode_literals

import csv
import logging
import os
import json

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import gettext as _

from ominicontacto_app.utiles import crear_archivo_en_media_root
from ominicontacto_app.models import Contacto
from ominicontacto_app.services.base_de_datos_contactos import BaseDatosService
from ominicontacto_app.services.dialer.wombat_config import CampanaListContactoConfigFile

logger = logging.getLogger(__name__)


# TODO: Verificar si este archivo se usa en algun momento
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
            logger.warn(_("ArchivoDeReporteCsv: Ya existe archivo CSV de "
                          "reporte para la campana {0}. Archivo: {1}. "
                          "El archivo sera sobreescrito".format(self._base_datos.pk, self.ruta)))

        crear_archivo_en_media_root(
            self.nombre_del_directorio,
            self.prefijo_nombre_de_archivo,
            self.sufijo_nombre_de_archivo)

    def escribir_archivo_csv(self, contactos, metadata, campana, telefonos,
                             usa_contestador, prefijo_discador):

        with open(self.ruta, 'wb', encoding='utf-8') as csvfile:
            nombres_de_columnas = metadata.nombres_de_columnas

            # Creamos encabezado
            encabezado = []
            encabezado.append(_("telefono"))
            encabezado.append(_("pk_contacto"))
            encabezado.append(_("campana"))
            encabezado.append(_("timeout"))
            encabezado.append(_("id_campana"))
            encabezado.append(_("usa_contestador"))
            encabezado.append(_("id_contacto"))
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


class SincronizarBaseDatosContactosService(object):

    def __init__(self):
        self._campana_list_contacto_config_file = CampanaListContactoConfigFile()

    def crear_lista(self, campana, evitar_duplicados, evitar_sin_telefono, prefijo_discador):

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

        lista_contacto = self.escribir_lista(contactos, metadata, campana, prefijo_discador)
        logger.info(_("Creando archivo para asociacion lista {0} campana".format(campana.nombre)))

        self._campana_list_contacto_config_file.write(lista_contacto)
        # return lista_contacto

    def escribir_lista(self, contactos, metadata, campana, prefijo_discador):

        list_multinum = []
        n_multinum = 0
        # Itero por los otros campos con telefonos (menos el primero que esta en contacto.telefono)
        indices_telefonos = metadata.columnas_con_telefono[1:]
        for indice in indices_telefonos:
            n_multinum += 1
            # El indice indica cual es la posicion en la lista de "nombres" de las columnas
            # Como en la lista de "datos" no aparece el primer telefono, le resto 1 a la posicion
            posicion_en_datos = indice - 1
            if metadata.columna_id_externo is not None:
                if indice > metadata.columna_id_externo:
                    posicion_en_datos -= 1
            list_multinum.append(('MULTINUM' + str((n_multinum)), posicion_en_datos))

        lista_contactos = "numbers="
        for contacto in contactos:
            dato_contacto = []
            # --- Buscamos datos
            dato_contacto.append(prefijo_discador + contacto.telefono)
            dato_contacto.append("id_cliente:" + str(contacto.pk))
            dato_contacto.append("id_campana:" + str(campana.id))
            if list_multinum:
                datos = json.loads(contacto.datos)
                for nombre, posicion_en_datos in list_multinum:
                    dato_contacto.append(nombre + ":" + datos[posicion_en_datos])

            lista_contactos += ",".join(dato_contacto) + "|"

        return lista_contactos
