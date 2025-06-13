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
Servicio encargado de validar y crear las listas negras
OJO: servicio copiado del modulo base_de_datos_contactos
"""

from __future__ import unicode_literals

import codecs
import csv
import logging
import os

from django.db import connection
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, OmlError

from utiles_globales import validar_estructura_csv


logger = logging.getLogger(__name__)


class CreacionBlacklistService(object):

    def genera_black_list(self, black_list):
        """
        Primer paso de la creación de una Blacklist.

        Este método se encarga de validar los datos para la creación del
        del objeto y llevar a cabo el guardado del mismo.

        Valida:
            Que el archivo subido para importar la base de datos de contactos
            sea y tenga las características válidas.
            Si el archivo es válido, hace el save del objeto y si no los es
            lanza la excepción correspondiente.
        """

        csv_extensions = ['.csv']

        file_invalid_msg = _("El archivo especificado para realizar la importación de contactos "
                             "no es válido.")
        filename = black_list.nombre_archivo_importacion
        extension = os.path.splitext(filename)[1].lower()
        if extension not in csv_extensions:
            logger.warn(_("La extension {0} no es CSV. ".format(extension)))
            raise OmlArchivoImportacionInvalidoError(file_invalid_msg)
        file_obj = codecs.iterdecode(
            black_list.archivo_importacion, 'utf-8', errors='ignore')
        data = csv.reader(file_obj, skipinitialspace=True)
        validar_estructura_csv(data, file_invalid_msg, logger)

    def forzar_borrado_completo(self, object=None):
        """ Borra la blacklist """

        if object is None:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM ominicontacto_app_contactoblacklist;')
                cursor.execute('DELETE FROM ominicontacto_app_blacklist;')
        else:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM ominicontacto_app_contactoblacklist WHERE '
                               f'black_list_id={object.id}')
                object.delete()

    def importa_contactos(self, blacklist):
        """
        Segundo paso de la creación de una Blacklist.
        Importa los contactos directamente a la BD ignorando conflictos por repetidos
        """
        file = blacklist.archivo_importacion.file.name
        with connection.cursor() as cursor:
            # 1. Crear tabla temporal sin índice
            cursor.execute("""
                CREATE TEMP TABLE tmp_telefonos (
                    telefono TEXT
                ) ON COMMIT DROP;
            """)

            # 2. Cargar el archivo CSV a la tabla temporal
            with open(file, 'r') as f:
                cursor.copy_expert("COPY tmp_telefonos (telefono) FROM STDIN WITH CSV", f)

            # 3. Insertar en la tabla real, asociando el ID de blacklist, ignorando conflictos
            cursor.execute("""
                INSERT INTO ominicontacto_app_contactoblacklist (telefono, black_list_id)
                SELECT DISTINCT telefono, %s
                FROM tmp_telefonos
                ON CONFLICT (telefono) DO NOTHING;
            """, [blacklist.id])


class NoSePuedeInferirMetadataErrorFormatoFilas(OmlError):
    """Indica que las filas no tienen el formato adecuado"""
    pass


class NoSePuedeInferirMetadataError(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class NoSePuedeInferirMetadataErrorEncabezado(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class ValidaDataService(object):

    def valida_datos_desde_lineas(self, lineas_unsafe):
        """Infiere los metadatos desde las lineas pasadas por parametros.
        """
        try:
            assert isinstance(lineas_unsafe, (list, tuple))
        except AssertionError:
            raise NoSePuedeInferirMetadataErrorFormatoFilas(
                _("Archivo .csv con problemas de estructura"))

        lineas = []
        for linea in lineas_unsafe:
            lineas.append(
                [smart_text(col) for col in linea]
            )
        del lineas_unsafe

        logger.debug("inferir_metadata_desde_lineas(): %s", lineas)

        if len(lineas) < 2:
            logger.debug("Se deben proveer al menos 2 lineas: %s", lineas)
            raise NoSePuedeInferirMetadataError(_("Se deben proveer al menos 2 "
                                                  "lineas para poder inferir "
                                                  "los metadatos"))

        # Primero chequeamos q' haya igual cant. de columnas
        set_cant_columnas = set([len(linea) for linea in lineas])
        if len(set_cant_columnas) != 1:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise NoSePuedeInferirMetadataError(_("Las lineas recibidas "
                                                  "poseen distintas cantidades "
                                                  "de columnas"))

        primer_linea = lineas[0]

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise NoSePuedeInferirMetadataError(_("Las lineas no poseen ninguna "
                                                  "columna"))

        # if str(primer_linea[0]).lower() != 'telefono':
        #     raise (NoSePuedeInferirMetadataErrorEncabezado(_("El nombre de la primera "
        #                                                      "columna debe ser telefono")))
