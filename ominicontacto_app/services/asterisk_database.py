# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.utiles import elimina_espacios
from ominicontacto_app.models import Campana
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
        elif campana.sitio_externo:
            dict_campana.update({'IDEXTERNALURL': campana.sitio_externo.pk})

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

    def delete_all_family(self):
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree("/OML/CAMP")
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de /OML/CAMP/")
