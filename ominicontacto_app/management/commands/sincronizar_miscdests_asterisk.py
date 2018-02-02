# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from ominicontacto_app.services.asterisk_service import AsteriskService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Sincroniza la tabla 'miscdests' de la base de datos de Asterisk.
    Esta tabla tiene informacion de las Queues de Campañas Entrantes no eliminadas.
    """

    help = u"Actualiza la tabla 'miscdests' de la base de datos de Asterisk"

    def _sincronizar_informacion_de_colas(self):
        asterisk_service = AsteriskService()
        asterisk_service.sincronizar_informacion_de_colas()

    def handle(self, *args, **options):
        try:
            self._sincronizar_informacion_de_colas()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
