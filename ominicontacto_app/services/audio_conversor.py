# -*- coding: utf-8 -*-

"""
Conversión de archivos de audio para Asterisk.
"""

from __future__ import unicode_literals

import os
import subprocess
import tempfile

from django.conf import settings
from django.core.files.storage import default_storage
from ominicontacto_app.errors import OmlAudioConversionError
from ominicontacto_app.utiles import crear_archivo_en_media_root
from ominicontacto_app.models import ArchivoDeAudio
import logging as _logging
import uuid
import re


logger = _logging.getLogger(__name__)


class ConversorDeAudioService(object):
    """Servicio que realiza la conversion de archivos de audio
    para poder ser usados por Asterisk
    """

    DIR_AUDIO_PREDEFINIDO = "audio_asterisk_predefinido"
    """Directorio relativo a MEDIA_ROOT donde se guardan los archivos
    convertidos para audios globales / predefinidos
    """

    TEMPLATE_NOMBRE_AUDIO_ASTERISK_PREDEFINIDO = "audio-predefinido-{0}{1}"
    """Nombre de archivo para audios ya convertidos, de archivos
    de audios globales / predefinidos.

    Debe poseer 2 placeholders:
    1. {0} para el ID de ArchivoDeAudio
    2. {1} para el sufijo del nombre del archivo (ej: '.wav')
    """

    REGEX_NOMBRE_AUDIO_ASTERISK_PREDEFINIDO = re.compile("^" +
        DIR_AUDIO_PREDEFINIDO + os.path.sep +
        TEMPLATE_NOMBRE_AUDIO_ASTERISK_PREDEFINIDO.format(
            "(\\d+)", settings.TMPL_OML_AUDIO_CONVERSOR_EXTENSION) +
        "$")

    def _crear_directorios(self, directorio, mode=0755):
        """Crea directorio (recursivamente) si no existen. Es el equivalente
        de `mkdir -p`.

        :param directorio: path absoluto al directorio
        :param mode: modo del archivo (OCTAL)
        :returns: True si fue creado, False si no fue creado (ya
                  existia). Puede devolver FALSOS POSITIVOS (o sea,
                  devuelve True pero en realidad otro proceso lo ha
                  creado).
        """
        assert os.path.isabs(directorio), \
            "El directorio especificado no es un path absoluto: {0}".format(
                directorio)
        if not os.path.exists(directorio):
            logger.info("Se crearan directorios: %s", directorio)
            os.makedirs(directorio, mode)
            return True

        return False

    def _crear_archivo(self, archivo, mode=0644):
        """Crea archivo vacio si no existe.

        :param archivo: path absoluto al archivo
        :param mode: modo del archivo (OCTAL)
        :returns: True si fue creado, False si no fue creado (ya
                  existia). Puede devolver FALSOS POSITIVOS (o sea,
                  devuelve True pero en realidad otro proceso lo ha
                  creado).
        """
        assert os.path.isabs(archivo), \
            "El archivo especificado no es un path absoluto: {0}".format(
                archivo)
        if not os.path.exists(archivo):
            with open(archivo, "a") as _:
                pass
            os.chmod(archivo, mode)
            return True

        return False

    def _convertir_audio(self, input_file_abs, output_filename_abs):
        """Convierte archivo de audio.

        :param input_file_abs: path absoluto a archivo de entrada (.wav)
        :type input_file_abs: str
        :param output_filename_abs: path absoluto a archivo de salida
        :type output_filename_abs: str

        :raises: OmlAudioConversionError: si se produjo algun tipo de error
        """

        # chequeos...
        if not os.path.exists(input_file_abs):
            logger.error("El archivo de entrada no existe: %s", input_file_abs)
            raise OmlAudioConversionError("El archivo de entrada no existe")

        if not os.path.abspath(input_file_abs):
            logger.error("El archivo de entrada no es un path absoluto: %s",
                input_file_abs)
            raise OmlAudioConversionError("El archivo de entrada no es "
                "un path absoluto")

        if not os.path.abspath(output_filename_abs):
            logger.error("El archivo de salida no es un path absoluto: %s",
                output_filename_abs)
            raise OmlAudioConversionError("El archivo de salida no es "
                "un path absoluto")

        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()

        FTS_AUDIO_CONVERSOR = []
        for item in settings.TMPL_OML_AUDIO_CONVERSOR:
            if item == "<INPUT_FILE>":
                FTS_AUDIO_CONVERSOR.append(input_file_abs)
            elif item == "<OUTPUT_FILE>":
                FTS_AUDIO_CONVERSOR.append(output_filename_abs)
            else:
                FTS_AUDIO_CONVERSOR.append(item)

        assert input_file_abs in FTS_AUDIO_CONVERSOR
        assert output_filename_abs in FTS_AUDIO_CONVERSOR

        # ejecutamos comando...
        try:
            logger.info("Iniciando conversion de audio de %s -> %s",
                input_file_abs, output_filename_abs)
            subprocess.check_call(FTS_AUDIO_CONVERSOR,
                stdout=stdout_file, stderr=stderr_file)
            logger.info("Conversion de audio finalizada exitosamente")

        except subprocess.CalledProcessError as e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            try:
                stdout_file.seek(0)
                stderr_file.seek(0)
                stdout = stdout_file.read().splitlines()
                for line in stdout:
                    if line:
                        logger.warn(" STDOUT> %s", line)
                stderr = stderr_file.read().splitlines()
                for line in stderr:
                    if line:
                        logger.warn(" STDERR> %s", line)
            except:
                logger.exception("Error al intentar reporter STDERR y STDOUT "
                    "(lo ignoramos)")

            raise OmlAudioConversionError("Error detectado al ejecutar "
                                          "conversor", cause=e)

        finally:
            stdout_file.close()
            stderr_file.close()

    def convertir_audio_de_archivo_de_audio_globales(self, archivo_de_audio):
        """Realiza la conversión y actualiza la instancia de ArchivoDeAudio.

        Esta funcion debe usarse en el Alta y Modificacioin de ArchivoDeAudio.

        :param archivo_de_audio: ArchivoDeAudio para la cual hay que convertir
                                 el audio
        :type archivo_de_audio: ominicontacto_app.models.ArchivoDeAudio
        :raises: OmlAudioConversionError
        """

        assert isinstance(archivo_de_audio, ArchivoDeAudio)

        # chequea archivo original (a convertir)
        wav_full_path = default_storage.path(
            archivo_de_audio.audio_original.name)
        assert os.path.exists(wav_full_path)

        # genera nombre del archivo de salida
        _template = ConversorDeAudioService.\
            TEMPLATE_NOMBRE_AUDIO_ASTERISK_PREDEFINIDO
        filename = _template.format(archivo_de_audio.id,
            settings.TMPL_OML_AUDIO_CONVERSOR_EXTENSION)

        # Creamos directorios si no existen
        abs_output_dir = os.path.join(settings.MEDIA_ROOT,
            ConversorDeAudioService.DIR_AUDIO_PREDEFINIDO)

        self._crear_directorios(abs_output_dir)

        # Creamos archivo si no existe
        abs_output_filename = os.path.join(abs_output_dir, filename)
        self._crear_archivo(abs_output_filename)

        assert os.path.exists(abs_output_filename)

        # convierte archivo
        self._convertir_audio(wav_full_path, abs_output_filename)

        # guarda ref. a archivo convertido
        archivo_de_audio.audio_asterisk = os.path.join(
            ConversorDeAudioService.DIR_AUDIO_PREDEFINIDO, filename)
        archivo_de_audio.save()

    def obtener_id_archivo_de_audio_desde_path(self, file_path):
        """Parsea el path del archivo de audio ya convertido, y
        devuelve el ID del ArchivoDeAudio al que está asociado,
        o devuelve None si el path NO correspode a una instancia
        de ArchivoDeAudio.

        Esta funcion es necesaria para saber si el archivo de
        audio de una campaña correspodne a un ArchivoDeAudio o
        fue un audio subido específicamente para la campaña.
        """

        regex = ConversorDeAudioService.REGEX_NOMBRE_AUDIO_ASTERISK_PREDEFINIDO
        match_obj = regex.search(file_path)
        if match_obj is None:
            return None
        archivo_id = match_obj.group(1)
        return int(archivo_id)






