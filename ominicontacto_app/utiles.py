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

"""Funciones de utilidad en el sistema"""

from __future__ import unicode_literals

from contextlib import contextmanager
import csv
import codecs
import cStringIO
import os
import re
import tempfile
import time
import uuid
import unicodedata
import datetime
from django.utils import timezone

from django.conf import settings
from django.forms import ValidationError

from ominicontacto_app.errors import OmlError
import logging as _logging


logger = _logging.getLogger(__name__)

SUBSITUTE_REGEX = re.compile(r'[^a-z\._-]')


def _upload_to(prefix, max_length, instance, filename):
    filename = SUBSITUTE_REGEX.sub('', filename)
    return "{0}/%Y/%m/{1}-{2}".format(prefix,
                                      str(uuid.uuid4()), filename)[:max_length]


def upload_to(prefix, max_length):
    """Genera (devuelve) una funcion a ser usada en `upload_to` de `FileField`.
    La funcion generada genera un path (relativo) de no mas de `max_length`
    caracteres, y usando el prefijo `prefix`
    """
    def func(instance, filename):
        return _upload_to(prefix, max_length, instance, filename)
    return func


def resolve_strftime(text):
    """Ejecuta strftime() en texto pasado por parametro"""
    return time.strftime(text)  # time.gmtime()


def elimina_tildes(s):
    return ''.join(unicodedata.normalize('NFD', s).encode('ASCII', 'ignore'))


def elimina_espacios_parentesis_guiones(cadena):
    """
    Elimina espacios, parentesis y guiones de la cadena recibida por parametro
    La cadena debe ser una instancia de unicode
    """
    assert isinstance(cadena, unicode), "'cadena' debe ser una instancia de unicode"
    return re.sub("\(?\)?\s?\-?", "", cadena)


def elimina_espacios(cadena):
    """
    Elimina espacios de la cadena recibida por parametro
    La cadena debe ser una instancia de unicode
    """
    assert isinstance(cadena, unicode), "'cadena' debe ser una instancia de unicode"
    return re.sub("\s?", "", cadena)


def remplace_espacio_por_guion(cadena):
    """
    Remplaza espacio por guion en cadaena recibida por parametro
    La cadena debe ser una instancia de unicode
    """
    assert isinstance(cadena, unicode), "'cadena' debe ser una instancia de unicode"
    return re.sub(r"\s+", "_", cadena)


def elimina_coma(cadena):
    """
    Elimina coma
    """
    return re.sub("\,?", "", cadena)


def elimina_comillas(cadena):
    """
    Elimina comillas
    """
    return re.sub('"', "", cadena)


def crear_archivo_en_media_root(dirname_template, prefix, suffix=""):
    """Crea un archivo en el directorio MEDIA_ROOT. Si los directorios
    no existen, los crea tambien.

    Para la creacion del archivo usa `tempfile.mkstemp`

    Parametros:
        - dirname_template (directorio, acepta %Y, %m, etc.)
        - prefix (prefijo para nombre de archivo)
        - suffix (para poder especificar una extension)

    Devuelve: tupla con
        (directorio_relativo_a_MEDIA_ROOT, nombre_de_archivo)

    Ej:
        crear_archivo('data/%Y/%m', 'audio-original'):
            En este caso, se creara (si no existen) los
            directorios `data`, ANIO y MES, y crea un archivo que
            comienza con `audio-original`
    """
    assert dirname_template[-1] != '/'
    assert dirname_template[0] != '/'
    assert prefix.find('/') == -1

    # relative_filename = resolve_strftime(dirname_template)
    # output_directory_rel, tempfile_prefix = os.path.split(relative_filename)
    # output_directory_abs = os.path.join(
    #    settings.MEDIA_ROOT, output_directory_rel)

    relative_dirname = resolve_strftime(dirname_template)

    # Creamos directorios si no existen
    abs_output_dir = os.path.join(settings.MEDIA_ROOT, relative_dirname)
    if not os.path.exists(abs_output_dir):
        logger.info("Se crearan directorios: %s", abs_output_dir)
        os.makedirs(abs_output_dir, mode=0755)

    fd, output_filename = tempfile.mkstemp(dir=abs_output_dir, prefix=prefix,
                                           suffix=suffix)

    # Cerramos FD
    os.close(fd)

    os.chmod(output_filename, 0644)

    __, generated_filename = os.path.split(output_filename)
    return relative_dirname, generated_filename


