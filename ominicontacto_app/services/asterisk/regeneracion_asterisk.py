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
Servicio de regenarción de archivos de asterisk y reload del mismo
"""

from __future__ import unicode_literals
from configuracion_telefonia_app.models import MusicaDeEspera, Playlist
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTelefonicaEnAsterisk)
from ominicontacto_app.services.asterisk.redis_database import RegenerarAsteriskFamilysOML
from ominicontacto_app.services.redis.redis_streams import RedisStreams

import getpass
import logging
import os
import sys

from crontab import CronTab

from django.conf import settings
from django.utils.translation import gettext as _

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import AsteriskConfigReloader, AudioConfigFile, \
    PlaylistsConfigCreator, QueuesCreator, SipConfigCreator
from configuracion_telefonia_app.models import AudiosAsteriskConf
import requests
import tempfile
import base64
from pathlib import Path
import json

logger = logging.getLogger(__name__)

flock_template = 'flock -n /tmp/{}.lock'


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class RegeneracionAsteriskService(object):

    def __init__(self):
        # Sincroniza Queues de Campañas
        self.queues_config_creator = QueuesCreator()
        # Sincroniza Sip De Agentes
        self.sip_config_creator = SipConfigCreator()
        # Sincroniza Modelos de Configuracion Telefonica
        self.sincronizador_config_telefonica = SincronizadorDeConfiguracionTelefonicaEnAsterisk()
        # Sincroniza en AstDB las que faltan en el Sincronizador de Configuracion Telefonica
        self.asterisk_database = RegenerarAsteriskFamilysOML()
        self.playlist_config_creator = PlaylistsConfigCreator()

        # Llama al comando que reinicia Asterisk
        self.reload_asterisk_config = AsteriskConfigReloader()

        # parámetros de script que desloguea agentes inactivos
        self.tareas_programadas_ids = [
            'asterisk_logout_script',
            'queue_log_clean_job',
            'actualizar_reportes_de_entrantes_job',
            'actualizar_reporte_supervisores',
            'actualizar_reporte_dia_actual_agentes',
            'actualizar_reportes_salientes',
            'actualizar_reportes_dialers']

        self.TIEMPO_CHEQUEO_CONTACTOS_INACTIVOS = 2
        self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_ENTRANTES = 1
        self.TIEMPO_ACTUALIZAR_REPORTE_SUPERVISORES = 5
        self.TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES = 1
        self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_SALIENTES = 1
        self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_DIALERS = 1

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.queues_config_creator.create_dialplan()
        except Exception:
            logger.exception(_("ActivacionQueueService: error al "
                               "intentar queues_config_creator()"))

            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion del queues de Asterisk. ")

        try:
            self.sip_config_creator.create_config_sip()
        except Exception:
            logger.exception(_("ActivacionAgenteService: error al "
                               "intentar create_config_sip()"))

            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion del config sip de Asterisk. ")

        try:
            self.playlist_config_creator.create_config_asterisk()
        except Exception:
            logger.exception(_("PlaylistsConfigCreator: error al "
                               "intentar create_config_sip()"))

            proceso_ok = False
            mensaje_error += _("Hubo un inconveniente al crear el archivo de "
                               "configuracion Playlists (MOH) en Asterisk. ")

        if not proceso_ok:
            raise(RestablecerDialplanError(mensaje_error))
        else:
            self.sincronizador_config_telefonica.sincronizar_en_asterisk()
            self.asterisk_database.regenerar_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def _generar_tarea_script_logout_agentes_inactivos(self):
        """Adiciona una tarea programada que llama al script de que desloguea
        agentes inactivos
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[0])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(settings.INSTALL_PREFIX,
                                          'ominicontacto/manage.py logout_unavailable_agents')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[0])
        crontab.remove_all(comment=self.tareas_programadas_ids[0])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script_logout),
                comment=self.tareas_programadas_ids[0])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_CHEQUEO_CONTACTOS_INACTIVOS)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_limpieza_diaria_queuelog(self):
        """Adiciona una tarea programada para limpiar la tabla queue_log
        diariamente
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_psql = os.popen('which psql').read()[:-1]
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[1])
        crontab.remove_all(comment=self.tareas_programadas_ids[1])
        if list(job) == []:
            postgres_user = settings.POSTGRES_USER
            postgres_host = settings.POSTGRES_HOST
            postgres_database = settings.POSTGRES_DATABASE
            postgres_password = 'PGPASSWORD={0}'.format(os.getenv('PGPASSWORD'))
            job = crontab.new(
                command='{0} {1} -U {2} -h {3} -d {4} -c \'DELETE FROM queue_log\''.format(
                    postgres_password, ruta_psql, postgres_user, postgres_host,
                    postgres_database),
                comment=self.tareas_programadas_ids[1])
            # adicionar tiempo de periodicidad al cron job
            job.hour.on(2)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_script_actualizar_reportes_llamadas_entrantes(self):
        """Adiciona una tarea programada que llama al script de que calcula reportes de llamadas
        entrantes
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[2])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reportes_llamadas_entrantes')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[2])
        crontab.remove_all(comment=self.tareas_programadas_ids[2])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script_logout),
                comment=self.tareas_programadas_ids[2])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_ENTRANTES)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_script_actualizar_reporte_datos_supervisores(self):
        """Adiciona una tarea programada que llama al script de que calcula el reportes
        los agentes y campanas asociados a cada supervisor
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[3])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reporte_supervisores')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[3])
        crontab.remove_all(comment=self.tareas_programadas_ids[3])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script),
                comment=self.tareas_programadas_ids[3])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTE_SUPERVISORES)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_script_actualizar_reporte_agentes_dia_actual(self):
        """Adiciona una tarea programada que llama al script de que calcula el reportes
        los agentes y campanas asociados a cada supervisor
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[4])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reporte_dia_actual_agentes')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[4])
        crontab.remove_all(comment=self.tareas_programadas_ids[4])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script),
                comment=self.tareas_programadas_ids[4])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_script_actualizar_reportes_llamadas_salientes(self):
        """Adiciona una tarea programada que llama al script de que calcula reportes de llamadas
        salientes
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[5])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reportes_llamadas_salientes')

        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[5])
        crontab.remove_all(comment=self.tareas_programadas_ids[5])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script_logout),
                comment=self.tareas_programadas_ids[5])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_SALIENTES)
            crontab.write_to_user(user=getpass.getuser())

    def _generar_tarea_script_actualizar_reportes_llamadas_dialers(self):
        """Adiciona una tarea programada que llama al script de que calcula reportes de llamadas
        dialers
        """
        # conectar con cron
        crontab = CronTab(user=getpass.getuser())
        ruta_source_envars = 'source /etc/profile.d/omnileads_envars.sh;'
        flock = flock_template.format(self.tareas_programadas_ids[6])
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reportes_llamadas_dialers')

        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[6])
        crontab.remove_all(comment=self.tareas_programadas_ids[6])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2} {3}'.format(
                    ruta_source_envars, flock, ruta_python_virtualenv, ruta_script_logout),
                comment=self.tareas_programadas_ids[6])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_DIALERS)
            crontab.write_to_user(user=getpass.getuser())

    def _reenviar_archivos_playlist_asterisk(self):
        playlists = Playlist.objects.all()
        for playlist in playlists:
            musica_espera_list = MusicaDeEspera.objects.filter(playlist=playlist.pk)
            print(list(musica_espera_list))
            for musica in musica_espera_list:
                audio_file_asterisk = AudioConfigFile(musica)
                audio_file_asterisk.copy_asterisk()

    def _reenviar_paquetes_idioma(self):
        ASTERISK_SOUNDS_URL = 'https://downloads.asterisk.org/pub/telephony/sounds/'
        audios_asterisk_conf_list = AudiosAsteriskConf.objects.filter(esta_instalado=True)
        print("Descargando paquete de idiomas instalados....")
        for audio_conf in audios_asterisk_conf_list:
            language = audio_conf.paquete_idioma
            filename = 'asterisk-core-sounds-{0}-wav-current.tar.gz'.format(language)
            url = ASTERISK_SOUNDS_URL + filename
            response = requests.get(url, stream=True)
            filename_full_path = os.path.join(tempfile.gettempdir(), filename)
            handle = open(filename_full_path, "wb")
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    handle.write(chunk)
            handle.close()

            print(f'   {language}...')
            __, nombre_archivo = os.path.split(filename_full_path)
            sound_tar_data = Path(filename_full_path).read_bytes()
            res = base64.b64encode(sound_tar_data)
            res = res.decode('utf-8')
            redis_stream = RedisStreams()
            content = {
                'archivo': nombre_archivo,
                'type': 'ASTERISK_SOUNDS',
                'action': 'COPY',
                'language': language,
                'content': res
            }
            redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))
        print('Completada descarga de paquetes de idioma')

    def regenerar(self):
        self._generar_y_recargar_configuracion_asterisk()
        self._reenviar_archivos_playlist_asterisk()
        self._reenviar_paquetes_idioma()
        self._generar_tarea_script_logout_agentes_inactivos()
        self._generar_tarea_limpieza_diaria_queuelog()
        self._generar_tarea_script_actualizar_reportes_llamadas_entrantes()
        self._generar_tarea_script_actualizar_reportes_llamadas_salientes()
        self._generar_tarea_script_actualizar_reportes_llamadas_dialers()
        self._generar_tarea_script_actualizar_reporte_datos_supervisores()
        self._generar_tarea_script_actualizar_reporte_agentes_dia_actual()
