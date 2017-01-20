# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import shutil
import tempfile
import logging
import json

from django.conf import settings



logger = logging.getLogger(__name__)


class CampanaCreator(object):

    def __init__(self):
        self._campana_config_file = CampanaConfigFile()

    def _generar_json(self, campana):
        """Genera json.

        :param campana: campana para el cual hay que crear el json
        :type campana: ominicontacto_app.models.Campana
        :returns: str -- json para la campana
        """

        assert campana is not None, "Campana == None"

        dict_campana = {
            "name": campana.nombre,

            "priority": 10,
            "pace": "RUNNABLE",
            "pauseWhenFinished": 0,
            "batchSize": 100,
            "securityKey": "",

            "timeStartHr": "000000",
            "timeEndHr": "235959",
            "timeDow": "234567",

            "dial_timeout": 30000,
            "maxCallLength": 0,
            "dial_clid": "",
            "agentClid": "",
            "dial_account": "",
            "dial_pres": "",
            "autopause": False,
            "campaignVars": "",

            "initialPredictiveModel": "OFF",
            "initialBoostFactor": 1.0,
            "amdTracking": "OFF",
            "amdParams": "AMD_MODE & AMD_EXTRA",
            "amdAudioFile": "AMD_FILE",
            "amdFaxFile": "FAX_FILE",

            "addlLogging": "QM_COMPATIBLE",
            "loggingAlias": "alias_nombre",
            "loggingQmVars": "",
            "httpNotify": "",
            "emailEvents": "NO",
            "emailAddresses": ""
        }

        return json.dumps(dict_campana)

    def create_json(self, campana):
        """Crea el archivo de json para campana
        """
        logger.info("Creando json para campana %s", campana.nombre)
        config_chunk = self._generar_json(campana)
        self._campana_config_file.write(config_chunk)


class ConfigFile(object):
    def __init__(self, filename):
        self._filename = filename

    def write(self, contenido):
        tmp_fd, tmp_filename = tempfile.mkstemp()
        try:
            tmp_file_obj = os.fdopen(tmp_fd, 'w')
            # assert isinstance(contenido, json), \
            #     "Objeto NO es unicode: {0}".format(type(contenido))
            tmp_file_obj.write(contenido.encode('utf-8'))

            tmp_file_obj.close()

            logger.info("Copiando file config a %s", self._filename)
            shutil.copy(tmp_filename, self._filename)
            os.chmod(self._filename, 0644)

        finally:
            try:
                os.remove(tmp_filename)
            except:
                logger.exception("Error al intentar borrar temporal %s",
                                 tmp_filename)


class CampanaConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_WOMBAT_FILENAME + "newcampaign.json"
        filename = filename.strip()
        super(CampanaConfigFile, self).__init__(filename)
