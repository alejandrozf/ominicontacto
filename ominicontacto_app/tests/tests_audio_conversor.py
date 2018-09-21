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

"""Tests del service audio_conversor"""

from __future__ import unicode_literals

import tempfile

from django.test.utils import override_settings
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService
from ominicontacto_app.models import ArchivoDeAudio
from ominicontacto_app.tests.utiles import OMLBaseTest
import logging as _logging
from mock import Mock


logger = _logging.getLogger(__name__)


def _tmpdir():
    """Crea directorio temporal"""
    return tempfile.mkdtemp(prefix=".oml-tests-", dir="/dev/shm")


class ConvertirAudioDeArchivoDeAudioGlobalesTests(OMLBaseTest):
    """Testea metodo convertir_audio_de_archivo_de_audio_globales() de
    ConversorDeAudioService
    """

    @override_settings(MEDIA_ROOT=_tmpdir())
    def test_convierte_audio_primera_vez_funciona(self):
        servicio = ConversorDeAudioService()
        servicio._convertir_audio = Mock()

        original = self.copy_test_resource_to_mediaroot("wavs/8k16bitpcm.wav")

        archivo_de_audio = ArchivoDeAudio(id=1,
                                          descripcion="Audio",
                                          audio_original=original)
        archivo_de_audio.save = Mock()

        # -----

        self.assertFalse(archivo_de_audio.audio_asterisk)
        servicio.convertir_audio_de_archivo_de_audio_globales(
            archivo_de_audio)

        self.assertTrue(archivo_de_audio.audio_asterisk)
        self.assertEqual(servicio._convertir_audio.call_count, 1)
        self.assertEqual(archivo_de_audio.save.call_count, 1)

    @override_settings(MEDIA_ROOT=_tmpdir())
    def test_convierte_audio_dos_veces_funciona(self):
        servicio = ConversorDeAudioService()
        servicio._convertir_audio = Mock()

        original1 = self.copy_test_resource_to_mediaroot("wavs/8k16bitpcm.wav")
        original2 = self.copy_test_resource_to_mediaroot("wavs/empty.wav")

        archivo_de_audio = ArchivoDeAudio(id=1,
                                          descripcion="Audio",
                                          audio_original=original1)
        archivo_de_audio.save = Mock()

        self.assertFalse(archivo_de_audio.audio_asterisk)
        servicio.convertir_audio_de_archivo_de_audio_globales(
            archivo_de_audio)

        self.assertTrue(archivo_de_audio.audio_asterisk)
        self.assertEqual(servicio._convertir_audio.call_count, 1)
        self.assertEqual(archivo_de_audio.save.call_count, 1)

        audio_asterisk_frist_call = archivo_de_audio.audio_asterisk

        # -----

        # Convertimos por 2da vez
        archivo_de_audio.audio_original = original2

        servicio.convertir_audio_de_archivo_de_audio_globales(
            archivo_de_audio)

        self.assertTrue(archivo_de_audio.audio_asterisk)
        self.assertEqual(servicio._convertir_audio.call_count, 2)
        self.assertEqual(archivo_de_audio.save.call_count, 2)

        audio_asterisk_second_call = archivo_de_audio.audio_asterisk

        self.assertEqual(audio_asterisk_frist_call,
                         audio_asterisk_second_call,
                         "La 2da ejecucion sobre la misma instancia de "
                         "ArchivoDeAudio ha generado un nombre distinto")

        # Chequeamos que las 2 veces que se convirtio hayan tenido
        # distinto archivo de entreda, pero mismo archivo de salida

        first_call = servicio._convertir_audio.call_args_list[0]
        second_call = servicio._convertir_audio.call_args_list[1]

        fc_p1 = first_call[0][0]
        fc_p2 = first_call[0][1]
        sc_p1 = second_call[0][0]
        sc_p2 = second_call[0][1]

        self.assertNotEqual(fc_p1, sc_p1, "Las 2 veces que se llamo "
                            "convertir_audio_de_archivo_de_audio_globales() "
                            "se ha utilizado el mismo archivo origen, cuando "
                            "debieron ser 2 archivos distintos")
        self.assertEqual(fc_p2, sc_p2, "En diversas llamadas se generaron "
                         "nombres de archivos destinos (convertidos) "
                         "distintos!")
