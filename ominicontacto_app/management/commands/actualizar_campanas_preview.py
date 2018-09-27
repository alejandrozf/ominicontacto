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

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ominicontacto_app.models import AgenteEnContacto

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Libera un contacto asignado a un agente en una campaña
    preview al sobrepasar el tiempo máximo definido para atenderlo.
    El contacto podrá ser asignado a un nuevo agente para la finalización de
    su gestión
    """

    help = u'Actualiza relaciones de agentes con contactos'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs=2, type=int)

    def _actualizar_relacion_agente_contacto(self, campana_id, tiempo_desconexion):
        """
        Procedimiento que libera un contacto asignado a un agente en una campaña
        preview al sobrepasar el tiempo máximo definido para atenderlo.
        El contacto podrá ser asignado a un nuevo agente para la finalización de
        su gestión
        """
        tiempo_actual = timezone.now()
        delta_tiempo_desconexion = timedelta(minutes=tiempo_desconexion)
        qs_agentes_demorados = AgenteEnContacto.objects.filter(
            campana_id=campana_id, estado=AgenteEnContacto.ESTADO_ENTREGADO,
            modificado__lte=tiempo_actual - delta_tiempo_desconexion)
        logging.info(
            "Actualizando {0} asignaciones de contactos a agentes en campaña {1}".format(
                qs_agentes_demorados.count(), campana_id))
        qs_agentes_demorados.update(agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)

    def handle(self, *args, **options):
        campana_id = args[0]
        tiempo_desconexion = args[1]
        try:
            self._actualizar_relacion_agente_contacto(campana_id, tiempo_desconexion)
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
