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

"""
Genera archivos de configuración para Asterisk: dialplan y queues.
"""

from __future__ import unicode_literals

import datetime
import os
import tempfile
import traceback
import time
import json
import base64
from pathlib import Path

from django.conf import settings
from django.utils.translation import ugettext as _

from configuracion_telefonia_app.models import RutaSaliente, TroncalSIP, Playlist
from ominicontacto_app.models import (
    AgenteProfile, SupervisorProfile, ClienteWebPhoneProfile, Campana
)
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeQueueFactory, GeneradorDePedazoDeAgenteFactory,
    GeneradorDePedazoDeRutasSalientesFactory, GeneradorDePedazoDePlaylistFactory,
)
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from ominicontacto_app.services.redis.redis_streams import RedisStreams
import logging as _logging

logger = _logging.getLogger(__name__)


class SipConfigCreator(object):

    def __init__(self):
        self._sip_config_file = SipConfigFile()
        self._generador_factory = GeneradorDePedazoDeAgenteFactory()

    def _generar_config_sip(self, agente, es_externo=False):
        """Genera la configuracion para el sip endpoint.

        :param agente: Agente/Supervisor/ClienteWebphone para la cual hay crear config sip
        :              Debe tener .sip_extension y .user
        :type agente: ominicontacto_app.models.AgenteProfile
        :             o ominicontacto_app.models.SupervisorProfile
        :             o ominicontacto_app.models.ClienteWebphoneProfile
        :param externo: Indica si es un cliente Webphone
        :returns: str -- config sip para los agentes/supervisores/clientes webphone
        """
        context = 'from-oml'
        if es_externo:
            context = 'from-pstn'

        # assert agente is not None, "AgenteProfile == None"
        assert agente.user.get_full_name() is not None,\
            "agente.user.get_full_name() == None"
        assert agente.sip_extension is not None, "agente.sip_extension  == None"

        partes = []
        param_generales = {
            'oml_agente_name': agente.get_asterisk_caller_id(),
            'oml_agente_sip': agente.sip_extension,
            'oml_context': context,
        }

        generador_agente = self._generador_factory.crear_generador_para_agente(
            param_generales)
        partes.append(generador_agente.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_para_generar_config_sip(self):
        """Devuelve los agente para crear config de sip.
        """
        return AgenteProfile.objects.all()

    def _obtener_supervisores_para_generar_config_sip(self):
        """Devuelve los supervisor para crear config de sip.
        """
        return SupervisorProfile.objects.all()

    def _obtener_clientes_webphone_para_generar_config_sip(self):
        """Devuelve los supervisor para crear config de sip.
        """
        return ClienteWebPhoneProfile.objects.all()

    def create_config_sip(self):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `queue` es pasada por parametro,
        se genera solo para dicha queue.
        """

        agentes = self._obtener_todas_para_generar_config_sip()
        sip = []
        for agente in agentes:
            logger.info(_("Creando config sip para agente {0}".format(agente.user.get_full_name())))
            try:
                config_chunk = self._generar_config_sip(agente)
                logger.info(_("Config sip generado OK para agente {0}".format(
                    agente.user.get_full_name())))
            except Exception as e:
                logger.exception(
                    _("Error {0}: No se pudo generar configuracion de "
                      "Asterisk para la quene {1}".format(e, agente.user.get_full_name())))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0} al intentar generar traceback".format(e))
                    logger.exception(_("Error al intentar generar traceback"))

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_queue_name': agente.user.get_full_name(),
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            sip.append(config_chunk)

        supervisores = self._obtener_supervisores_para_generar_config_sip()

        for supervisor in supervisores:
            logger.info(_("Creando config sip para supervisor {0}".format(
                supervisor.user.get_full_name())))
            try:
                config_chunk = self._generar_config_sip(supervisor)
                logger.info(_("Config sip generado OK para supervisor {0}".format(
                    supervisor.user.get_full_name())))
            except Exception as e:
                logger.exception(
                    _("Error {0}: no se pudo generar configuracion de "
                      "Asterisk para la queue {1}".format(
                          e, supervisor.user.get_full_name())))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0} al intentar generar traceback".format(e))
                    logger.exception(traceback_lines)

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_queue_name': supervisor.user.get_full_name(),
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()
            sip.append(config_chunk)

        clientes = ClienteWebPhoneProfile.objects.all()
        for cliente in clientes:
            logger.info(_("Creando config sip para cliente {0}".format(
                cliente.user.get_full_name())))
            try:
                config_chunk = self._generar_config_sip(cliente, True)
                logger.info(_("Config sip generado OK para cliente {0}".format(
                    cliente.user.get_full_name())))
            except Exception as e:
                logger.exception(
                    _("Error {0}: no se pudo generar configuracion de "
                      "Asterisk para la queue {1}".format(
                          e, cliente.user.get_full_name())))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0} al intentar generar traceback".format(e))
                    logger.exception(traceback_lines)

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_queue_name': cliente.user.get_full_name(),
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()
            sip.append(config_chunk)

        self._sip_config_file.write(sip)


class QueuesCreator(object):

    def __init__(self):
        self._queues_config_file = QueuesConfigFile()
        self._generador_factory = GeneradorDePedazoDeQueueFactory()

    def _generar_dialplan(self, campana):
        """Genera el dialplan para una queue.

        :param campana: Campana para la cual hay crear el dialplan
        :type campana: ominicontacto_app.models.Campana
        :returns: str -- dialplan para la queue
        """

        assert campana.queue_campana is not None, "campana.queue_campana == None"

        retry = 1
        if campana.queue_campana.retry:
            retry = campana.queue_campana.retry

        audio_entrada = campana.queue_campana.audio_previo_conexion_llamada
        if audio_entrada:
            announce = os.path.join(
                settings.OML_AUDIO_FOLDER, audio_entrada.get_filename_audio_asterisk())
        else:
            announce = "beep"

        partes = []
        param_generales = {
            'oml_queue_name': campana.get_queue_id_name(),
            'oml_queue_type': campana.type,
            'oml_strategy': campana.queue_campana.strategy,
            'oml_timeout': campana.queue_campana.timeout,
            'oml_servicelevel': campana.queue_campana.servicelevel,
            'oml_weight': campana.queue_campana.weight,
            'oml_wrapuptime': campana.queue_campana.wrapuptime,
            'oml_maxlen': campana.queue_campana.maxlen,
            'oml_retry': retry,
            'oml_announce': announce,
        }

        # QUEUE: Creamos la porción inicial del Queue.
        generador_queue = self._generador_factory. \
            crear_generador_para_queue(param_generales)
        partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _generar_dialplan_entrantes(self, campana):
        """Genera el dialplan para una queue.

        :param campana: Campana para la cual hay crear el dialplan
        :type campana: ominicontacto_app.models.Campana
        :returns: str -- dialplan para la queue
        """
        assert campana.queue_campana is not None, "campana.queue_campana == None"

        retry = 1
        if campana.queue_campana.retry:
            retry = campana.queue_campana.retry

        # TODO: OML-496
        audio_asterisk = campana.queue_campana.announce
        if audio_asterisk:
            audio_split = audio_asterisk.split("/")
            audio_name = audio_split[1]
            audio_name = audio_name.split(".")
            periodic_announce = os.path.join(
                settings.OML_AUDIO_FOLDER, audio_name[0])
        else:
            periodic_announce = ""

        audio_entrada = campana.queue_campana.audio_previo_conexion_llamada
        if audio_entrada:
            announce = os.path.join(
                settings.OML_AUDIO_FOLDER, audio_entrada.get_filename_audio_asterisk())
        else:
            announce = "beep"

        partes = []
        param_generales = {
            'oml_queue_name': campana.get_queue_id_name(),
            'oml_queue_type': campana.type,
            'oml_strategy': campana.queue_campana.strategy,
            'oml_timeout': campana.queue_campana.timeout,
            'oml_servicelevel': campana.queue_campana.servicelevel,
            'oml_weight': campana.queue_campana.weight,
            'oml_wrapuptime': campana.queue_campana.wrapuptime,
            'oml_maxlen': campana.queue_campana.maxlen,
            'oml_retry': retry,
            'oml_periodic-announce': periodic_announce,
            'oml_periodic-announce-frequency': campana.queue_campana.announce_frequency,
            'oml_announce-holdtime': campana.queue_campana.announce_holdtime,
            'oml_ivr-breakdown': campana.queue_campana.ivr_breakdown,
            'oml_announce_position': 'yes' if campana.queue_campana.announce_position else 'no',
            'oml_announce_frequency': campana.queue_campana.wait_announce_frequency,
            'oml_announce': announce,
        }

        ivr_breakdown = campana.queue_campana.ivr_breakdown
        if ivr_breakdown is not None:
            oml_ivr_breakdown = 'sub-oml-module-ivrbreakout'
        else:
            oml_ivr_breakdown = ''

        param_generales.update({'oml_ivr-breakdown': oml_ivr_breakdown})

        # QUEUE: Creamos la porción inicial del Queue.
        generador_queue = self._generador_factory. \
            crear_generador_para_queue_entrante(param_generales)
        partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_para_generar_dialplan(self):
        """
        Devuelve las queues para crear el dialplan.
        Exclude las entrantes
        """
        return Campana.objects.obtener_all_dialplan_asterisk().exclude(
            type=Campana.TYPE_ENTRANTE)

    def _obtener_todas_entrante_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        return Campana.objects.obtener_all_dialplan_asterisk().filter(
            type=Campana.TYPE_ENTRANTE)

    def create_dialplan(self, campana=None, campanas=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `queue` es pasada por parametro,
        se genera solo para dicha queue.
        """

        if campanas:
            pass
        elif campana:
            campanas = [campana]
        else:
            campanas = self._obtener_todas_para_generar_dialplan()
        dialplan = []
        for campana in campanas:
            logger.info(_("Creando dialplan para queue {0}".format(campana.nombre)))
            try:
                config_chunk = self._generar_dialplan(campana)
                logger.info(_("Dialplan generado OK para queue {0}".format(campana.nombre)))
            except Exception as e:
                logger.exception(
                    _("Error {0}: No se pudo generar configuracion de "
                      "Asterisk para la queue {1}".format(e, campana.nombre)))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0}: al intentar generar traceback".format(
                        e))
                    logger.exception(traceback)

                # FAILED: Creamos la porción para el fallo del Dialplan.
                param_failed = {'oml_queue_name': campana.nombre,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            dialplan.append(config_chunk)
        campanas_entrantes = self._obtener_todas_entrante_para_generar_dialplan()
        for campana in campanas_entrantes:
            logger.info(_("Creando dialplan para queue {0}".format(campana.nombre)))
            try:
                config_chunk = self._generar_dialplan_entrantes(campana)
                logger.info(_("Dialplan generado OK para queue {0}".format(campana.nombre)))
            except Exception as e:
                logger.exception(
                    _("Error {0}: no se pudo generar configuracion de "
                      "Asterisk para la queue {1}".format(e, campana.nombre)))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0} al intentar generar traceback".format(e))
                    logger.exception(traceback_lines)

                # FAILED: Creamos la porción para el fallo del Dialplan.
                param_failed = {'oml_queue_name': campana.nombre,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            dialplan.append(config_chunk)

        self._queues_config_file.write(dialplan)


class RutasSalientesConfigCreator(object):

    def __init__(self):
        self._rutas_config_file = RutasSalientesConfigFile()
        self._generador_factory = GeneradorDePedazoDeRutasSalientesFactory()

    def _generar_config(self, ruta):
        """Genera el dialplan para una ruta.

        :param ruta: ruta para la cual hay crear config asterisk
        :type RutaSaliente: configuracion_telefonia_app.models.RutaSaliente
        :returns: str -- config para las rutas
        """

        partes = []
        patrones = self._obtener_patrones_ordenados(ruta)
        for orden, patron in patrones:
            if patron.prefix:
                dialpatern = ''.join(("_", str(patron.prefix), patron.match_pattern))
            else:
                dialpatern = ''.join(("_", patron.match_pattern))
            param_generales = {
                'oml-ruta-id': ruta.id,
                'oml-ruta-dialpatern': dialpatern,
                'oml-ruta-orden-patern': orden
            }

            generador_ruta = self._generador_factory.crear_generador_para_patron_ruta_saliente(
                param_generales)
            partes.append(generador_ruta.generar_pedazo())

        return ''.join(partes)

    def _obtener_patrones_ordenados(self, ruta):
        """ devuelve patrones ordenados con enumerate"""
        return list(enumerate(ruta.patrones_de_discado.all(), start=1))

    def _obtener_todas_para_generar_config_rutas(self):
        """Devuelve las rutas salientes para config rutas
        """
        return RutaSaliente.objects.all().order_by('orden')

    def _obtener_todas_menos_una_ruta_para_generar_config_rutas(self, ruta):
        """Devuelve las rutas salientes para config rutas menos la ruta pasada por parametro
        """
        return RutaSaliente.objects.exclude(pk=ruta.id).order_by('orden')

    def create_config_asterisk(self, ruta=None, rutas=None, ruta_exclude=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `ruta` es pasada por parametro,
        se genera solo para dicha ruta.
        """

        if rutas:
            pass
        elif ruta:
            rutas = [ruta]
        elif ruta_exclude:
            rutas = self._obtener_todas_menos_una_ruta_para_generar_config_rutas(ruta_exclude)
        else:
            rutas = self._obtener_todas_para_generar_config_rutas()
        rutas_file = []

        # agrego el encabezado de las rutas
        rutas_file.append("[oml-outr]\n")

        # agrego los include
        for ruta in rutas:
            rutas_file.append("include => oml-outr-{0}\n".format(ruta.id))

        # Agrega parametros
        rutas_file.append("exten => i,1,Verbose(2, no existe patron)\n")
        rutas_file.append("same => n,Set(__DIALSTATUS=NONDIALPLAN)\n")
        rutas_file.append("same => n,Set(SHARED(OMLCALLSTATUS,${OMLMOTHERCHAN})=${DIALSTATUS})\n")
        gosub = \
            "same => n,Gosub(sub-oml-hangup,s,1(FAIL FAIL FAIL no hay ruta para ${OMLOUTNUM}))\n"
        rutas_file.append(gosub)

        # agrego las rutas con los patrones de discado
        for ruta in rutas:
            logger.info(_("Creando config sip para ruta saliente {0}".format(ruta.id)))
            rutas_file.append("\n[oml-outr-{0}]\n".format(ruta.id))
            rutas_file.append("include => oml-outr-{0}-custom".format(ruta.id))
            try:
                config_chunk = self._generar_config(ruta)
                logger.info(_("Config generado OK para ruta saliente {0}".format(ruta.id)))
            except Exception as e:
                logger.exception(
                    _("Error {0}: No se pudo generar configuracion de "
                      "Asterisk para la ruta {1}".format(e, ruta.id)))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0}: al intentar generar traceback".format(
                        e))
                    logger.exception(traceback_lines)

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_ruta_name': ruta.nombre,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            rutas_file.append(config_chunk)

        self._rutas_config_file.write(rutas_file)


class SipTrunksConfigCreator(object):

    def __init__(self):
        self._chansip_trunks_config_file = ChanSipTrunksConfigFile()
        self._pjsip_trunks_config_file = PJSipTrunksConfigFile()

    def _obtener_todas_para_generar_config_rutas(self):
        """Devuelve todas para config troncales
        """
        return TroncalSIP.objects.all()

    def _obtener_todas_menos_un_troncal_para_generar_config_troncales(self, trunk):
        """Devuelve los troncales para configmenos el troncal pasada por parametro
        """
        return TroncalSIP.objects.exclude(pk=trunk.id)

    def create_config_asterisk(self, trunk=None, trunks=None, trunk_exclude=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `trunk` es pasada por parametro,
        se genera solo para dicha trunk.
        """

        if trunks:
            pass
        elif trunk:
            trunks = [trunk]
        elif trunk_exclude:
            trunks = self._obtener_todas_menos_un_troncal_para_generar_config_troncales(
                trunk_exclude)
        else:
            trunks = self._obtener_todas_para_generar_config_rutas()
        chansip_trunk_file = []
        pjsip_trunk_file = []

        for trunk in trunks:
            logger.info(_("Creando config troncal sip {0}".format(trunk.id)))
            if trunk.tecnologia == TroncalSIP.CHANSIP:
                chansip_trunk_file.append("\n[{0}]\n{1}\n".format(
                    trunk.nombre, trunk.text_config.replace("\r", "")))
            elif trunk.tecnologia == TroncalSIP.PJSIP:
                pjsip_trunk_file.append("\n[{0}]\n{1}\n".format(
                    trunk.nombre, trunk.text_config.replace("\r", "")))
        self._chansip_trunks_config_file.write(chansip_trunk_file)
        self._pjsip_trunks_config_file.write(pjsip_trunk_file)


class SipRegistrationsConfigCreator(object):

    def __init__(self):
        self._sip_registrations_config_file = SipRegistrationsConfigFile()

    def _obtener_todas_para_generar_config_rutas(self):
        """Devuelve todas para config troncales
        """
        return TroncalSIP.objects.all()

    def _obtener_todas_menos_un_troncal_para_generar_config_troncales(self, trunk):
        """Devuelve los troncales para configmenos el troncal pasada por parametro
        """
        return TroncalSIP.objects.exclude(pk=trunk.id)

    def create_config_asterisk(self, trunk=None, trunks=None, trunk_exclude=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `trunk` es pasada por parametro,
        se genera solo para dicha trunk.
        """

        if trunks:
            pass
        elif trunk:
            trunks = [trunk]
        elif trunk_exclude:
            trunks = self._obtener_todas_menos_un_troncal_para_generar_config_troncales(
                trunk_exclude)
        else:
            trunks = self._obtener_todas_para_generar_config_rutas()
        trunk_file = []

        for trunk in trunks:
            logger.info(_("Creando config troncal sip {0}".format(trunk.id)))
            trunk_file.append("register=>{0}\n".format(trunk.register_string))

        self._sip_registrations_config_file.write(trunk_file)


class PlaylistsConfigCreator(object):

    def __init__(self):
        self._playlist_config_file = PlaylistsConfigFile()
        self._generador_factory = GeneradorDePedazoDePlaylistFactory()

    def _generar_config(self, playlist):
        """Genera el dialplan para una playlist.

        :param playlist: playlist para la cual hay crear config asterisk
        :type Playlist: configuracion_telefonia_app.models.Playlist
        :returns: str -- config para la playlist
        """

        param_generales = {
            'oml_nombre_playlist': playlist.nombre,
        }
        generador_playlists = self._generador_factory.crear_generador_para_playlist(
            param_generales)
        return generador_playlists.generar_pedazo()

    def create_config_asterisk(self):
        """Crea el archivo de dialplan para playlists existentes
        """

        playlists = Playlist.objects.all()
        playlists_file = []

        for playlist in playlists:
            logger.info(_("Creando config para playlist {0}".format(playlist.id)))
            try:
                config_chunk = self._generar_config(playlist)
                logger.info(_("Config generado OK para playlist {0}".format(playlist.id)))
            except Exception as e:
                logger.exception(
                    _("Error {0}: No se pudo generar configuracion de "
                      "Asterisk para la playlist {1}".format(e, playlist.id)))
                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except Exception as e:
                    traceback_lines = _("Error {0}: al intentar generar traceback".format(
                        e))
                    logger.exception(traceback_lines)

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_playlist_name': playlist.nombre,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            playlists_file.append(config_chunk)

        self._playlist_config_file.write(playlists_file)


# #########################################
#    Reloader
# #########################################

class AsteriskConfigReloader(object):

    MOH_MODULE = 'res_musiconhold.so'
    SIP_TRUNKS_MODULE = 'res_pjsip.so'
    AGENTS_SIP_MODULE = 'res_pjsip.so'
    OUT_ROUTE_MODULE = 'pbx_config.so'

    def reload_asterisk(self):
        """Realiza reload de configuracion de Asterisk usando AMI
        """
        manager = AMIManagerConnector()
        manager.connect()
        manager._ami_manager('command', 'module reload')
        manager.disconnect()

    def reload_module(self, module):
        """
        Realiza reload de configuracion de Asterisk usando AMI
        ATENCION: El comando parece estar blacklisted.
        """
        manager = AMIManagerConnector()
        manager.connect()
        manager._ami_manager('command', 'module reload {0}'.format(module))
        manager.disconnect()


class AsteriskMOHConfigReloader(object):

    def reload_music_on_hold_config(self):
        """Realiza reload de configuracion de Asterisk usando AMI
        """
        # TODO: Actualmente  el comando  manager.command(content) del metodo _ami_action
        #       esta devolviendo estos headers:
        #       {'Response': 'Error', 'ActionID': 'xxx', 'Message': 'Command blacklisted'}
        manager = AMIManagerConnector()
        manager.connect()
        manager._ami_manager('command', 'module unload res_musiconhold.so')
        time.sleep(2)
        manager._ami_manager('command', 'module load res_musiconhold.so')
        manager.disconnect()


# #########################################
#    Config Files
# #########################################


class ConfigFile(object):
    def __init__(self, filename):
        self._filename = filename

    def write(self, contenidos):
        tmp_fd, tmp_filename = tempfile.mkstemp()
        try:
            tmp_file_obj = os.fdopen(tmp_fd, 'w', encoding='utf-8')
            contenidos_str = ''
            for contenido in contenidos:
                assert isinstance(contenido, str), \
                    _("Objeto NO es unicode: {0}".format(type(contenido)))
                tmp_file_obj.write(contenido)
                contenidos_str += contenido

            tmp_file_obj.close()

            redis_stream = RedisStreams()
            __, nombre_archivo = os.path.split(self._filename)
            content = {
                'archivo': nombre_archivo,
                'content': contenidos_str,
                'type': 'CONF_FILE'
            }
            redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))

        finally:
            try:
                os.remove(tmp_filename)
            except Exception as e:
                logger.exception(_("Error {0} al intentar borrar temporal {1}".format(
                    e, tmp_filename)))


class SipConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_SIP_FILENAME.strip()
        super(SipConfigFile, self).__init__(filename)


class QueuesConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_QUEUES_FILENAME.strip()
        super(QueuesConfigFile, self).__init__(filename)


class RutasSalientesConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_RUTAS_SALIENTES_FILENAME.strip()
        super(RutasSalientesConfigFile, self).__init__(filename)


class ChanSipTrunksConfigFile(ConfigFile):
    def __init__(self):
        filename = "oml_sip_trunks.conf"
        super(ChanSipTrunksConfigFile, self).__init__(filename)


class PJSipTrunksConfigFile(ConfigFile):
    def __init__(self):
        filename = "oml_pjsip_trunks.conf"
        super(PJSipTrunksConfigFile, self).__init__(filename)


class SipRegistrationsConfigFile(ConfigFile):
    def __init__(self):
        filename = "oml_sip_registrations.conf"
        super(SipRegistrationsConfigFile, self).__init__(filename)


class PlaylistsConfigFile(ConfigFile):
    def __init__(self):
        filename = "oml_moh.conf"
        super(PlaylistsConfigFile, self).__init__(filename)


class AudioConfigFile(object):
    PLAYLIST_LOCAL_FOLDER = 'musicas_asterisk'
    ASTERISK_MOH_FOLDER = 'moh'

    def __init__(self, audio):
        filename = audio.audio_asterisk.name
        self._filename = os.path.join(settings.MEDIA_ROOT, filename)
        self.es_archivo_playlist = False
        if self.PLAYLIST_LOCAL_FOLDER in filename:
            self.es_archivo_playlist = True
            self.nombre_archivo = filename.replace(
                self.PLAYLIST_LOCAL_FOLDER, self.ASTERISK_MOH_FOLDER)
        else:
            __, self.nombre_archivo = os.path.split(self._filename)
        self.redis_stream = RedisStreams()

    def copy_asterisk(self):
        # por el momento usar el mismo método pero cambiar la funcionalidad
        # hasta posterior refactor
        self._filename = self._filename.replace('//', '/')
        content = {
            'archivo': self.nombre_archivo,
            'type': 'AUDIO_CUSTOM',
            'action': 'COPY',
            'content': self._encode_audio_base64_str()
        }
        self.redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))

    def delete_asterisk(self):
        self._filename = self._filename.replace('//', '/')
        content = {
            'archivo': self.nombre_archivo,
            'type': 'AUDIO_CUSTOM',
            'action': 'DELETE',
            'content': ''
        }
        self.redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))

    def _encode_audio_base64_str(self):
        data = Path(self._filename).read_bytes()
        res = base64.b64encode(data)
        return res.decode('utf-8')
