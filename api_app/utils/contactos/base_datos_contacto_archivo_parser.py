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

import codecs
import csv
import os

from abc import ABC, abstractmethod
from django.utils.encoding import smart_text
import re
from ominicontacto_app.utiles import elimina_tildes


class BaseDatosContactoArchivoCampo(object):

    def __init__(self, nombre, valor, tipo="texto") -> None:
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor


class BaseDatosContactoArchivoParser(ABC):

    def __init__(self, nombre_archivo) -> None:
        self.nombre_archivo = nombre_archivo
        self.extension_archivo = os.path.splitext(nombre_archivo)[1].lower()
        self.columnas = {}

    def agrega_columna(self, columna) -> None:
        self.columnas.update(columna)

    @abstractmethod
    def es_valida_extension(self) -> bool:
        pass


class BaseDatosContactoArchivoCSVParser(BaseDatosContactoArchivoParser):

    def __init__(self, nombre_archivo, archivo) -> None:
        BaseDatosContactoArchivoParser.__init__(self, nombre_archivo)
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
