# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import subprocess
import os
import tempfile

from django.conf import settings

logger = logging.getLogger(__name__)


class WombatService():

    def update_config_wombat(self, json_file, url_edit):
        """Realiza un update en la config de wombat

        :returns: int -- exit status de proceso ejecutado.
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
                                     '-i', '-X', 'POST', '--data-urlencode',
                                     '@'.join(['data', filename]),
                                     '/'.join([settings.OML_WOMBAT_URL,
                                               url_edit])])
            logger.info("actualizacion en WOMBAT OK")
            return out
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e

    def update_lista_wombat(self, lista, url_edit):
        """Realiza un update en la config de wombat

        :returns: int -- exit status de proceso ejecutado.
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
                                     '-m', '30', '-X', 'POST', '-w', 'string',
                                     '-d',  lista,
                                    '/'.join([settings.OML_WOMBAT_URL,
                                             url_edit])])
            return out
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e
