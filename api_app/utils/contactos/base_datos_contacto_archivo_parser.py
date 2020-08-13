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
from __future__ import unicode_literals

import codecs
import csv
import os

from abc import ABC, abstractmethod


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
        headers_set = set([x.strip().capitalize() for x in headers])
        self.columnas = headers_set
        return len(headers) == len(headers_set)
