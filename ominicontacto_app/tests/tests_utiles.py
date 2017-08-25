# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.utiles'
"""

from __future__ import unicode_literals

import uuid
import logging as _logging

from django.conf import settings

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.utiles import upload_to
from ominicontacto_app.errors import OmlError
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
