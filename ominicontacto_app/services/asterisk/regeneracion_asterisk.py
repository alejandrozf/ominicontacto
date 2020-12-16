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

import getpass
import logging
import os
import sys

from crontab import CronTab

from django.conf import settings
from django.utils.translation import ugettext as _

from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader, QueuesCreator, SipConfigCreator, PlaylistsConfigCreator
)
from ominicontacto_app.services.asterisk.redis_database import RegenerarAsteriskFamilysOML
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTelefonicaEnAsterisk)

logger = logging.getLogger(__name__)


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
            'actualizar_reporte_dia_actual_agentes']
        self.TIEMPO_CHEQUEO_CONTACTOS_INACTIVOS = 2
        self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_ENTRANTES = 1
        self.TIEMPO_ACTUALIZAR_REPORTE_SUPERVISORES = 5
        self.TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES = 1

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
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(settings.INSTALL_PREFIX,
                                          'ominicontacto/manage.py logout_unavailable_agents')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[0])
        crontab.remove_all(comment=self.tareas_programadas_ids[0])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2}'.format(
                    ruta_source_envars, ruta_python_virtualenv, ruta_script_logout),
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
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script_logout = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reportes_llamadas_entrantes')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[2])
        crontab.remove_all(comment=self.tareas_programadas_ids[2])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2}'.format(
                    ruta_source_envars, ruta_python_virtualenv, ruta_script_logout),
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
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reporte_supervisores')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[3])
        crontab.remove_all(comment=self.tareas_programadas_ids[3])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2}'.format(
                    ruta_source_envars, ruta_python_virtualenv, ruta_script),
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
        ruta_python_virtualenv = os.path.join(sys.prefix, 'bin/python3')
        ruta_script = os.path.join(
            settings.INSTALL_PREFIX,
            'ominicontacto/manage.py actualizar_reporte_dia_actual_agentes')
        # adicionar nuevo cron job para esta tarea si no existe anteriormente
        job = crontab.find_comment(self.tareas_programadas_ids[4])
        crontab.remove_all(comment=self.tareas_programadas_ids[4])
        if list(job) == []:
            job = crontab.new(
                command='{0} {1} {2}'.format(
                    ruta_source_envars, ruta_python_virtualenv, ruta_script),
                comment=self.tareas_programadas_ids[4])
            # adicionar tiempo de periodicidad al cron job
            job.minute.every(self.TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES)
            crontab.write_to_user(user=getpass.getuser())

    def regenerar(self):
        self._generar_y_recargar_configuracion_asterisk()
        self._generar_tarea_script_logout_agentes_inactivos()
        self._generar_tarea_limpieza_diaria_queuelog()
        self._generar_tarea_script_actualizar_reportes_llamadas_entrantes()
        self._generar_tarea_script_actualizar_reporte_datos_supervisores()
        self._generar_tarea_script_actualizar_reporte_agentes_dia_actual()
