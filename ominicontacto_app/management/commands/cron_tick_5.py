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

import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Agrupa las tareas cada 5 minutos: supervisores y campañas preview"

    def handle(self, *args, **options):
        logger.info("Iniciando cron_5")
        # Lista de comandos a ejecutar cada 5 minutos
        for cmd in [
            'actualizar_reporte_supervisores',
            'actualizar_campanas_preview',
        ]:
            try:
                call_command(cmd)
                logger.info(f"Ejecutado con éxito: {cmd}")
            except Exception:
                logger.exception(f"Fallo al ejecutar {cmd}")
        logger.info("cron_5 completado")
