# -*- coding: utf-8 -*-

"""
Parser de archivos CSV.
"""

from __future__ import unicode_literals

import csv
import logging
import re

from django.conf import settings
from django.utils.encoding import smart_text
from ominicontacto_app.errors import\
    (OmlParserCsvDelimiterError, OmlParserMinRowError, OmlParserMaxRowError,
     OmlParserCsvImportacionError, OmlParserCsvEncodingError)
from ominicontacto_app.models import MetadataBaseDatosContactoDTO


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
            return [unicode(column, 'utf-8') for column in row]
        except UnicodeDecodeError:
            # Aja! Una columna no es utf-8 valido!
            celda_problematica = None
            try:
                for column in row:
                    celda_problematica = column
                    unicode(column, 'utf-8')
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

        workbook = csv.reader(file_obj, self._get_dialect(file_obj))

        cantidad_importados = 0
        for i, curr_row in enumerate(workbook):
            if len(curr_row) == 0:
                logger.info("Ignorando fila vacia %s", i)
                self.vacias += 1
                continue

            if i >= settings.OL_MAX_CANTIDAD_CONTACTOS:
                raise OmlParserMaxRowError("El archivo CSV "
                                           "posee mas registros de los "
                                           "permitidos.")

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
                    logger.warn("Error en la imporación de contactos: No "
                                "valida el formato fecha en la linea %s",
                                curr_row)
                    raise OmlParserCsvImportacionError(
                        numero_fila=i,
                        numero_columna=metadata.columnas_con_fecha,
                        fila=curr_row,
                        valor_celda=fechas)

            if metadata.columnas_con_hora:
                horas = [curr_row[columna]
                         for columna in metadata.columnas_con_hora]
                if not validate_horas(horas):
                    logger.warn("Error en la imporación de contactos: No "
                                "valida el formato hora en la linea %s",
                                curr_row)
                    raise OmlParserCsvImportacionError(
                        numero_fila=i,
                        numero_columna=metadata.columnas_con_hora,
                        fila=curr_row,
                        valor_celda=horas)

            if len(curr_row) != metadata.cantidad_de_columnas:
                mensaje = ("N/A - la BD esta definida con {0} columnas, "
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

        logger.info("%s contactos importados - %s valores ignoradas.",
                    cantidad_importados, self.vacias)

    def previsualiza_archivo(self, base_datos_contactos):
        """
        Lee un archivo CSV y devuelve contenidos de
        las primeras tres filas.
        """

        file_obj = base_datos_contactos.archivo_importacion.file
        workbook = csv.reader(file_obj, self._get_dialect(file_obj))

        structure_dic = []
        for i, row in enumerate(workbook):
            if row:
                structure_dic.append(row)

            if i == 3:
                break

        if i < 3:
            logger.warn("El archivo CSV seleccionado posee menos de 3 "
                        "filas.")
            raise OmlParserMinRowError("El archivo CSV posee menos de "
                                       "3 filas")
        return structure_dic

    def _get_dialect(self, file_obj):
        try:
            file_obj.seek(0, 0)
            dialect = csv.Sniffer().sniff(file_obj.read(1024),
                                          [',', ';', '\t'])
            file_obj.seek(0, 0)

            return dialect
        except csv.Error:
            file_obj.seek(0, 0)

            workbook = csv.reader(file_obj)
            single_column = []

            i = 0
            for i, row in enumerate(workbook):
                value = row[0].strip()
                try:
                    int(value)
                    value_valid = True
                except ValueError:
                    value_valid = False

                if i == 0 and not value_valid:
                    continue

                single_column.append(value_valid)

                if i == 3:
                    break

            if i < 3:
                logger.warn("El archivo CSV seleccionado posee menos de 3 "
                            "filas.")
                raise OmlParserMinRowError("El archivo CSV posee menos de "
                                           "3 filas")

            if single_column and all(single_column):
                file_obj.seek(0, 0)
                return None

            logger.warn("No se pudo determinar el delimitador del archivo"
                        " CSV")
            raise OmlParserCsvDelimiterError("No se pudo determinar el "
                                             "delimitador del archivo CSV")
        finally:
            file_obj.seek(0, 0)

    def get_estructura_archivo(self, base_datos_contactos):
        """
        Lee un archivo CSV y devuelve contenidos.
        """

        file_obj = base_datos_contactos.archivo_importacion.file
        workbook = csv.reader(file_obj, self._get_dialect(file_obj))

        structure_dic = []
        for i, row in enumerate(workbook):
            if row:
                structure_dic.append(row)

        if i < 3:
            logger.warn("El archivo CSV seleccionado posee menos de 3 "
                        "filas.")
            raise OmlParserMinRowError("El archivo CSV posee menos de "
                                           "3 filas")
        return structure_dic

    def detectar_encoding_csv(self, estructura_archivo):
        """
        Detecta el encoding la estructura pasada por parametro
        :param estructura_archivo: estructura del archiva
        :return: retorna el enconding del archivo
        """

        error_utf_8 = False
        error_iso = False
        for item in estructura_archivo:
            for value in item:
                try:
                    value.decode('utf-8')
                except UnicodeDecodeError:
                    error_utf_8 = True
                    break

        if not error_utf_8:
            return "utf-8"
        else:
            for item in estructura_archivo:
                for value in item:
                    try:
                        value.decode('iso-8859-1')
                    except UnicodeDecodeError:
                        error_iso = True
                    break

        if error_iso:
            logger.warn("No se pudo detectar el encoding del archivo csv")
            raise OmlParserCsvEncodingError("No se pudo detectar el encoding"
                                            " del archivo csv")
        else:
            return "iso-8859-1"

    def visualizar_estructura_template(self, estructura_archivo, encoding):

        transformado = []
        for fila in estructura_archivo:
            item = [value.decode(encoding) for value in fila]
            transformado.append(item)
        return transformado

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
            "^(0[1-9]|[12][0-9]|3[01])[/](0[1-9]|1[012])[/](19|20)?\d\d$",
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


PATTERN_SANITIZE_NUMBER = re.compile("[^0-9]")


def sanitize_number(number):
    number = unicode(number)
    return PATTERN_SANITIZE_NUMBER.sub("", number)
