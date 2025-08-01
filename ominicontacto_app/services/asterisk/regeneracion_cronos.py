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
para OMniLeads/Asterisk. Refactorizado para evitar duplicación, corregir índices y mejorar robustez.
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
    """
    # Identificadores únicos para cada tarea cron (agregada preview)
    tareas_programadas_ids = [
        'actualizar_reportes_llamadas_entrantes',
        'actualizar_reportes_salientes',
        'actualizar_reportes_llamadas_dialers',
        'actualizar_reporte_supervisores',
        'actualizar_reporte_dia_actual_agentes',
        'actualizar_campanas_preview',
        'reiniciar_estadisticas_calldata',
        'calcular_datos_wallboards',
    ]

    # Intervalos de ejecución en minutos u horas
    TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_ENTRANTES = 1
    TIEMPO_ACTUALIZAR_REPORTE_SUPERVISORES = 5
    TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES = 1
    TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_SALIENTES = 1
    TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_DIALERS = 1
    TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_PREVIEW = 6
    TIEMPO_ACTUALIZAR_REPORTES_WALLBOARD = 1

    def __init__(self):
        self.user = getpass.getuser()
        self.cron = CronTab(user=self.user)

    def _add_job(self, id_tarea, script_name, schedule_fn):
        """Helper para añadir o actualizar un job cron."""
        flock = flock_template.format(id_tarea)
        manage_py = os.path.join(settings.INSTALL_PREFIX, 'ominicontacto', 'manage.py')
        command = f"{flock} {sys.executable} {manage_py} {script_name}"

        # Elimina previas con mismo comentario
        self.cron.remove_all(comment=id_tarea)
        # Añade nuevo job
        job = self.cron.new(command=command, comment=id_tarea)
        schedule_fn(job)
        logger.debug(f"Cron job '{id_tarea}' programado: {command}")

    def regenerar_cronos(self):
        """
        Ejecuta la creación/actualización de todas las tareas cron configuradas.
        Escribe cambios al final en un solo write.
        """
        try:
            # Llamadas entrantes
            self._add_job(
                self.tareas_programadas_ids[0],
                'actualizar_reportes_llamadas_entrantes',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_ENTRANTES)
            )
            # Llamadas salientes
            self._add_job(
                self.tareas_programadas_ids[1],
                'actualizar_reportes_llamadas_salientes',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_SALIENTES)
            )
            # Dialers
            self._add_job(
                self.tareas_programadas_ids[2],
                'actualizar_reportes_llamadas_dialers',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_DIALERS)
            )
            # Supervisores
            self._add_job(
                self.tareas_programadas_ids[3],
                'actualizar_reporte_supervisores',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTE_SUPERVISORES)
            )
            # Agentes día actual
            self._add_job(
                self.tareas_programadas_ids[4],
                'actualizar_reporte_dia_actual_agentes',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_DASHBOARD_AGENTES)
            )
            # Campañas preview
            self._add_job(
                self.tareas_programadas_ids[5],
                'actualizar_campanas_preview',
                lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_LLAMADAS_PREVIEW)
            )
            # Reiniciar estadísticas calldata a medianoche
            self._add_job(
                self.tareas_programadas_ids[6],
                'reiniciar_estadisticas_calldata',
                lambda job: (job.hour.on(0), job.minute.on(0))
            )
            # Wallboards (si está habilitado)
            if os.getenv('WALLBOARD_VERSION'):
                self._add_job(
                    self.tareas_programadas_ids[7],
                    'calcular_datos_wallboards',
                    lambda job: job.minute.every(self.TIEMPO_ACTUALIZAR_REPORTES_WALLBOARD)
                )
            # Escribir todos los cambios de una vez
            self.cron.write_to_user(user=self.user)
        except Exception as e:
            logger.error(f"Error al regenerar cron jobs: {e}")
