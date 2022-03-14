# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
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

from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, \
    OmlError, OmlParserMaxRowError, OmlParserCsvImportacionError
from ominicontacto_app.models import ContactoBlacklist
from ominicontacto_app.parser import ParserCsv

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
            raise(OmlArchivoImportacionInvalidoError(file_invalid_msg))
        file_obj = codecs.iterdecode(
            black_list.archivo_importacion, 'utf-8', errors='ignore')
        data = csv.reader(file_obj, skipinitialspace=True)
        validar_estructura_csv(data, file_invalid_msg, logger)

    def importa_contactos(self, blacklist):
        """
        Segundo paso de la creación de una Blacklist.
        Este método se encarga de generar los objectos Contacto por cada linea
        del archivo de importación especificado para la base de datos de
        contactos.
        """

        parser = ParserCsv()

        try:
            estructura_archivo = parser.get_estructura_archivo(blacklist)
            cantidad_contactos = 0
            contactos_repetidos = False
            if blacklist.cantidad_contactos:
                cantidad_contactos = blacklist.cantidad_contactos
            for lista_dato in estructura_archivo[1:]:
                if ContactoBlacklist.objects.filter(telefono=lista_dato[0]).count() == 0:
                    cantidad_contactos += 1
                    ContactoBlacklist.objects.create(
                        telefono=lista_dato[0],
                        black_list=blacklist,
                    )
                else:
                    contactos_repetidos = True
        except OmlParserMaxRowError:
            blacklist.elimina_contactos()
            raise

        except OmlParserCsvImportacionError:
            blacklist.elimina_contactos()
            raise

        blacklist.cantidad_contactos = cantidad_contactos
        blacklist.save()
        return contactos_repetidos


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
            raise(NoSePuedeInferirMetadataError(_("Se deben proveer al menos 2 "
                                                  "lineas para poder inferir "
                                                  "los metadatos")))

        # Primero chequeamos q' haya igual cant. de columnas
        set_cant_columnas = set([len(linea) for linea in lineas])
        if len(set_cant_columnas) != 1:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise(NoSePuedeInferirMetadataError(_("Las lineas recibidas "
                                                  "poseen distintas cantidades "
                                                  "de columnas")))

        primer_linea = lineas[0]

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError(_("Las lineas no poseen ninguna "
                                                  "columna")))

        if str(primer_linea[0]).lower() != 'telefono':
            raise (NoSePuedeInferirMetadataErrorEncabezado(_("El nombre de la primera "
                                                             "columna debe ser telefono")))
