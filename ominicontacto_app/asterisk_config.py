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

from ominicontacto_app.models import Queue
import logging as _logging
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeQueueFactory)


logger = _logging.getLogger(__name__)


class QueueDialplanConfigCreator(object):

    def __init__(self):
        self._dialplan_config_file = QueueConfigFile()
        self._generador_factory = GeneradorDePedazoDeQueueFactory()

    def _generar_dialplan(self, queue):
        """Genera el dialplan para una queue.

        :param queue: Queue para la cual hay crear el dialplan
        :type queue: ominicontacto_app.models.Queue
        :returns: str -- dialplan para la queue
        """

        assert queue is not None, "Queue == None"
        assert queue.name is not None, "queue.name == None"

        partes = []
        param_generales = {
            'oml_queue_name': queue.name,
            'oml_queue_id_asterisk': '0077' + str(queue.queue_asterisk),
            'oml_queue_wait': queue.wait,
            'date': str(datetime.datetime.now())
        }

        # QUEUE: Creamos la porción inicial del Queue.
        generador_queue = self._generador_factory.crear_generador_para_queue(
            param_generales)
        partes.append(generador_queue.generar_pedazo())

        return ''.join(partes)

    def _obtener_todas_para_generar_dialplan(self):
        """Devuelve las queues para crear el dialplan.
        """
        # Ver de obtener activa ya que en este momemento no estamos manejando
        # estados
        # Queue.objects.obtener_todas_para_generar_dialplan()
        return Queue.objects.all()

    def create_dialplan(self, queue=None, queues=None):
        """Crea el archivo de dialplan para queue existentes
        (si `queue` es None). Si `queue` es pasada por parametro,
        se genera solo para dicha queue.
        """

        if queues:
            pass
        elif queue:
            queues = [queue]
        else:
            queues = self._obtener_todas_para_generar_dialplan()
        dialplan = []
        for queue in queues:
            logger.info("Creando dialplan para queue %s", queue.name)
            try:
                config_chunk = self._generar_dialplan(queue)
                logger.info("Dialplan generado OK para queue %s",
                            queue.name)
            except:
                logger.exception(
                    "No se pudo generar configuracion de "
                    "Asterisk para la quene {0}".format(queue.name))

                try:
                    traceback_lines = [
                        "; {0}".format(line)
                        for line in traceback.format_exc().splitlines()]
                    traceback_lines = "\n".join(traceback_lines)
                except:
                    traceback_lines = "Error al intentar generar traceback"
                    logger.exception("Error al intentar generar traceback")

                # FAILED: Creamos la porción para el fallo del Dialplan.
                param_failed = {'oml_queue_name': queue.name,
                                'date': str(datetime.datetime.now()),
                                'traceback_lines': traceback_lines}
                generador_failed = \
                    self._generador_factory.crear_generador_para_failed(
                        param_failed)
                config_chunk = generador_failed.generar_pedazo()

            dialplan.append(config_chunk)

        self._dialplan_config_file.write(dialplan)


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
        hostname = settings.OML_QUEUE_HOSTNAME
        remote_path = settings.OML_QUEUE_REMOTEPATH
        super(QueueConfigFile, self).__init__(filename, hostname, remote_path)
