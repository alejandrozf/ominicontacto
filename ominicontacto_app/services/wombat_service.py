# -*- coding: utf-8 -*-

"""Servicio para generar los curl hacia wombat"""

from __future__ import unicode_literals

import logging
import subprocess
import os
import tempfile
import json

from django.conf import settings

logger = logging.getLogger(__name__)


class WombatService():

    def update_config_wombat(self, json_file, url_edit):
        """Realiza un update en la config de wombat

        :returns: json -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                json_file)
        try:
            #subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                    ':'.join([settings.OML_WOMBAT_USER,
                                              settings.OML_WOMBAT_PASSWORD]),
                                     '-X', 'POST', '--data-urlencode',
                                     '@'.join(['data', filename]),
                                     '/'.join([settings.OML_WOMBAT_URL,
                                               url_edit])])
            logger.info("actualizacion en WOMBAT OK")
            return json.loads(out)
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e

    def update_lista_wombat(self, nombre_archivo, url_edit):
        """Realiza un update en la config de wombat

        :returns: out -- salida del comando ejectuado hacia wombat.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()

        try:
            #subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            filename_archivo = settings.OML_WOMBAT_FILENAME + nombre_archivo
            out = subprocess.check_output(['curl', '--user',
                                    ':'.join([settings.OML_WOMBAT_USER,
                                              settings.OML_WOMBAT_PASSWORD]),
                                     '-m', '60', '-X', 'POST', '-w', 'string',
                                     '-d',  "@{0}".format(filename_archivo),
                                    '/'.join([settings.OML_WOMBAT_URL,
                                             url_edit])])
            return out
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e

    def list_config_wombat(self, url_edit):
        """Realiza un list en la config de wombat

        :returns: json -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()

        try:
            #subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                    ':'.join([settings.OML_WOMBAT_USER,
                                              settings.OML_WOMBAT_PASSWORD]),
                                      '-X', 'POST',
                                     '/'.join([settings.OML_WOMBAT_URL,
                                               url_edit])])
            logger.info("list en WOMBAT OK")
            return json.loads(out)
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e
