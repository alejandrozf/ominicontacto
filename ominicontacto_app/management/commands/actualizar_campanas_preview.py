# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand
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
        parser.add_argument('campana_id', nargs=1, type=int)

    def _actualizar_relacion_agente_contacto(self, campana_id):
        """
        Procedimiento que libera un contacto asignado a un agente en una campaña
        preview al sobrepasar el tiempo máximo definido para atenderlo.
        El contacto podrá ser asignado a un nuevo agente para la finalización de
        su gestión
        """
        AgenteEnContacto.objects.filter(
            campana_id=campana_id, estado=AgenteEnContacto.ESTADO_ENTREGADO).update(
                agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)

    def handle(self, *args, **options):
        campana_id = options['campana_id'][0]
        try:
            self._actualizar_relacion_agente_contacto(campana_id)
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
        else:
            logging.info(
                "Actualizando asignaciones de contactos a agentes en campaña {0}".format(
                    campana_id))
