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

import logging

from django.core.management.base import BaseCommand

from ominicontacto_app.models import Campana

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Reescribe los archivos de tareas de cron para cada campaña preview activa en el sistema
    Esto es util para casos donde se hayan eliminado accidentalmente algunas de estas tareas
    """

    def _regenerar_tareas_campanas_preview_activas(self):
        campanas_preview_activas = Campana.objects.obtener_campanas_preview().filter(
            estado=Campana.ESTADO_ACTIVA)
        for campana in campanas_preview_activas:
            campana.crear_tarea_actualizacion()

    def handle(self, *args, **options):
        try:
            self._regenerar_tareas_campanas_preview_activas()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e))
