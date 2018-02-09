# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from ominicontacto_app.services.regeneracion_asterisk import RegeneracionAsteriskService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sincroniza la tabla 'miscdests' de la base de datos de Asterisk.
    Esta tabla tiene informacion de las Queues de Campañas Entrantes no eliminadas.
    """

    help = u"Actualiza la tabla 'miscdests' de la base de datos de Asterisk"

    def _regenerar_asterisk(self):
        regenerar_service = RegeneracionAsteriskService()
        regenerar_service.regenerar()

    def handle(self, *args, **options):
        try:
            self._regenerar_asterisk()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