# TODO: rename to 'get_class_or_func'
def get_class(full_name):
    """Devuelve clase  o func referenciada por `full_name`"""
    splitted = full_name.split(r".")
    if len(splitted) < 2:
        raise OmlError("La clase/func sepecificada no es valida: '{0}'".format(
            full_name))
    module_name = ".".join(splitted[0:-1])
    class_or_func_name = splitted[-1]

    try:

        try:
            module = __import__(module_name)
        except ImportError as e:
            msg = "No se pudo importar el modulo '{0}'".format(module_name)
            logger.warn(msg)
            raise OmlError(msg, e)

        for sub_module_name in splitted[1:-1]:
            module = getattr(module, sub_module_name)

        try:
            clazz = getattr(module, class_or_func_name)
        except AttributeError as e:
            msg = "El modulo '{0}' no posee la clase o func '{1}'".format(
                module_name, class_or_func_name)
            logger.warn(msg)
            raise OmlError(msg, e)

    except OmlError:
        raise

    except Exception as e:
        msg = "No se pudo obtener la clase o func '{0}'".format(full_name)
        logger.warn(msg)
        raise OmlError(msg, e)

    return clazz


get_class_or_func = get_class


@contextmanager
def log_timing(logger, template_message):
    """Loguea el tiempo que ha tardado la ejecucion del codigo contenido
    en `with`.
    :param logger: Logger a utilizar para loguear el mensaje
    :type logger: logging.Logger
    :param template_message: Template para el mensaje. Debe contener %s,
        para reemplazar por el tiempo transcurrido
    :type template_message: str
    """
    start = time.time()
    yield
    logger.info(template_message, (time.time() - start))


REGEX_NOMBRE_DE_COLUMNA_VALIDO = re.compile(r'^[A-Z0-9_]+$')


class ValidadorDeNombreDeCampoExtra(object):

    def validar_nombre_de_columna(self, nombre):
        """Devuelve True si el nombre de columna es valido"""
        return REGEX_NOMBRE_DE_COLUMNA_VALIDO.match(nombre)


def convert_string_in_boolean(cadena):
    if cadena == 'true':
        return True
    elif cadena == 'false':
        return False
    else:
        # por defecto lo casteamos como false
        return False


# FIXME: realizar validacion en el caso que se reciba en otro formato
def convert_fecha_datetime(fecha, final_dia=False):
    """
    Metodo que convierte string fecha en un datatime
    :param fecha: debe tener este formato dd/mm/aaaa
    :return: fecha en datetime
    """
    dia, mes, ano = fecha.split('/')
    hora = 0
    minuto = 0
    if final_dia:
        hora = 23
        minuto = 59
    fecha = timezone.datetime(int(ano), int(mes), int(dia), hora, minuto,
                              tzinfo=timezone.get_current_timezone())
    return fecha


def datetime_hora_minima_dia(fecha):
    minima = timezone.datetime.combine(fecha, datetime.time.min)
    return timezone.make_aware(minima, timezone.get_current_timezone())


def datetime_hora_maxima_dia(fecha):
    maxima = timezone.datetime.combine(fecha, datetime.time.max)
    return timezone.make_aware(maxima, timezone.get_current_timezone())


def fecha_local(fecha_hora):
    return fecha_hora.astimezone(timezone.get_current_timezone()).date()

def fecha_hora_local(fecha_hora):
    return fecha_hora.astimezone(timezone.get_current_timezone())

def convertir_ascii_string(cadena):
    """ Devuelve ascii ignorando caracteres extraños"""
    return cadena.encode('ascii', errors='ignore')


def cast_datetime_part_date(fecha):
    """ Devuelve un datetime part date """
    return fecha.date()


def convert_audio_asterisk_path_astdb(audio_asterisk):
    """convert audio_asterisk en oml/audio"""
    audio_asterisk = audio_asterisk.name.split("/")
    audio_name = audio_asterisk[1].split(".")
    audio_asterisk = os.path.join(settings.OML_AUDIO_FOLDER, audio_name[0])
    return audio_asterisk


class UnicodeWriter:            # tomado de https://docs.python.org/2/library/csv.html
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def validar_solo_ascii_y_sin_espacios(
        cadena,
        error_ascii='el texto no puede contener tildes ni caracteres no ASCII',
        error_espacios='el texto no puede contener espacios'):
    """
    Valida que no hayan espacios ni caracteres no ASCII
    """
    if ' ' in cadena:
        raise ValidationError(error_espacios)
    if any([(ord(i) >= 128) for i in cadena]):
        raise ValidationError(error_ascii)


def validar_nombres_campanas(nombre):
    """
    Valida que no hayan espacios ni caracteres no ASCII en los nombres de campañas
    """
    error_ascii = 'el nombre no puede contener tildes ni caracteres no ASCII'
    error_espacios = 'el nombre no puede contener espacios'
    validar_solo_ascii_y_sin_espacios(nombre, error_ascii, error_espacios)
