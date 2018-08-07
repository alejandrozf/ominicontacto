# -*- coding: utf-8 -*-

"""
Genera archivos de configuración para Asterisk: dialplan y queues.
"""

from __future__ import unicode_literals

import datetime
import os
import shutil
import subprocess
import tempfile
import traceback

from django.conf import settings
from ominicontacto_app.utiles import (
    elimina_espacios, remplace_espacio_por_guion
)
from ominicontacto_app.models import (
    AgenteProfile, SupervisorProfile, Campana, Pausa
)
from configuracion_telefonia_app.models import RutaSaliente, TroncalSIP
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeQueueFactory, GeneradorDePedazoDeAgenteFactory,
    GeneradorDePedazoDePausaFactory, GeneradorDePedazoDeRutasSalientesFactory
)

import logging as _logging

logger = _logging.getLogger(__name__)


class SipConfigCreator(object):

    def __init__(self):
        self._sip_config_file = SipConfigFile()
        self._generador_factory = GeneradorDePedazoDeAgenteFactory()

    def _generar_config_sip(self, agente):
        """Genera el dialplan para una queue.

        :param agente: Agente para la cual hay crear config sip
        :type agente: ominicontacto_app.models.AgenteProfile
        :returns: str -- config sip para los agentes
        """

        # assert agente is not None, "AgenteProfile == None"
        assert agente.user.get_full_name() is not None,\
            "agente.user.get_full_name() == None"
        assert agente.sip_extension is not None, "agente.sip_extension  == None"

        partes = []
        nombre_agente = remplace_espacio_por_guion(agente.user.get_full_name())
        param_generales = {
            'oml_agente_name': "{0}_{1}".format(agente.id, nombre_agente),
            'oml_agente_sip': agente.sip_extension,
            'oml_kamailio_ip': settings.OML_KAMAILIO_IP,
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

    def create_config_sip(self, agente=None, agentes=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `queue` es pasada por parametro,
        se genera solo para dicha queue.
        """

        if agentes:
            pass
        elif agente:
            agentes = [agente]
        else:
            agentes = self._obtener_todas_para_generar_config_sip()
        sip = []
        for agente in agentes:
            logger.info("Creando config sip para agente %s", agente.user.
                        get_full_name())
            try:
                config_chunk = self._generar_config_sip(agente)
                logger.info("Config sip generado OK para agente %s",
                            agente.user.get_full_name())
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(agente.user.get_full_name()))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

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
            logger.info("Creando config sip para supervisor %s", supervisor.user.
                        get_full_name())
            try:
                config_chunk = self._generar_config_sip(supervisor)
                logger.info("Config sip generado OK para supervisor %s",
                            supervisor.user.get_full_name())
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(supervisor.user.get_full_name()))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_queue_name': supervisor.user.get_full_name(),
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

        partes = []
        param_generales = {
            'oml_queue_name': "{0}_{1}".format(campana.id,
                                               elimina_espacios(campana.nombre)),
            'oml_queue_type': campana.type,
            'oml_strategy': campana.queue_campana.strategy,
            'oml_timeout': campana.queue_campana.timeout,
            'oml_servicelevel': campana.queue_campana.servicelevel,
            'oml_weight': campana.queue_campana.weight,
            'oml_wrapuptime': campana.queue_campana.wrapuptime,
            'oml_maxlen': campana.queue_campana.maxlen,
            'oml_retry': retry
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

        audio_asterisk = campana.queue_campana.announce
        if audio_asterisk:
            audio_split = audio_asterisk.split("/")
            audio_name = audio_split[1]
            audio_name = audio_name.split(".")
            periodic_announce = os.path.join(
                settings.OML_AUDIO_FOLDER, audio_name[0])
        else:
            periodic_announce = ""
        partes = []
        param_generales = {
            'oml_queue_name': "{0}_{1}".format(campana.id,
                                               elimina_espacios(campana.nombre)),
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
        }

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
            logger.info("Creando dialplan para queue %s", campana.nombre)
            try:
                config_chunk = self._generar_dialplan(campana)
                logger.info("Dialplan generado OK para queue %s",
                            campana.nombre)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(campana.nombre))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

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
            logger.info("Creando dialplan para queue %s", campana.nombre)
            try:
                config_chunk = self._generar_dialplan_entrantes(campana)
                logger.info("Dialplan generado OK para queue %s",
                            campana.nombre)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(campana.nombre))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

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


class GlobalsVariableConfigCreator(object):

    def __init__(self):
        self._globals_config_file = GlobalsConfigFile()
        self._generador_sip_agente_factory = GeneradorDePedazoDeAgenteFactory()
        self._generador_pausa_factory = GeneradorDePedazoDePausaFactory()

    def _generar_config_agente(self, agente):
        """Genera el dialplan para una queue.

        :param agente: Agente para la cual hay crear config sip
        :type agente: ominicontacto_app.models.AgenteProfile
        :returns: str -- config sip para los agentes
        """

        # assert agente is not None, "AgenteProfile == None"
        assert agente.user.get_full_name() is not None,\
            "agente.user.get_full_name() == None"
        assert agente.sip_extension is not None, "agente.sip_extension  == None"

        partes = []
        param_generales = {
            'oml_agente_sip': agente.sip_extension,
            'oml_agente_pk': agente.id
        }

        generador_agente = self._generador_sip_agente_factory. \
            crear_generador_para_agente_global(param_generales)
        partes.append(generador_agente.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_para_generar_config_sip(self):
        """Devuelve los agente para crear config de sip.
        """
        return AgenteProfile.objects.all()

    def _obtener_configuraciones_sip_agentes(self):
        configuraciones = []
        agentes = self._obtener_todas_para_generar_config_sip()
        for agente in agentes:
            logger.info("Creando config sip para agente %s", agente.user.
                        get_full_name())
            try:
                config_chunk = self._generar_config_agente(agente)
                logger.info("Config sip generado OK para agente %s",
                            agente.user.get_full_name())
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(agente.user.get_full_name()))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

                # FAILED: Creamos la porción para el fallo del config sip.
                param_failed = {'oml_queue_name': agente.user.get_full_name(),
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_sip_agente_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            configuraciones.append(config_chunk)
        return configuraciones

    def _generar_config_pausa(self, pausa):
        """Genera configuracion de pausa.

        :param pausa: Pausa
        :type agente: ominicontacto_app.models.Pausa
        :returns: str -- config sip para la pausa
        """
        assert pausa.nombre is not None, "pausa.nombre == None"
        param_generales = {
            'oml_pausa_nombre': pausa.nombre,
            'oml_pausa_pk': pausa.id
        }

        generador_pausa = self._generador_pausa_factory. \
            crear_generador_para_pausa_global(param_generales)
        return generador_pausa.generar_pedazo()

    def _obtener_configuraciones_pausas(self):
        configuraciones = []
        pausas = Pausa.objects.all()
        for pausa in pausas:

            logger.info("Creando config para pausa: %s", pausa.nombre)
            try:
                config_chunk = self._generar_config_pausa(pausa)
                logger.info("Config global generado OK para pausa %s", pausa.nombre)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(pausa.nombre))
                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

                # FAILED: Creamos la porción para el fallo del config de pausa.
                param_failed = {'oml_queue_name': pausa.nombre,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_pausa_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            configuraciones.append(config_chunk)
        return configuraciones

    def create_config_global(self):
        """Crea el archivo de configuración global para Asterisk.
        """

        # se adiciona la información del format serán generadas las grabaciones de las llamadas
        monitor_format_line = "\nMONITORFORMAT = {0}\n".format(settings.MONITORFORMAT)
        configuracion = [monitor_format_line]

        configs_sip_agentes = self._obtener_configuraciones_sip_agentes()
        configuracion += configs_sip_agentes
        configs_pausas = self._obtener_configuraciones_pausas()
        configuracion += configs_pausas

        self._globals_config_file.write(configuracion)


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
        return RutaSaliente.objects.all()

    def _obtener_todas_menos_una_ruta_para_generar_config_rutas(self, ruta):
        """Devuelve las rutas salientes para config rutas menos la ruta pasada por parametro
        """
        return RutaSaliente.objects.exclude(pk=ruta.id)

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
        rutas_file.append("same => n,Set(__DIALSTATUS=NONDIALPLANMATCH)\n")
        rutas_file.append("same => n,Gosub(sub-oml-hangup,s,1(FAIL FAIL FAIL no hay ruta para ${OMLOUTNUM})\n")

        # agrego las rutas con los patrones de discado
        for ruta in rutas:
            logger.info("Creando config sip para ruta saliente %s", ruta.id)
            rutas_file.append("\n[oml-outr-{0}]\n".format(ruta.id))
            rutas_file.append("include => oml-outr-{0}-custom".format(ruta.id))
            try:
                config_chunk = self._generar_config(ruta)
                logger.info("Config generado OK para ruta saliente %s", ruta.id)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la ruta {0}".format(ruta.id))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

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
        self._sip_trunks_config_file = SipTrunksConfigFile()

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
            logger.info("Creando config troncal sip %s", trunk.id)
            trunk_file.append("\n{0}\n".format(trunk.text_config.replace("\r", "")))
        self._sip_trunks_config_file.write(trunk_file)


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
            logger.info("Creando config troncal sip %s", trunk.id)
            trunk_file.append("{0}\n".format(trunk.register_string))

        self._sip_registrations_config_file.write(trunk_file)


class AsteriskConfigReloader(object):

    def reload_config(self):
        """Realiza reload de configuracion de Asterisk

        :returns: int -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.mkstemp()
        stderr_file = tempfile.mkstemp()

        try:
            subprocess.check_call(settings.OML_RELOAD_CMD,
                                  stdout=stdout_file, stderr=stderr_file)
            logger.info("Reload de configuracion de Asterisk fue OK")
            return 0
        except subprocess.CalledProcessError, e:
            logger.warn("Exit status erroneo: %s", e.returncode)
            logger.warn(" - Comando ejecutado: %s", e.cmd)
            try:
                stdout_file.seek(0)
                stderr_file.seek(0)
                stdout = stdout_file.read().splitlines()
                for line in stdout:
                    if line:
                        logger.warn(" STDOUT> %s", line)
                stderr = stderr_file.read().splitlines()
                for line in stderr:
                    if line:
                        logger.warn(" STDERR> %s", line)
            except:
                logger.exception("Error al intentar reporter STDERR y STDOUT")

            return e.returncode

        finally:
            stdout_file.close()
            stderr_file.close()

    def reload_asterisk(self):
        subprocess.call(['ssh', settings.OML_ASTERISK_HOSTNAME, '/usr/sbin/asterisk', '-rx',
                         '\'core reload\''])


class ConfigFile(object):
    def __init__(self, filename, hostname, remote_path):
        self._filename = filename
        self._hostname = hostname
        self._remote_path = remote_path

    def write(self, contenidos):
        tmp_fd, tmp_filename = tempfile.mkstemp()
        try:
            tmp_file_obj = os.fdopen(tmp_fd, 'w')
            for contenido in contenidos:
                assert isinstance(contenido, unicode), \
                    "Objeto NO es unicode: {0}".format(type(contenido))
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

    def copy_asterisk(self):
        subprocess.call(['scp', self._filename, ':'.join([self._hostname,
                                                          self._remote_path])])


class SipConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_SIP_FILENAME.strip()
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(SipConfigFile, self).__init__(filename, hostname, remote_path)


class QueuesConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_QUEUES_FILENAME.strip()
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(QueuesConfigFile, self).__init__(filename, hostname, remote_path)


class RutasSalientesConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_RUTAS_SALIENTES_FILENAME.strip()
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(RutasSalientesConfigFile, self).__init__(filename, hostname, remote_path)


class SipTrunksConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_ASTERISK_REMOTEPATH,
                                "oml_sip_trunks.conf")
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(SipTrunksConfigFile, self).__init__(filename, hostname, remote_path)


class SipRegistrationsConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_ASTERISK_REMOTEPATH,
                                "oml_sip_registrations.conf")
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(SipRegistrationsConfigFile, self).__init__(filename, hostname, remote_path)


class BackListConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "oml_backlist.txt")
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_BACKLIST_REMOTEPATH
        super(BackListConfigFile, self).__init__(filename, hostname, remote_path)


class GlobalsConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_GLOBALS_VARIABLES_FILENAME.strip()
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(GlobalsConfigFile, self).__init__(filename, hostname, remote_path)


class AudioConfigFile(object):
    def __init__(self, filename):
        self._filename = os.path.join(settings.MEDIA_ROOT, filename)
        self._hostname = settings.OML_ASTERISK_HOSTNAME
        self._remote_path = settings.OML_AUDIO_PATH_ASTERISK

    def copy_asterisk(self):
        subprocess.call(['scp', self._filename, ':'.join([self._hostname,
                                                          self._remote_path])])
