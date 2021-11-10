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
Parser de archivos CSV.
"""

from __future__ import unicode_literals

import codecs
import csv
import logging
import re

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text
from ominicontacto_app.errors import\
    (OmlParserMinRowError, OmlParserMaxRowError,
     OmlParserCsvImportacionError, OmlParserRepeatedColumnsError)
from ominicontacto_app.models import MetadataBaseDatosContactoDTO
from ominicontacto_app.utiles import elimina_tildes


logger = logging.getLogger('ParserCsv')


# =============================================================================
# Parser CSV
# =============================================================================

class ParserCsv(object):
    """
    Clase utilitaria para obtener datos de archivo CSV.
    """

    def __init__(self):
        # No es thread-safe!
        self.vacias = 0

    def read_file(self, base_datos_contactos):
        """Lee un archivo CSV y devuelve contenidos de las columnas."""

        # Reseteamos estadisticas
        self.vacias = 0

        # base_datos_contactos.archivo_importacion.open()
        # file_obj = base_datos_contactos.archivo_importacion.file
        # try:
        #     return self._read_file(file_obj,
        #                            self._get_dialect(file_obj),
        #                            base_datos_contactos.get_metadata()
        #                            )
        # finally:
        #     base_datos_contactos.archivo_importacion.close()

        # with open(base_datos_contactos.archivo_importacion.path, 'rb')
        #     as file_obj:
        #     return self._read_file(file_obj,
        #                            self._get_dialect(file_obj),
        #                            base_datos_contactos.get_metadata()
        #                            )

        file_obj = base_datos_contactos.archivo_importacion.file
        return self._read_file(file_obj, base_datos_contactos.get_metadata())

    def _transformar_en_unicode(self, row, numero_fila):
        """Recibe lista con datos de una linea del CSV, y transforma
        los elementos de la lista en unicodes.

        :returns: lista con datos del CSV, como unicodes
        :raises: FtsParserCsvImportacionError
        """
        try:
            return [str(column, 'utf-8') for column in row]
        except UnicodeDecodeError:
            # Aja! Una columna no es utf-8 valido!
            celda_problematica = None
            try:
                for column in row:
                    celda_problematica = column
                    str(column, 'utf-8')
                # Alguna columna deberia fallar, pero por las dudas limpiamos
                # 'celda_problematica' si el 'for' termina de procesar todas
                # las columnas. Esto NO DEBERIA SUCEDER!
                celda_problematica = None
            except UnicodeDecodeError:
                pass

            # Lanza excepcion, pasa por parametro la fila problemática
            # OJO! La fila será pasada así como fue leida por Python del CSV,
            #  y por lo tanto serán strigs/bytes, NO unicodes.
            raise OmlParserCsvImportacionError(
                numero_fila=numero_fila,
                numero_columna='',
                fila=row,
                valor_celda=celda_problematica or '?')

    def _read_file(self, file_obj, metadata):

        assert isinstance(metadata, MetadataBaseDatosContactoDTO)

        file_obj_str = codecs.iterdecode(file_obj, 'utf-8', errors='ignore')
        workbook = csv.reader(file_obj_str, skipinitialspace=True)

        cantidad_importados = 0
        for i, curr_row in enumerate(workbook):
            if len(curr_row) == 0:
                logger.info(_("Ignorando fila vacia {0}".format(i)))
                self.vacias += 1
                continue

            if i >= settings.OL_MAX_CANTIDAD_CONTACTOS:
                raise OmlParserMaxRowError(_("El archivo CSV "
                                             "posee mas registros de los "
                                             "permitidos."))

            # La libreria CSV de Python 2 devuelve strings (o sea, bytes)
            # ignorando completamente el tipo de codificacion.
            # Por eso, antes de procesar la línea, la convertimos
            # en unicode
            curr_row = self._transformar_en_unicode(curr_row, i)

            # telefono = sanitize_number(
            #     curr_row[metadata.columna_con_telefono].strip())
            #
            # if not validate_telefono(telefono):
            #     if i == 0 and metadata.primer_fila_es_encabezado:
            #         continue
            #     logger.warn("Error en la imporación de contactos: No "
            #                 "valida el teléfono en la linea %s",
            #                 curr_row)
            #     raise OmlParserCsvImportacionError(
            #         numero_fila=i,
            #         numero_columna=metadata.columna_con_telefono,
            #         fila=curr_row,
            #         valor_celda=telefono)

            if metadata.columnas_con_fecha:
                fechas = [curr_row[columna]
                          for columna in metadata.columnas_con_fecha]
                if not validate_fechas(fechas):
                    logger.warn(_("Error en la importacion de contactos: No "
                                  "valida el formato fecha en la linea {0}".format(curr_row)))
                    raise OmlParserCsvImportacionError(
                        numero_fila=i,
                        numero_columna=metadata.columnas_con_fecha,
                        fila=curr_row,
                        valor_celda=fechas)

            if metadata.columnas_con_hora:
                horas = [curr_row[columna]
                         for columna in metadata.columnas_con_hora]
                if not validate_horas(horas):
                    logger.warn(_("Error en la importacion de contactos: No "
                                  "valida el formato hora en la linea {0}".format(curr_row)))
                    raise OmlParserCsvImportacionError(
                        numero_fila=i,
                        numero_columna=metadata.columnas_con_hora,
                        fila=curr_row,
                        valor_celda=horas)

            if len(curr_row) != metadata.cantidad_de_columnas:
                mensaje = _("N/A - la BD esta definida con {0} columnas, "
                            "pero el archivo posee esta fila con {1} columnas"
                            "".format(metadata.cantidad_de_columnas,
                                      len(curr_row)))
                raise OmlParserCsvImportacionError(
                    numero_fila=i,
                    numero_columna=0,
                    fila=curr_row,
                    valor_celda=mensaje)

            cantidad_importados += 1
            yield curr_row

        logger.info(_("{0} contactos importados - {1} valores ignorados.".format(
            cantidad_importados, self.vacias)))

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
        nombre = nombre.strip()  # .upper()
        nombre = DOUBLE_SPACES.sub("_", nombre)
        nombre = elimina_tildes(nombre)
        return nombre

    def _sanear_nombres_de_columnas(self, nombres):
        nombres_saneados = [self._sanear_nombre_de_columna(nombre) for nombre in nombres]
        # Validar que no se repiten las columnas
        if not len(nombres) == len(set([x for x in nombres_saneados])):
            raise OmlParserRepeatedColumnsError(_("El archivo a procesar tiene nombres de columnas "
                                                  "repetidos."))
        return nombres_saneados

    def previsualiza_archivo(self, base_datos_contactos):
        """
        Lee un archivo CSV y devuelve contenidos de
        las primeras tres filas.
        """

        return self._get_contenido_de_archivo(base_datos_contactos, True)

    def get_estructura_archivo(self, base_datos_contactos):
        """
        Lee un archivo CSV y devuelve contenidos.
        """
        return self._get_contenido_de_archivo(base_datos_contactos)

    def _get_contenido_de_archivo(self, base_datos_contactos, previsualizacion=False):
        """
        Lee un archivo CSV y devuelve contenidos de
        las primeras tres filas.
        """

        file_obj = base_datos_contactos.archivo_importacion.file
        file_obj_str = codecs.iterdecode(file_obj, 'utf-8', errors='ignore')
        workbook = csv.reader(file_obj_str, skipinitialspace=True)

        structure_dic = []
        for i, row in enumerate(workbook):
            if row:
                structure_dic.append(row)

            if previsualizacion and i == 2:
                break

        if i < 2:
            logger.warn(_("El archivo CSV seleccionado posee menos de 2 "
                          "filas."))
            raise OmlParserMinRowError(_("El archivo CSV posee menos de "
                                         "2 filas"))
        structure_dic[0] = self._sanear_nombres_de_columnas(structure_dic[0])

        return structure_dic

# =============================================================================
# Funciones utilitarias
# =============================================================================


def validate_fechas(fechas):
    """
    Esta función en principio, valida el formato de las fechas.
    Si todas validan devuelve True, sino False.
    """
    if not fechas:
        return False

    validate = []
    for fecha in fechas:
        if re.match(
            r"^(0[1-9]|[12][0-9]|3[01])[/](0[1-9]|1[012])[/](19|20)?\d\d$",
                fecha):
            validate.append(True)
        else:
            validate.append(False)
    return all(validate)


def validate_horas(horas):
    """
    Esta función en principio, valida el formato de las horas.
    Si todas validan devuelve True, sino False.
    """
    if not horas:
        return False

    validate = []
    for hora in horas:

        if re.match(
            "^(([0-1][0-9])|([2][0-3])):([0-5]?[0-9])(:([0-5]?[0-9]))?$",
                hora):
            validate.append(True)
        else:
            validate.append(False)
    return all(validate)


REGEX_NON_DIGITS = re.compile(r'[^0-9]')


def validate_telefono(number):
    """
    Esta función valida el numero telefónico tenga  entre 10 y 13 dígitos.
    """
    number = REGEX_NON_DIGITS.sub("", smart_text(number))
    if settings.OL_NRO_TELEFONO_LARGO_MIN <= len(number) <= \
            settings.OL_NRO_TELEFONO_LARGO_MAX:
        return True

    return False


def validate_telefono_or_ext(number):
    """
    Esta función valida el numero telefónico tenga  entre 3 y 13 dígitos.
    """
    number = REGEX_NON_DIGITS.sub("", smart_text(number))
    if settings.OL_NRO_EXT_BPX_LARGO_MIN <= len(number) <= \
            settings.OL_NRO_TELEFONO_LARGO_MAX:
        return True


PATTERN_SANITIZE_NUMBER = re.compile("[^0-9]")


def sanitize_number(number):
    number = str(number)
    return PATTERN_SANITIZE_NUMBER.sub("", number)


DOUBLE_SPACES = re.compile(r' +')
