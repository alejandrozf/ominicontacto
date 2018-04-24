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
import logging as _logging
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeQueueFactory, GeneradorDePedazoDeAgenteFactory,
    GeneradorDePedazoDeCampanaDialerFactory,
    GeneradorDePedazoDePausaFactory,
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
            'oml_queue_name': "{0}_{1}".format(campana.id,
                                               elimina_espacios(campana.nombre)),
            'oml_queue_type': campana.type,
            'oml_queue_id_asterisk': campana.get_string_queue_asterisk(),
            'oml_queue_wait': campana.queue_campana.wait,
            'oml_campana_id': campana.id,
            'date': str(datetime.datetime.now())
        }

        # QUEUE: Creamos la porción inicial del Queue.
        filepath = 'silence/1'
        if campana.queue_campana.audio_de_ingreso:
            local_filepath = campana.queue_campana.audio_de_ingreso.audio_asterisk.path
            filename = os.path.splitext(os.path.basename(local_filepath))[0]
            filepath = os.path.join('oml', filename)
        param_generales['filepath_audio_ingreso'] = filepath

        sub_partes = []
        param_generales['parametros_extra'] = ''
        # Generador para lineas de Parametros Extra para Webform
        if campana.parametros_extra_para_webform.count() > 0:
            for parametro in campana.parametros_extra_para_webform.all():
                generador_queue = self._generador_dialer_factory. \
                    crear_generador_para_parametro_extra_para_webform({
                        'parametro': parametro.parametro,
                        'columna': parametro.columna})
                sub_partes.append(generador_queue.generar_pedazo())
        param_generales['parametros_extra'] = ''.join(sub_partes)

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
            'oml_queue_name': "{0}_{1}".format(campana.id,
                                               elimina_espacios(campana.nombre)),
            'oml_queue_type': campana.type,
            'oml_queue_id_asterisk': campana.get_string_queue_asterisk(),
            'date': str(datetime.datetime.now()),
        }

        # Generador inicial para campana dialer
        generador_queue = self._generador_dialer_factory. \
            crear_generador_para_campana_dialer_start(param_generales)
        partes.append(generador_queue.generar_pedazo())

        # Generador para lineas de Parametros Extra para Webform
        if campana.parametros_extra_para_webform.count() > 0:
            for parametro in campana.parametros_extra_para_webform.all():
                generador_queue = self._generador_dialer_factory. \
                    crear_generador_para_parametro_extra_para_webform({
                        'parametro': parametro.parametro,
                        'columna': parametro.columna})
                partes.append(generador_queue.generar_pedazo())

        # Generador para grabacion
        if campana.queue_campana.auto_grabacion:
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_grabacion(param_generales)
            partes.append(generador_queue.generar_pedazo())

        # Generador para contestadores
        if campana.queue_campana.detectar_contestadores:
            generador_queue = self._generador_dialer_factory. \
                crear_generador_para_campana_dialer_contestadores(param_generales)
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
            if campana.queue_campana.audio_para_contestadores:
                filepath = campana.queue_campana.audio_para_contestadores.audio_asterisk.path
                filename = os.path.splitext(os.path.basename(filepath))[0]
                param_generales['filename_audio_contestadores'] = filename
                generador_queue = self._generador_dialer_factory. \
                    crear_generador_para_campana_dialer_contestadores_end_con_audio(param_generales)
            else:
                generador_queue = self._generador_dialer_factory. \
                    crear_generador_para_campana_dialer_contestadores_end(param_generales)
            partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_entrante_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        return Campana.objects.obtener_all_dialplan_asterisk().filter(
            type=Campana.TYPE_ENTRANTE)

    def _obtener_todas_dialer_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        return Campana.objects.obtener_all_dialplan_asterisk().filter(type=Campana.TYPE_DIALER)

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
                "oml/", audio_name[0])
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
