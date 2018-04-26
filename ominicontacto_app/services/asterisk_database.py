# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.utiles import elimina_espacios
from ominicontacto_app.models import Campana, AgenteProfile, Pausa
from ominicontacto_app.services.asterisk_ami_http import AsteriskHttpClient,\
    AsteriskHttpAsteriskDBError
import logging as _logging

logger = _logging.getLogger(__name__)


class CampanaFamily(object):

    def _genera_dict(self, campana):

        dict_campana = {
            'QNAME': "{0}_{1}".format(campana.id, elimina_espacios(campana.nombre)),
            'TYPE': campana.type,
            'REC': campana.queue_campana.auto_grabacion,
            'AMD': campana.queue_campana.detectar_contestadores,
            'CALLAGENTACTION': campana.tipo_interaccion,
            'RINGTIME': campana.queue_campana.timeout,
            'QUEUETIME': campana.queue_campana.wait,
            'MAXQCALLS': campana.queue_campana.maxlen,
            'SL': campana.queue_campana.servicelevel,
            'TC': "",  # a partir de esta variable no se usan
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
            'FAILOVER': "",
        }

        if campana.queue_campana.audio_para_contestadores:
            dict_campana.update({'AMDPLAY': "oml/{0}".format(
                    campana.queue_campana.audio_para_contestadores.get_filename_audio_asterisk())})

        if campana.queue_campana.audio_de_ingreso:
            dict_campana.update({'WELCOMEPLAY': "oml/{0}".format(
                campana.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())})

        if campana.formulario:
            dict_campana.update({'IDFORM': campana.formulario.pk})
        else:
            dict_campana.update({'IDFORM': ""})

        if campana.sitio_externo:
            dict_campana.update({'IDEXTERNALURL': campana.sitio_externo.pk})
        else:
            dict_campana.update({'IDEXTERNALURL': ""})

        return dict_campana

    def create_dict(self, campana):
        dict_campana = self._genera_dict(campana)
        return dict_campana

    def _obtener_todas_campana_para_generar_familys(self):
        """Devuelve las campanas para generar .
        """
        return Campana.objects.obtener_all_dialplan_asterisk()

    def create_familys(self, campana=None, campanas=None):
        """Crea familys en database de asterisk
        """

        if campanas:
            pass
        elif campana:
            campanas = [campana]
        else:
            campanas = self._obtener_todas_campana_para_generar_familys()
        client = AsteriskHttpClient()
        client.login()
        for campana in campanas:
            logger.info("Creando familys para campana %s", campana.nombre)
            variables = self.create_dict(campana)

            for key, val in variables.items():
                try:
                    family = "/OML/CAMP/{0}/".format(campana.id)
                    client.asterisk_db("DBPut", family, key, val=val)
                except AsteriskHttpAsteriskDBError:
                    logger.exception("Error al intentar DBPut al insertar"
                                     " en la family {0} la siguiente key={1}"
                                     " y val={2}".format(family, key, val))

    def delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def regenerar_familys_campana(self):
        """regenera la family de las campana"""
        self.delete_tree_family("/OML/CAMP")
        self.create_familys()


class AgenteFamily(object):

    def _genera_dict(self, agente):

        dict_agente = {
            'SIP': agente.sip_extension,
            'STATUS': ""
        }

        return dict_agente

    def create_dict(self, agente):
        dict_agente = self._genera_dict(agente)
        return dict_agente

    def _obtener_todos_agentes_para_generar_family(self):
        """Obtengo todos los agentes activos"""
        return AgenteProfile.objects.obtener_agentes_activos()

    def create_familys(self, agente=None, agentes=None):
        """Crea familys en database de asterisk
        """

        if agentes:
            pass
        elif agente:
            agentes = [agente]
        else:
            agentes = self._obtener_todos_agentes_para_generar_family()
        client = AsteriskHttpClient()
        client.login()
        for agente in agentes:
            logger.info("Creando familys para agente %s", agente.id)
            variables = self.create_dict(agente)

            for key, val in variables.items():
                try:
                    family = "/OML/AGENT/{0}/".format(agente.id)
                    client.asterisk_db("DBPut", family, key, val=val)
                except AsteriskHttpAsteriskDBError:
                    logger.exception("Error al intentar DBPut al insertar"
                                     " en la family {0} la siguiente key={1}"
                                     " y val={2}".format(family, key, val))

    def delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def regenerar_familys_agente(self):
        """regenera la family de los agentes"""
        self.delete_tree_family("/OML/AGENT")
        self.create_familys()


class PausaFamily(object):

    def _obtener_todas_pausas_para_generar_family(self):
        """Obtener todas pausas"""
        return Pausa.objects.activas()

    def create_familys(self):
        """Crea family en database asterisk"""

        pausas = self._obtener_todas_pausas_para_generar_family()
        for pausa in pausas:
            logger.info("Creando familys para pausa %s", pausa.nombre)
            try:
                client = AsteriskHttpClient()
                client.login()
                family = "/OML/PAUSE/{0}/".format(pausa.id)
                client.asterisk_db("DBPut", family, "NAME", val=pausa.nombre)
            except AsteriskHttpAsteriskDBError:
                logger.exception("Error al intentar DBPut al insertar"
                                 " en la family {0} la siguiente ket=NAME"
                                 " y val={1}".format(family, pausa.nombre))

    def delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def regenerar_familys_pausa(self):
        """regenera la family de las pausas"""
        self.delete_tree_family("/OML/PAUSE")
        self.create_familys()


class RegenerarAsteriskFamilysOML(object):

    def __init__(self):
        self.campana_family = CampanaFamily()
        self.agente_family = AgenteFamily()
        self.pausa_family = PausaFamily()

    def regenerar_asterisk(self):
        self.campana_family.regenerar_familys_campana()
        self.agente_family.regenerar_familys_agente()
        self.pausa_family.regenerar_familys_pausa()
