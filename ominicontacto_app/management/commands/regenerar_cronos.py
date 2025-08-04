# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions
#
# This file is part of OMniLeads
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import logging
from django.core.management.base import BaseCommand, CommandError
from ominicontacto_app.services.asterisk.regeneracion_cronos import RegeneracionCronosService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Se regeneran las tareas programadas (cron jobs) para OMniLeads/Asterisk.
    """
    help = "Se regeneran las tareas cron configuradas para OMniLeads/Asterisk"

    def handle(self, *args, **options):
        service = RegeneracionCronosService()
        try:
            service.regenerar_cronos()
        except Exception as e:
            logger.error(f"Fallo al regenerar cron jobs: {e}")
            raise CommandError(f"Fallo al regenerar cron jobs: {e}")
