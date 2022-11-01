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
Tests del metodo 'ominicontacto_app.utiles'
"""

from __future__ import unicode_literals

import uuid
import logging as _logging

from django.conf import settings
from django.utils import timezone
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.utiles import (
    upload_to, crear_archivo_en_media_root, elimina_espacios_parentesis_guiones,
    remplace_espacio_por_guion, elimina_coma, elimina_comillas,
    convert_string_in_boolean, convert_fecha_datetime, convertir_ascii_string,
    dividir_lista
)
import os

logger = _logging.getLogger(__name__)


class UtilesTest(OMLBaseTest):

    def assertAndSplit(self, text, prefix):
        tokens = text.split("/")
        self.assertEqual(tokens[0], prefix)
        self.assertEqual(tokens[1], "%Y")
        self.assertEqual(tokens[2], "%m")
        uuid.UUID(tokens[3][0:36])
        self.assertEqual(tokens[3][36], '-')
        return tokens[3][37:]

    def test_upload_to_archivo_importacion(self):
        upload_to_archivo_importacion = upload_to("archivo_importacion", 200)

        # ~~~~~ cliente.txt
        output = upload_to_archivo_importacion(None, "cliente.txt")
        self.assertEqual(self.assertAndSplit(output, "archivo_importacion"),
                         'cliente.txt')

        # ~~~~~ ''
        output = upload_to_archivo_importacion(None, "")
        self.assertEqual(self.assertAndSplit(output, "archivo_importacion"), '')

        # ~~~~~ 'archivo con espacios#ext'
        output = upload_to_archivo_importacion(None, "archivo con espacios#ext")
        self.assertEqual(self.assertAndSplit(output, "archivo_importacion"),
                         'archivoconespaciosext')

        # ~~~~~ file.extensionmuylarga
        len_sin_filename = len(upload_to_archivo_importacion(None, ""))
        largo_filename_max = 200 - len_sin_filename

        output = upload_to_archivo_importacion(None, "x" * 300)
        self.assertEqual(len(output), 200)
        rest_of_filename = self.assertAndSplit(output, "archivo_importacion")

        self.assertEqual(len(rest_of_filename), largo_filename_max)
        self.assertEqual(rest_of_filename, "x" * largo_filename_max)

    def test_crear_archivo_en_media_root(self):
        t_dirname = 'output-dir-name'
        t_filename_prefix = 'reporte-agente-'

        dirname, filename = crear_archivo_en_media_root(
            t_dirname + '/algo', t_filename_prefix)
        logger.debug("crear_archivo_en_media_root():")
        logger.debug(" - %s", dirname)
        logger.debug(" - %s", filename)

        self.assertEqual(dirname, t_dirname + "/algo")
        self.assertTrue(filename.find(t_filename_prefix) >= 0)

        # ~~~ casi lo mismo, pero con 'suffix'
        dirname, filename = crear_archivo_en_media_root(
            t_dirname + '/algo', t_filename_prefix, suffix=".csv")

        logger.debug("crear_archivo_en_media_root():")
        logger.debug(" - %s", dirname)
        logger.debug(" - %s", filename)

        self.assertEqual(dirname, t_dirname + "/algo")
        self.assertTrue(filename.find(t_filename_prefix) >= 0)
        self.assertTrue(filename.endswith(".csv"))

    def test_crear_archivo_en_media_root_falla(self):
        dirname, filename = crear_archivo_en_media_root('algo', 'prefix')
        self.assertTrue(os.path.exists(settings.MEDIA_ROOT + "/" +
                        dirname + "/" + filename))
        self.assertTrue(os.path.isfile(settings.MEDIA_ROOT + "/" +
                        dirname + "/" + filename))
        self.assertTrue(os.path.isdir(settings.MEDIA_ROOT + "/" + dirname))

        with self.assertRaises(AssertionError):
            crear_archivo_en_media_root('/algo', 'prefix')

        with self.assertRaises(AssertionError):
            crear_archivo_en_media_root('algo/', 'prefix')

        with self.assertRaises(AssertionError):
            crear_archivo_en_media_root('algo', 'prefix/algomas')

    def test_elimina_espacios_parentesis_guiones(self):
        cadena = elimina_espacios_parentesis_guiones(" asdfg32432 ñ(899) -781")
        self.assertEqual(cadena, "asdfg32432ñ899781")

    def test_remplace_espacios_por_guien(self):
        cadena = remplace_espacio_por_guion(" asdfg32432 ñ(899)  781")
        self.assertEqual(cadena, "_asdfg32432_ñ(899)_781")

    def test_elimina_coma(self):
        cadena = elimina_coma(" asdf,g32432 ñ(899) ,781")
        self.assertEqual(cadena, " asdfg32432 ñ(899) 781")

    def test_elimina_comillas(self):
        cadena = elimina_comillas(' asdfg"32432 ñ(899) "781"')
        self.assertEqual(cadena, " asdfg32432 ñ(899) 781")

    def test_convertir_string_false_in_boolean(self):
        cadena = convert_string_in_boolean("false")
        self.assertEqual(cadena, False)

    def test_convertir_string_true_in_boolean(self):
        cadena = convert_string_in_boolean("true")
        self.assertEqual(cadena, True)

    def test_convertir_string_default_in_boolean(self):
        cadena = convert_string_in_boolean("fsdsf")
        self.assertEqual(cadena, False)

    def test_convertir_fecha_datetime(self):
        fecha = convert_fecha_datetime("25/08/2017")
        fecha_datetime = timezone.datetime(2017, 8, 25, tzinfo=timezone.get_current_timezone())
        self.assertEqual(fecha, fecha_datetime)

    def test_convertir_fecha_datetime_falla(self):
        with self.assertRaisesMessage(
                ValueError, "day is out of range for month"):
            convert_fecha_datetime("2017/08/25")

    def test_convertir_ascii_string(self):
        cadena = convertir_ascii_string("asdfg32432\xf1 (899)-781")
        self.assertEqual(cadena, "asdfg32432 (899)-781")

    def test_dividir_lista(self):
        self.assertEqual(list(dividir_lista(range(13), 2)), [range(0, 6), range(6, 13)])
        self.assertEqual(
            list(dividir_lista(range(13), 3)), [range(0, 4), range(4, 8), range(8, 13)])
        self.assertEqual(list(dividir_lista(range(4), 2)), [range(0, 2), range(2, 4)])
        self.assertEqual(list(dividir_lista(range(11), 1)), [range(0, 11)])
        self.assertEqual(list(dividir_lista(range(5), 6)), [[0], [1], [2], [3], [4]])
