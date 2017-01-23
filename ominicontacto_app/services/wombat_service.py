# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import subprocess
import os
import tempfile

from django.conf import settings
#from ominicontacto_app.services import Wombat_config


logger = logging.getLogger(__name__)


class WombatService():

    def update_config_wombat(self):
        """Realiza un update en la config de wombat

        :returns: int -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign.json")
        try:
            #subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            print subprocess.check_output(['curl', '--user',
                                    ':'.join([settings.OML_WOMBAT_USER,
                                              settings.OML_WOMBAT_PASSWORD]),
                                     '-i', '-X', 'POST', '--data-urlencode',
                                     '@'.join(['data', filename]),
                                     '/'.join([settings.OML_WOMBAT_URL,
                                               'api/edit/campaign/?mode=E'])])
            logger.info("actualizacion en WOMBAT OK")
            return 0
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            print e
