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
