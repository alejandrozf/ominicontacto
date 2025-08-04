# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import os
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Agrupa las tareas de cron con frecuencia 1m en un solo proceso Django"

    def handle(self, *args, **options):
        logger.info("Iniciando cron_tick_1")
        for cmd in [
            'actualizar_reportes_llamadas_entrantes',
            'actualizar_reportes_llamadas_salientes',
            'actualizar_reportes_llamadas_dialers',
            'actualizar_reporte_dia_actual_agentes',
        ]:
            try:
                call_command(cmd)
            except Exception:
                logger.exception(f"Fallo al ejecutar {cmd}")
        if os.getenv('WALLBOARD_VERSION'):
            try:
                call_command('calcular_datos_wallboards')
            except Exception:
                logger.exception("Fallo al ejecutar calcular_datos_wallboards")
        logger.info("cron_tick_1 completado")
