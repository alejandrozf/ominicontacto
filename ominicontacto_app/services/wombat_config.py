# -*- coding: utf-8 -*-

"""Servicio para crear los json para crear los objectos en wombat"""

from __future__ import unicode_literals

import os
import shutil
import tempfile
import logging
import json

from django.conf import settings
from ominicontacto_app.utiles import elimina_espacios

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
            "name": "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),

            "priority": 10,
            "pace": "RUNNABLE",
            "pauseWhenFinished": 0,
            "batchSize": 100,
            "securityKey": "",

            "timeStartHr": campana.actuacionvigente.get_hora_desde_wombat(),
            "timeEndHr": campana.actuacionvigente.get_hora_hasta_wombat(),
            "timeDow": campana.actuacionvigente.get_dias_vigente_wombat(),

            "dial_timeout": 50000,
            "maxCallLength": 0,
            "dial_clid": elimina_espacios(campana.nombre),
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
            "httpNotify": "http://{0}:8000/wombat/logs/".format(
                settings.OML_OMNILEADS_IP),
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


class TrunkCreator(object):

    def __init__(self):
        self._trunk_config_file = TrunkConfigFile()

    def _generar_json(self):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_trunk = {
           "trunkId": {
                "trunkId": 1
           }
        }

        return json.dumps(dict_trunk)

    def create_json(self, campana):
        """Crea el archivo de json para trunk de campana
        """
        logger.info("Creando json para trunk  campana %s", campana.nombre)
        config_chunk = self._generar_json()
        self._trunk_config_file.write(config_chunk)


class RescheduleRuleCreator(object):

    def __init__(self):
        self._reschedule_config_file = RescheduleRuleConfigFile()

    def _generar_json(self, parametros):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_reschedule = {
            "status": parametros[0],
            "statusExt": parametros[1],
            "maxAttempts": parametros[2],
            "retryAfterS": parametros[3],
            "mode": parametros[4]
        }

        return json.dumps(dict_reschedule)

    def create_json(self, campana, parametros):
        """Crea el archivo de json para trunk de campana
        """
        logger.info("Creando json para regla de reschedule para la campana %s",
                    campana.nombre)
        config_chunk = self._generar_json(parametros)
        self._reschedule_config_file.write(config_chunk)


class EndPointCreator(object):

    def __init__(self):
        self._endpoint_config_file = EndPointConfigFile()

    def _generar_json(self, campana):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_endpoint = {
            "type": "QUEUE",
            "queueName": "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),
            "name": "",
            "astId": {
                "id": 1
            },
            "idx": "",
            "campaignId": "",
            "maxChannels": campana.queue_campana.maxlen,
            "extension": '0077' + str(campana.queue_campana.queue_asterisk),
            "context": "from-queue-fts",
            "boostFactor": 1,
            "maxWaitingCalls": 2,
            "reverseDialing": False,
            "stepwiseReverse": False,
            "securityKey": "",
            "description": "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),
            "dialFind": "",
            "dialReplace": ""
        }

        return json.dumps(dict_endpoint)

    def create_json(self, campana):
        """Crea el archivo de json para trunk de campana
        """
        logger.info("Creando json end point para la campana %s",
                    campana.nombre)
        config_chunk = self._generar_json(campana)
        self._endpoint_config_file.write(config_chunk)


class CampanaEndPointCreator(object):

    def __init__(self):
        self._campana_endpoint_config_file = CampanaEndPointConfigFile()

    def _generar_json(self, campana):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_trunk = {
            "epId": {
                "epId": campana.queue_campana.ep_id_wombat
            }
        }

        return json.dumps(dict_trunk)

    def create_json(self, campana):
        """Crea el archivo de json para endpoint de campana
        """
        logger.info("Creando json para asociacion campana %s endpoint",
                    campana.nombre)
        config_chunk = self._generar_json(campana)
        self._campana_endpoint_config_file.write(config_chunk)


class CampanaListCreator(object):

    def __init__(self):
        self._campana_list_config_file = CampanaListConfigFile()

    def _generar_json(self, list):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_trunk = {
            "cl": {
                "listId": list
            }
        }

        return json.dumps(dict_trunk)

    def create_json(self, list):
        """Crea el archivo de json para list de campana
        """
        logger.info("Creando json para asociacion lista %s campana",
                    list)
        config_chunk = self._generar_json(list)
        self._campana_list_config_file.write(config_chunk)


class CampanaDeleteListCreator(object):

    def __init__(self):
        self._campana_list_config_file = CampanaDesListConfigFile()

    def _generar_json(self, cclId):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_trunk = {
            "cclId": cclId
        }

        return json.dumps(dict_trunk)

    def create_json(self, cclId):
        """Crea el archivo de json para list de campana
        """
        logger.info("Creando json para asociacion lista %s campana",
                    list)
        config_chunk = self._generar_json(cclId)
        self._campana_list_config_file.write(config_chunk)


class CampanaEndPointDelete(object):

    def __init__(self):
        self._campana_endpoint_config_file = CampanaDeleteEndPointConfigFile()

    def _generar_json(self, campana):
        """Genera json.
        :returns: str -- json para la campana
        """

        dict_trunk = {
            "epId": {
                "epId": campana.queue_campana.ep_id_wombat
            }
        }

        return json.dumps(dict_trunk)

    def create_json(self, campana):
        """Crea el archivo de json para endpoint de campana
        """
        logger.info("Creando json para asociacion campana %s endpoint",
                    campana.nombre)
        config_chunk = self._generar_json(campana)
        self._campana_endpoint_config_file.write(config_chunk)


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
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign.json")
        filename = filename.strip()
        super(CampanaConfigFile, self).__init__(filename)


class TrunkConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign_trunk.json")
        filename = filename.strip()
        super(TrunkConfigFile, self).__init__(filename)


class RescheduleRuleConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign_reschedule.json")
        filename = filename.strip()
        super(RescheduleRuleConfigFile, self).__init__(filename)


class EndPointConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newep.json")
        filename = filename.strip()
        super(EndPointConfigFile, self).__init__(filename)


class CampanaEndPointConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign_ep.json")
        filename = filename.strip()
        super(CampanaEndPointConfigFile, self).__init__(filename)


class CampanaListConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign_list.json ")
        filename = filename.strip()
        super(CampanaListConfigFile, self).__init__(filename)


class CampanaListContactoConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "newcampaign_list_contacto.txt ")
        filename = filename.strip()
        super(CampanaListContactoConfigFile, self).__init__(filename)


class CampanaDesListConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "deletecampaign_list.json ")
        filename = filename.strip()
        super(CampanaDesListConfigFile, self).__init__(filename)


class CampanaDeleteEndPointConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "deletecampaign_ep.json")
        filename = filename.strip()
        super(CampanaDeleteEndPointConfigFile, self).__init__(filename)
