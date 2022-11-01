
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

from __future__ import unicode_literals

from django.utils.encoding import smart_text
from django.utils.translation import gettext as _
from django.contrib import messages

from ominicontacto_app.errors import (OmlArchivoImportacionInvalidoError, OmlError,
                                      OmlParserMaxRowError, OmlParserCsvImportacionError,
                                      OmlParserCsvDelimiterError, OmlParserMinRowError,
                                      OmlParserOpenFileError, OmlParserRepeatedColumnsError)
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.models import ListasRapidas, ContactoListaRapida
from ominicontacto_app.utiles import elimina_tildes
from ominicontacto_app.services.base_de_datos_contactos import PredictorMetadataService

import codecs
import csv
import os
import logging
import re

logger = logging.getLogger(__name__)


class ListaRapidaService(object):

    def __init__(self) -> None:
        self.parser = None
        self.legacy_parser = ParserCsv()

    def inferir_metadata(self, estructura_archivo):
        try:
            predictor_metadata = PredictorMetadataService()
            return predictor_metadata.inferir_metadata_desde_lineas(
                estructura_archivo, permitir_ext_pbx=True)
        except Exception as e:
            raise(NoSePuedeInferirMetadataError(e))

    def _existe_lista_rapida(self, nombre) -> bool:
        return ListasRapidas.objects.filter(nombre=nombre).exists()

    def genera_lista_rapida(self, lista_rapida):

        nombre_archivo = lista_rapida.nombre_archivo_importacion
        archivo = lista_rapida.archivo_importacion
        self.parser = ListaRapidaArchivoCSVParser(nombre_archivo, archivo)

        if not self.parser.es_valida_extension() or not self.parser.es_valido_archivo():
            file_invalid_msg = _("El archivo especificado para realizar la importación de "
                                 "contactos no es válido.")
            raise(OmlArchivoImportacionInvalidoError(file_invalid_msg))

    def importa_contactos(self, lista_rapida):

        parser = ParserCsv()

        try:
            estructura_archivo = parser.get_estructura_archivo(lista_rapida)
            cantidad_contactos = 0
            if lista_rapida.cantidad_contactos:
                cantidad_contactos = lista_rapida.cantidad_contactos
            for lista_dato in estructura_archivo[1:]:
                cantidad_contactos += 1
                ContactoListaRapida.objects.create(
                    nombre=lista_dato[0],
                    telefono=lista_dato[1],
                    lista_rapida=lista_rapida,
                )
        except OmlParserMaxRowError:
            lista_rapida.elimina_contactos()
            raise

        except OmlParserCsvImportacionError:
            lista_rapida.elimina_contactos()
            raise

        lista_rapida.cantidad_contactos = cantidad_contactos
        lista_rapida.save()

    def crea_lista_rapida(self, archivo, nombre_archivo, nombre_lista):
        """ Creacion de la lista rapida en el modelo
        """
        if self._existe_lista_rapida(nombre_lista):
            raise(OmlError(_("Ya existe una lista rapida de contactos con ese nombre")))

        model_lista_rapida = ListasRapidas()

        model_lista_rapida.archivo_importacion = archivo
        model_lista_rapida.nombre_archivo_importacion = nombre_archivo
        model_lista_rapida.nombre = nombre_lista
        model_lista_rapida.save()

        return model_lista_rapida.id


class ListaRapidaArchivoCSVParser(object):

    def __init__(self, nombre_archivo, archivo) -> None:
        self.nombre_archivo = nombre_archivo
        self.extension_archivo = os.path.splitext(nombre_archivo)[1].lower()
        self.columnas = {}
        self.archivo_str = codecs.iterdecode(archivo, 'utf-8', errors='ignore')

    def es_valida_extension(self) -> bool:
        return self.extension_archivo == ".csv"

    def es_valido_archivo(self) -> bool:
        return csv.Sniffer().has_header(self.archivo_str.__str__())

    def headers_no_repetidos(self) -> bool:
        headers = next(csv.reader(self.archivo_str))
        headers_set = set([self._sanear_nombre_de_columna(x) for x in headers])
        self.columnas = headers_set
        return len(headers) == len(headers_set)

    def _sanear_nombre_de_columna(self, nombre):
        """Realiza saneamiento básico del nombre de la columna. Con basico
        se refiere a:
        - eliminar trailing spaces
        - NO pasar a mayusculas
        - reemplazar espacios por '_'
        - eliminar tildes

        Los caracteres invalidos NO son borrados.
        """
        nombre = smart_text(nombre)
        nombre = nombre.strip()
        nombre = DOUBLE_SPACES.sub("_", nombre)
        nombre = elimina_tildes(nombre)
        return nombre


DOUBLE_SPACES = re.compile(r' +')


class NoSePuedeInferirMetadataErrorFormatoFilas(OmlError):
    """Indica que las filas no tienen el formato adecuado"""
    pass


class NoSePuedeInferirMetadataError(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class NoSePuedeInferirMetadataErrorEncabezado(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class ContactoExistenteError(OmlError):
    """este contacto con este id de cliente ya existe"""
    pass


class ValidaListaRapidaService(object):

    def _obtiene_previsualizacion_archivo(self, lista_rapida, previsualizacion=True):
        """
        Instancia el servicio ParserCsv e intenta obtener un resumen de las
        primeras 3 lineas del csv.
        """
        try:
            parser = ParserCsv()
            estructura_archivo = parser.previsualiza_archivo(
                lista_rapida, previsualizacion)

        except OmlParserCsvDelimiterError:
            message = _('<strong>Operación Errónea!</strong> '
                        'No se pudo determinar el delimitador a ser utilizado '
                        'en el archivo csv. No se pudo llevar a cabo el procesamiento '
                        'de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserMinRowError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó posee menos de 3 filas. '
                        'No se pudo llevar a cabo el procesamiento de sus datos.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        except OmlParserOpenFileError:
            message = _('<strong>Operación Errónea!</strong> '
                        'El archivo que seleccionó no pudo ser abierto para su procesamiento.')

            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
        else:
            return estructura_archivo

    def valida_datos_desde_lineas(self, lista_rapida):
        """Infiere los metadatos desde las lineas pasadas por parametros.
        """
        lineas_unsafe = self._obtiene_previsualizacion_archivo(lista_rapida)
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

        # Tiene que tener 2 columnas
        if len(primer_linea) != 2:
            logger.debug("Las lineas no poseen 2 "
                         "columnas: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError(_("Las lineas no poseen 2 "
                                                  "columnas")))

    def valida_lista_rapida(self, archivo, nombre_archivo, nombre_lista):
        if self._existe_lista_rapida(nombre_lista):
            raise(OmlError(_("Ya existe una lista de contactos rapida con ese nombre")))
        self.parser = ListaRapidaArchivoCSVParser(nombre_archivo, archivo)

        if not self.parser.es_valida_extension() or not self.parser.es_valido_archivo():
            file_invalid_msg = _("El archivo especificado para realizar la importación de "
                                 "contactos no es válido.")
            raise(OmlArchivoImportacionInvalidoError(file_invalid_msg))

        if not self.parser.headers_no_repetidos():
            raise OmlParserRepeatedColumnsError(_("El archivo a procesar tiene nombres de columnas "
                                                  "repetidos."))

    def _existe_lista_rapida(self, nombre) -> bool:
        return ListasRapidas.objects.filter(nombre=nombre).exists()
