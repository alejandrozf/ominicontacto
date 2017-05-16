# -*- coding: utf-8 -*-

"""
Servicio encargado de validar y crear las listas negras
"""

from __future__ import unicode_literals

from __builtin__ import callable, enumerate
import json
import logging
import pprint
import os
import re
from django.utils.encoding import smart_text

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, \
    OmlError, OmlParserMaxRowError, OmlParserCsvImportacionError
from ominicontacto_app.models import Backlist, ContactoBacklist
from ominicontacto_app.parser import ParserCsv
from ominicontacto_app.asterisk_config import BackListConfigFile


logger = logging.getLogger(__name__)


class CreacionBacklistService(object):

    def genera_back_list(self, back_list):
        """
        Primer paso de la creación de una Backlist.

        Este método se encarga de validar los datos para la creación del
        del objeto y llevar a cabo el guardado del mismo.

        Valida:
            Que el archivo subido para importar la base de datos de contactos
            sea y tenga las características válidas.
            Si el archivo es válido, hace el save del objeto y si no los es
            lanza la excepción correspondiente.
        """

        csv_extensions = ['.csv']

        filename = back_list.nombre_archivo_importacion
        extension = os.path.splitext(filename)[1].lower()
        if extension not in csv_extensions:
            logger.warn("La extensión %s no es CSV. ", extension)
            raise(OmlArchivoImportacionInvalidoError("El archivo especificado "
                  "para realizar la importación de contactos no es válido"))



    def importa_contactos(self, backlist):
        """
        Tercer paso de la creación de una BaseDatosContacto.
        Este método se encarga de generar los objectos Contacto por cada linea
        del archivo de importación especificado para la base de datos de
        contactos.
        """


        parser = ParserCsv()

        try:
            estructura_archivo = parser.get_estructura_archivo(backlist)
            cantidad_contactos = 0
            if backlist.cantidad_contactos:
                cantidad_contactos = backlist.cantidad_contactos
            for lista_dato in estructura_archivo[1:]:
                cantidad_contactos += 1
                ContactoBacklist.objects.create(
                    telefono=lista_dato[0],
                    back_list=backlist,
                )
        except OmlParserMaxRowError:
            base_datos_contacto.elimina_contactos()
            raise

        except OmlParserCsvImportacionError:
            backlist.elimina_contactos()
            raise

        backlist.cantidad_contactos = cantidad_contactos
        backlist.save()

    def crear_archivo_backlist(self, back_list):
        contactos = ContactoBacklist.objects.filter(back_list=back_list)
        lista_contacto = []
        for contacto in contactos:
            telefono = contacto.telefono + "\n"
            lista_contacto.append(telefono)
        backlist_config_file = BackListConfigFile()
        backlist_config_file.write(lista_contacto)
        backlist_config_file.copy_asterisk()


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
        assert isinstance(lineas_unsafe, (list, tuple))

        lineas = []
        for linea in lineas_unsafe:
            lineas.append(
                [smart_text(col) for col in linea]
            )
        del lineas_unsafe

        logger.debug("inferir_metadata_desde_lineas(): %s", lineas)

        if len(lineas) < 2:
            logger.debug("Se deben proveer al menos 2 lineas: %s", lineas)
            raise(NoSePuedeInferirMetadataError("Se deben proveer al menos 2 "
                                                "lineas para poder inferir "
                                                "los metadatos"))

        # Primero chequeamos q' haya igual cant. de columnas
        set_cant_columnas = set([len(linea) for linea in lineas])
        if len(set_cant_columnas) != 1:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise(NoSePuedeInferirMetadataError("Las lineas recibidas "
                                                "poseen distintas cantidades "
                                                "de columnas"))

        primer_linea = lineas[0]

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError("Las lineas no poseen ninguna "
                                                "columna"))

        if primer_linea[0] != 'telefono':
            raise (NoSePuedeInferirMetadataErrorEncabezado("El nombre de la primera "
                                                 "columna debe ser telefono"))