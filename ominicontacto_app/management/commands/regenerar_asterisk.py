# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand, CommandError

from ominicontacto_app.services.regeneracion_asterisk import RegeneracionAsteriskService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Se regeneran los archivos de configuracion para Asterisk
    """

    help = u"Se regeneran los archivos de configuracion para Asterisk"

    def _regenerar_asterisk(self):
        regenerar_service = RegeneracionAsteriskService()
        regenerar_service.regenerar()

    def handle(self, *args, **options):
        try:
            self._regenerar_asterisk()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e.message))
            raise CommandError('Fallo del comando: {0}'.format(e.message))
