# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions
#
# This file is part of OMniLeads
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
"""
Servicio de regeneración de tareas programadas (cron jobs)
para OMniLeads/Asterisk. Refactorizado para agrupar invocaciones cada minuto.
"""
import logging
import os
import sys
import getpass

from crontab import CronTab
from django.conf import settings

logger = logging.getLogger(__name__)
# Template para usar flock y prevenir ejecuciones simultáneas
flock_template = 'flock -n /tmp/{}.lock'


class RegeneracionCronosService:
    """
    Servicio para crear o actualizar las tareas cron necesarias
    para funcionamiento de OMniLeads/Asterisk.
    Agrupa las tareas de frecuencia 1m y 5m en un solo comando 
    `cron_tick_1`& `cron_tick_5`.
    """
    tareas_programadas_ids = [
        'cron_tick_1',
        'cron_tick_5',
        'reiniciar_estadisticas_calldata',
    ]

    def __init__(self):
        self.user = getpass.getuser()
        self.cron = CronTab(user=self.user)

    def _add_job(self, id_tarea, script_name, schedule_fn):
        """Helper para añadir o actualizar un job cron."""
        flock = flock_template.format(id_tarea)
        manage_py = os.path.join(settings.INSTALL_PREFIX, 'ominicontacto', 'manage.py')
        cmd = f"{flock} {sys.executable} {manage_py} {script_name}"

        # Remueve previas con ese comentario
        self.cron.remove_all(comment=id_tarea)
        job = self.cron.new(command=cmd, comment=id_tarea)
        schedule_fn(job)
        logger.debug(f"Cron job '{id_tarea}' programado: {cmd}")

    def regenerar_cronos(self):
        """
        Crea o actualiza los cron jobs:
        - `cron_tick_1` cada minuto (agrupa 5 tareas)
        - `cron_tick_5` cada 5 minuto (agrupa 2 tareas)
        - reinicio diario a medianoche
        """
        # Agrupar tareas 1m  (supervision) en un solo comando
        self._add_job(
            'cron_tick_1',
            'cron_tick_1',
            lambda job: job.minute.every(1)
        )
        # Reporte supervisores & preview contactos cada 5 minutos
        self._add_job(
            'cron_tick_5',
            'cron_tick_5',
            lambda job: job.minute.every(5)
        )
        # Reiniciar estadísticas calldata a medianoche
        self._add_job(
            'reiniciar_estadisticas_calldata',
            'reiniciar_estadisticas_calldata',
            lambda job: (job.hour.on(0), job.minute.on(0))
        )
        # Escribe cambios en el crontab una sola vez
        self.cron.write_to_user(user=self.user)