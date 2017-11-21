# -*- coding: utf-8 -*-

import logging

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ominicontacto_app.tests.factories import AgenteEnContacto

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
        AgenteEnContacto.objects.filter(
            campana_id=campana_id, estado=AgenteEnContacto.ESTADO_ENTREGADO,
            modificado__lte=tiempo_actual - delta_tiempo_desconexion).update(
                agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)

    def handle(self, *args, **options):
        campana_id = args[0]
        tiempo_desconexion = args[1]
        try:
            self._actualizar_relacion_agente_contacto(campana_id, tiempo_desconexion)
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
        else:
            logging.info(
                "Actualizando asignaciones de contactos a agentes en campaña {0}".format(
                    campana_id))
