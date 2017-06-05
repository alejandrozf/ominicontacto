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
from ominicontacto_app.utiles import elimina_espacios
from ominicontacto_app.models import (
    AgenteProfile, SupervisorProfile, Campana
)
import logging as _logging
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeQueueFactory, GeneradorDePedazoDeAgenteFactory,
    GeneradorDePedazoDeCampanaDialerFactory
)


logger = _logging.getLogger(__name__)


class QueueDialplanConfigCreator(object):

    def __init__(self):
        self._dialplan_config_file = QueueConfigFile()
        self._generador_factory = GeneradorDePedazoDeQueueFactory()
        self._generador_dialer_factory = GeneradorDePedazoDeCampanaDialerFactory()

    def _generar_dialplan(self, campana):
        """Genera el dialplan para una queue.

        :param campana: Campana para la cual hay crear el dialplan
        :type campana: ominicontacto_app.models.Campana
        :returns: str -- dialplan para la queue
        """

        assert campana.queue_campana is not None, "campana.queue_campana == None"

        partes = []
        param_generales = {
            'oml_queue_name': elimina_espacios(campana.nombre),
            'oml_queue_id_asterisk': '0077' + str(campana.queue_campana.queue_asterisk),
            'oml_queue_wait': campana.queue_campana.wait,
            'oml_campana_id': campana.id,
            'date': str(datetime.datetime.now())
        }

        # QUEUE: Creamos la porción inicial del Queue.
        if campana.queue_campana.auto_grabacion:
            generador_queue = self._generador_factory.\
                crear_generador_para_queue_grabacion(param_generales)
            partes.append(generador_queue.generar_pedazo())
        else:
            generador_queue = self._generador_factory. \
                crear_generador_para_queue_sin_grabacion(param_generales)
            partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _generar_dialplan_campana_dialer(self, campana):
        """Genera el dialplan para una queue.

        :param campana: Campana para la cual hay crear el dialplan
        :type campana: ominicontacto_app.models.Campana
        :returns: str -- dialplan para la queue
        """

        assert campana.queue_campana is not None, "campana.queue_campana == None"

        partes = []
        param_generales = {
            'oml_queue_name': elimina_espacios(campana.nombre),
            'oml_queue_id_asterisk': '0077' + str(campana.queue_campana.queue_asterisk),
            'date': str(datetime.datetime.now())
        }

        # Generador inicial para campana dialer
        generador_queue = self._generador_dialer_factory.\
            crear_generador_para_campana_dialer_start(param_generales)
        partes.append(generador_queue.generar_pedazo())

        #Generador para contestadores
        if campana.queue_campana.detectar_contestadores:
            generador_queue = self._generador_dialer_factory. \
            crear_generador_para_campana_dialer_contestadores(param_generales)
            partes.append(generador_queue.generar_pedazo())

        # Generador para grabacion
        if campana.queue_campana.auto_grabacion:
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_grabacion(param_generales)
            partes.append(generador_queue.generar_pedazo())

        # generador de acuerdo al tipo de interacion
        if campana.tipo_interaccion is Campana.FORMULARIO:
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_formulario(param_generales)
            partes.append(generador_queue.generar_pedazo())
        elif campana.tipo_interaccion is Campana.SITIO_EXTERNO:
            param_generales.update({'oml_sitio_externo_url': campana.sitio_externo.url})
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_sitio_externo(param_generales)
            partes.append(generador_queue.generar_pedazo())

        # Generador para contestadores para end
        if campana.queue_campana.detectar_contestadores:
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_contestadores_end(param_generales)
            partes.append(generador_queue.generar_pedazo())
        return ''.join(partes)

    def _obtener_todas_entrante_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        # Queue.objects.obtener_todas_para_generar_dialplan()
        return Campana.objects.obtener_all_dialplan_asterisk().filter(
            type=Campana.TYPE_ENTRANTE)

    def _obtener_todas_dialer_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        # Queue.objects.obtener_todas_para_generar_dialplan()
        return Campana.objects.obtener_all_dialplan_asterisk().filter(
            type=Campana.TYPE_DIALER)

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
            campanas = self._obtener_todas_entrante_para_generar_dialplan()
        dialplan = []
        # agrego linea inicial que lleva [from-queue-fts] el archivo de asterisk
        dialplan.append("[from-queue-fts]")
        for campana in campanas:
            logger.info("Creando dialplan para queue %s", campana.nombre)
            try:
                config_chunk = self._generar_dialplan(campana)
                logger.info("Dialplan generado OK para queue %s",
                            campana.nombre)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la queue {0}".format(campana.nombre))

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

        campanas = self._obtener_todas_dialer_para_generar_dialplan()

        for campana in campanas:
            logger.info("Creando dialplan para queue %s", campana.nombre)
            try:
                config_chunk = self._generar_dialplan_campana_dialer(campana)
                logger.info("Dialplan generado OK para queue %s",
                            campana.nombre)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la queue {0}".format(campana.nombre))

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

        self._dialplan_config_file.write(dialplan)


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

        #assert agente is not None, "AgenteProfile == None"
        assert agente.user.get_full_name() is not None,\
            "agente.user.get_full_name() == None"
        assert agente.sip_extension is not None, "agente.sip_extension  == None"

        partes = []
        param_generales = {
            'oml_agente_name': agente.user.get_full_name(),
            'oml_agente_sip': agente.sip_extension,
            'oml_kamailio_ip': settings.OML_KAMAILIO_IP,
        }

        generador_agente= self._generador_factory.crear_generador_para_agente(
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
            'oml_queue_name': elimina_espacios(campana.nombre),
            'oml_strategy': campana.queue_campana.strategy,
            'oml_timeout': campana.queue_campana.wait,
            'oml_servicelevel': campana.queue_campana.servicelevel,
            'oml_weight': campana.queue_campana.weight,
            'oml_wrapuptime': campana.queue_campana.wrapuptime,
            'oml_maxlen': campana.queue_campana.maxlen,
            'oml_retry': retry
        }

        # QUEUE: Creamos la porción inicial del Queue.
        generador_queue = self._generador_factory.\
            crear_generador_para_queue(param_generales)
        partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        # Queue.objects.obtener_todas_para_generar_dialplan()
        return Campana.objects.obtener_all_dialplan_asterisk()

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

        self._queues_config_file.write(dialplan)


class AsteriskConfigReloader(object):

    def reload_config(self):
        """Realiza reload de configuracion de Asterisk

        :returns: int -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()

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
        subprocess.call(['ssh', settings.OML_ASTERISK_HOSTNAME, '/usr/sbin/asterisk', '-rx', '\'core reload\''])


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


class QueueConfigFile(ConfigFile):
    def __init__(self):
        filename = settings.OML_QUEUE_FILENAME.strip()
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_ASTERISK_REMOTEPATH
        super(QueueConfigFile, self).__init__(filename, hostname, remote_path)


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


class BackListConfigFile(ConfigFile):
    def __init__(self):
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                "oml_backlist.txt")
        hostname = settings.OML_ASTERISK_HOSTNAME
        remote_path = settings.OML_BACKLIST_REMOTEPATH
        super(BackListConfigFile, self).__init__(filename, hostname, remote_path)
