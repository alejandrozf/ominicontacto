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

"""Servicio para crear los json para crear los objectos en wombat"""

from __future__ import unicode_literals

import os
import shutil
import tempfile
import logging
import json

from django.conf import settings
from django.utils.translation import gettext as _

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

        campana_id_wombat = ""
        if campana.campaign_id_wombat:
            campana_id_wombat = campana.campaign_id_wombat

        dict_campana = {
            "campaignId": campana_id_wombat,
            "name": campana.get_queue_id_name(),

            "priority": campana.prioridad,
            "pace": "RUNNABLE",
            "pauseWhenFinished": 0,
            "batchSize": 100,
            "securityKey": "",

            "timeStartHr": campana.actuacionvigente.get_hora_desde_wombat(),
            "timeEndHr": campana.actuacionvigente.get_hora_hasta_wombat(),
            "timeDow": campana.actuacionvigente.get_dias_vigente_wombat(),

            "dial_timeout": campana.queue_campana.dial_timeout * 1000,
            "maxCallLength": 0,
            "dial_clid": campana.nombre,
            "agentClid": "",
            "dial_account": "",
            "dial_pres": "",
            "autopause": False,
            "campaignVars": "",

            "initialPredictiveModel": campana.queue_campana.get_string_initial_predictive_model(),
            "initialBoostFactor": float(campana.queue_campana.initial_boost_factor),
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
        logger.info(_("Creando json para campana {0}".format(campana.nombre)))
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
        logger.info(_("Creando json para trunk  campana {0}".format(campana.nombre)))
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
        logger.info(_("Creando json para regla de reschedule para la campana {0}".format(
            campana.nombre)))
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
            "queueName": campana.get_queue_id_name(),
            "name": "",
            "astId": {
                "id": 1
            },
            "idx": "",
            "campaignId": "",
            "maxChannels": campana.queue_campana.maxlen,
            "extension": "s",
            "context": "sub-oml-campaign-2-deliver-contactcall",
            "boostFactor": 1,
            "maxWaitingCalls": 2,
            "reverseDialing": False,
            "stepwiseReverse": False,
            "securityKey": "",
            "description": campana.get_queue_id_name(),
            "dialFind": "",
            "dialReplace": ""
        }

        # Si ya tiene enpoint_id, es para edición
        if (campana.queue_campana.ep_id_wombat):
            dict_endpoint['epId'] = campana.queue_campana.ep_id_wombat

        return json.dumps(dict_endpoint)

    def create_json(self, campana):
        """Crea el archivo de json para trunk de campana
        """
        logger.info(_("Creando json end point para la campana {0}".format(campana.nombre)))
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
        logger.info(_("Creando json para asociacion lista {0} campana".format(list)))
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
        logger.info(_("Creando json para asociacion lista {0} campana".format(list)))
        config_chunk = self._generar_json(cclId)
        self._campana_list_config_file.write(config_chunk)


class ConfigFile(object):
    def __init__(self, filename):
        self._filename = filename

    def write(self, contenido):
        tmp_fd, tmp_filename = tempfile.mkstemp()
        try:
            tmp_file_obj = os.fdopen(tmp_fd, 'w', encoding='utf-8')
            # assert isinstance(contenido, json), \
            #     "Objeto NO es unicode: {0}".format(type(contenido))
            tmp_file_obj.write(contenido)

            tmp_file_obj.close()

            logger.info(_("Copiando file config a {0}".format(self._filename)))
            shutil.copy(tmp_filename, self._filename)
            os.chmod(self._filename, 0o644)

        finally:
            try:
                os.remove(tmp_filename)
            except Exception:
                logger.exception(_("Error al intentar borrar temporal {0}".format(tmp_filename)))


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
