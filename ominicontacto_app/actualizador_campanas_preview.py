# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import logging

from ominicontacto_app.models import AgenteEnContacto

logger = logging.getLogger(__name__)


def actualizar_relacion_agente_contacto(campana_id):
    """
    Procedimiento que libera un contacto asignado a un agente en una campaña
    preview al sobrepasar el tiempo máximo definido para atenderlo.
    El contacto podrá ser asignado a un nuevo agente para la finalización de
    su gestión
    """
    logger.info(
        "Actualizando asignaciones de contactos a agentes en campaña {0}".format(campana_id))
    AgenteEnContacto.objects.filter(
        campana_id=campana_id, estado=AgenteEnContacto.ESTADO_ENTREGADO).update(
            agente_id=-1, estado=AgenteEnContacto.ESTADO_INICIAL)


if __name__ == "__main__":
    actualizar_relacion_agente_contacto(sys.argv[1])
