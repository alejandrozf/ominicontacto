# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import logging

from django.core.management.base import BaseCommand, CommandError

from ominicontacto_app.services.wombat_service import WombatReloader

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Se sincroniza el estado local del servicio Wombat Dialer.
    """

    help = u"Se sincroniza el estado local del servicio Wombat Dialer."

    def _sincronizar_wombat(self):
        wombat_service = WombatReloader()
        wombat_service.synchronize_local_state()

    def handle(self, *args, **options):
        try:
            self._sincronizar_wombat()
        except Exception as e:
            logging.error('Fallo del comando: {0}'.format(e))
            raise CommandError('Fallo del comando: {0}'.format(e))
