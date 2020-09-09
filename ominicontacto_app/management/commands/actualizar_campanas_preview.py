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
from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from ominicontacto_app.models import AgenteEnContacto

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Libera los contactos asignados a agentes en campañas
    preview al sobrepasar el tiempo máximo definido para atenderlo.
    El contacto podrá ser asignado a un nuevo agente para la finalización de
    su gestión
    """

    help = 'Actualiza relaciones de agentes con contactos'

    def _actualizar_relaciones_agente_contacto(self):
        """
        Procedimiento que libera los contactos reservados y asignados a los agentes de las campañas
        preview al sobrepasar el tiempo máximo definido para atenderlo.
        Los contactos liberados podrán ser asignados a nuevos agentes para la finalización de
        su gestión
        """
        liberados = AgenteEnContacto.liberar_contactos_por_tiempo()

        logger.info(
            _("Actualizando {0} asignaciones de contactos a agentes en campañas preview".format(
                liberados)))

    def handle(self, *args, **options):
        try:
            self._actualizar_relaciones_agente_contacto()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
