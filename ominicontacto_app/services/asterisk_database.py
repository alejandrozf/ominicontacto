# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ominicontacto_app.utiles import elimina_espacios
from ominicontacto_app.models import Campana, AgenteProfile, Pausa
from ominicontacto_app.services.asterisk_ami_http import AsteriskHttpClient,\
    AsteriskHttpAsteriskDBError
from configuracion_telefonia_app.models import RutaSaliente, TroncalSIP
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
                    family = "OML/CAMP/{0}".format(campana.id)
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
        self.delete_tree_family("OML/CAMP")
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
        return AgenteProfile.objects.obtener_activos()

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
                    family = "OML/AGENT/{0}".format(agente.id)
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
        self.delete_tree_family("OML/AGENT")
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
                family = "OML/PAUSE/{0}".format(pausa.id)
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
        self.delete_tree_family("OML/PAUSE")
        self.create_familys()


class RutaSalienteFamily(object):

    def _genera_dict_ruta(self, ruta):

        dict_ruta = {
            'NAME': ruta.nombre,
            'RINGTIME': ruta.ring_time,
            'OPTIONS': ruta.dial_options,
            'TRUNKS': len(ruta.secuencia_troncales.all())
        }

        return dict_ruta

    def _genera_dict_patron_discado(self, patron):

        if patron.prefix:
            prefix = len(str(patron.prefix))
        else:
            prefix = None
        dict_patron = {
            'PREFIX': prefix,
            'PREPEND': patron.prepend,
        }

        return dict_patron

    def create_dict_ruta(self, ruta):
        dict_ruta = self._genera_dict_ruta(ruta)
        return dict_ruta

    def create_dict_patron(self, patron):
        dict_ruta = self._genera_dict_patron_discado(patron)
        return dict_ruta

    def _obtener_todas_rutas_para_generar_family(self):
        """Obtengo todos las rutas salientes para generar family"""
        return RutaSaliente.objects.all()

    def _obtener_patrones_ordenados(self, ruta):
        """ devuelve patrones ordenados con enumerate"""
        return list(enumerate(ruta.patrones_de_discado.all(), start=1))

    def _obtener_troncales_ordenados(self, ruta):
        """ devuelve troncales ordenados con enumerate"""
        return list(enumerate(ruta.secuencia_troncales.all().order_by("orden"), start=1))

    def create_familys(self, ruta=None, rutas=None):
        """Crea familys en database de asterisk
        """

        if rutas:
            pass
        elif ruta:
            rutas = [ruta]
        else:
            rutas = self._obtener_todas_rutas_para_generar_family()
        client = AsteriskHttpClient()
        client.login()
        for ruta in rutas:
            # agrego lo datos basico de la ruta saliente
            logger.info("Creando familys para ruta saliente %s", ruta.id)
            variables = self.create_dict_ruta(ruta)

            for key, val in variables.items():
                try:
                    family = "OML/OUTR/{0}".format(ruta.id)
                    client.asterisk_db("DBPut", family, key, val=val)
                except AsteriskHttpAsteriskDBError:
                    logger.exception("Error al intentar DBPut al insertar"
                                     " en la family {0} la siguiente key={1}"
                                     " y val={2}".format(family, key, val))

            # agrego los datos de los patrones de de discado
            patrones = self._obtener_patrones_ordenados(ruta)
            for orden, patron in patrones:
                logger.info("Creando familys para patrones de discado %s", patron.id)
                variables = self.create_dict_patron(patron)

                for key, val in variables.items():
                    try:
                        family = "OML/OUTR/{0}".format(ruta.id)
                        key = "{0}/{1}".format(key, orden)
                        client.asterisk_db("DBPut", family, key, val=val)
                    except AsteriskHttpAsteriskDBError:
                        logger.exception("Error al intentar DBPut al insertar"
                                         " en la family {0} la siguiente key={1}"
                                         " y val={2}".format(family, key, val))

            # agrego lo datos de los troncales
            troncales = self._obtener_troncales_ordenados(ruta)
            for orden, troncal in troncales:
                logger.info("Creando familys para troncales %s", troncal.troncal.id)

                try:
                    family = "OML/OUTR/{0}".format(ruta.id)
                    key = "TRUNK/{0}".format(orden)
                    val = troncal.troncal.nombre
                    client.asterisk_db("DBPut", family, key=key, val=val)
                except AsteriskHttpAsteriskDBError:
                    logger.exception("Error al intentar DBPut al insertar"
                                     " en la family {0} la siguiente key={1}"
                                     " y val={2}".format(family, key, val))

    def _existe_family_key(self, family, key):
        """Consulta en la base de datos si existe la family y clave"""

        try:
            client = AsteriskHttpClient()
            client.login()
            db_get = client.asterisk_db("DBGet", family, key=key)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBGet al consultar con la family {0} y "
                             "la siguiente key={1}".format(family, key))
            return False
        if db_get.response_value == 'success':
            return True

    def delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def delete_family_ruta(self, ruta):
        """Elimina una la family de una ruta"""
        # primero chequeo si existe la family
        family = "OML/OUTR/{0}".format(ruta.id)
        key = "NAME"
        existe_family = self._existe_family_key(family, key)
        if existe_family:
            self.delete_tree_family(family)

    def regenerar_familys_rutas(self, ruta):
        """regenera la family de las rutas"""
        family = "OML/OUTR/{0}".format(ruta.id)
        self.delete_tree_family(family)
        self.create_familys(ruta=ruta)

    def _regenero_trunks_ruta(self, ruta):
        """
        Regenero las entradas para los trunks en la ruta
            /OML/OUTR/XX/TRUNK/N donde xx es la id de la ruta y N el numero de troncal
        """

        # regenero lo datos de los troncales
        troncales = self._obtener_troncales_ordenados(ruta)
        for orden, troncal in troncales:
            logger.info("Creando familys para troncales %s", troncal.troncal.id)

            try:
                client = AsteriskHttpClient()
                client.login()
                family = "OML/OUTR/{0}".format(ruta.id)
                key = "TRUNK/{0}".format(orden)
                val = troncal.troncal.nombre
                client.asterisk_db("DBPut", family, key=key, val=val)
            except AsteriskHttpAsteriskDBError:
                logger.exception("Error al intentar DBPut al insertar"
                                 " en la family {0} la siguiente key={1}"
                                 " y val={2}".format(family, key, val))

    def regenerar_family_trunk_ruta(self, ruta):
        """regeneros lso troncales de la ruta"""
        family = "OML/OUTR/{0}".format(ruta.id)
        key = "NAME"
        existe_family = self._existe_family_key(family, key)
        if existe_family:
            self._regenero_trunks_ruta(ruta)


class TrunkFamily(object):

    def _genera_dict(self, trunk):

        dict_trunk = {
            'NAME': trunk.nombre,
            'CHANNELS': trunk.canales_maximos,
            'CALLERID': trunk.caller_id,
        }

        return dict_trunk

    def create_dict(self, trunk):
        dict_trunk = self._genera_dict(trunk)
        return dict_trunk

    def _obtener_todas_trunks_para_generar_family(self):
        """Obtengo todos los troncales sip para generar family"""
        return TroncalSIP.objects.all()

    def create_familys(self, trunk=None, trunks=None):
        """Crea familys en database de asterisk
        """

        if trunks:
            pass
        elif trunk:
            trunks = [trunk]
        else:
            trunks = self._obtener_todas_trunks_para_generar_family()
        client = AsteriskHttpClient()
        client.login()
        for trunk in trunks:
            # agrego lo datos basico de la ruta saliente
            logger.info("Creando familys para troncal sip %s", trunk.id)
            variables = self.create_dict(trunk)

            for key, val in variables.items():
                try:
                    family = "OML/TRUNK/{0}".format(trunk.id)
                    client.asterisk_db("DBPut", family, key, val=val)
                except AsteriskHttpAsteriskDBError:
                    logger.exception("Error al intentar DBPut al insertar"
                                     " en la family {0} la siguiente key={1}"
                                     " y val={2}".format(family, key, val))

    def _existe_family_key(self, family, key):
        """Consulta en la base de datos si existe la family y clave"""

        try:
            client = AsteriskHttpClient()
            client.login()
            db_get = client.asterisk_db("DBGet", family, key=key)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBGet al consultar con la family {0} y "
                             "la siguiente key={1}".format(family, key))
            return False
        if db_get.response_value == 'success':
            return True

    def delete_tree_family(self, family):
        """Elimina el tree de la family pasada por parametro"""
        try:
            client = AsteriskHttpClient()
            client.login()
            client.asterisk_db_deltree(family)
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBDelTree de {0}".format(family))

    def delete_family_trunk(self, trunk):
        """Elimina una la family de una ruta"""
        # primero chequeo si existe la family
        family = "OML/TRUNK/{0}".format(trunk.id)
        key = "NAME"
        existe_family = self._existe_family_key(family, key)
        if existe_family:
            self.delete_tree_family(family)

    def regenerar_familys_trunks(self):
        """regenera la family de las troncales"""
        self.delete_tree_family("OML/TRUNK")
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


class GlobalsFamily(object):

    def _genera_dict(self):

        dict_globals = {
            'DEFAULTQUEUETIME': 90,
            'DEFAULTRINGTIME': 45,
            'LANG': 'es',
            'OBJ/1': 'sub-oml-in-check-set,s,1',
            'OBJ/2': 'sub-oml-module-tc,s,1',
            'OBJ/3': 'sub-oml-module-ivr,s,1',
            'OBJ/4': 'sub-oml-module-ext,s,1',
            'OBJ/5': 'sub-oml-hangup,s,1',
            'OBJ/6': 'sub-oml-module-survey,s,1',
            'RECFILEPATH': '/var/spool/asterisk/monitor',
            'TYPECALL/1': 'manualCall',
            'TYPECALL/2': 'dialerCall',
            'TYPECALL/3': 'inboundCall',
            'TYPECALL/4': 'previewCall',
            'TYPECALL/5': 'icsCall',
            'TYPECALL/7': 'internalCall',
            'TYPECALL/8': 'transferCall',
            'TYPECALL/9': 'transferOutNumCall',
        }

        return dict_globals

    def create_dict(self):
        dict_globals = self._genera_dict()
        return dict_globals

    def create_familys(self):
        """Crea familys en database de asterisk
        """

        client = AsteriskHttpClient()
        client.login()
        variables = self.create_dict()

        for key, val in variables.items():
            try:
                family = "OML/GLOBALS"
                client.asterisk_db("DBPut", family, key, val=val)
            except AsteriskHttpAsteriskDBError:
                logger.exception("Error al intentar DBPut al insertar"
                                 " en la family {0} la siguiente key={1}"
                                 " y val={2}".format(family, key, val))

    def _existe_family_key(self, family, key):
        """Consulta en la base de datos si existe la family y clave"""

        try:
            client = AsteriskHttpClient()
            client.login()
            db_get = client.asterisk_db("DBGet", family, key=key)
            response_dict = db_get.response_dict
        except AsteriskHttpAsteriskDBError:
            logger.exception("Error al intentar DBGet al consultar con la family {0} y "
                             "la siguiente key={1}".format(family, key))
            return False
        if response_dict['response'] == 'Success':
            return True
