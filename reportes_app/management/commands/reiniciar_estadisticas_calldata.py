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

import os
import logging
from django.core.management.base import BaseCommand

from ominicontacto_app.services.redis.connection import create_redis_connection
from reportes_app.services.redis.call_data_generation import CallDataGenerator


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Reinicia valores de calldata al comenzar nuevo día.
    """

    help = 'Reinicia estadísticas al comenzar nuevo día.'

    def reiniciar_estadisticas(self):
        redis_oml_connection = create_redis_connection(0)
        redis_calldata_connection = create_redis_connection(2)
        calldata_generator = CallDataGenerator(redis_calldata_connection)
        calldata_generator.eliminar_datos()
        if not os.getenv('WALLBOARD_VERSION', '') == '':
            from wallboard_app.redis.regeneracion import reiniciar_wallboard_cache
            reiniciar_wallboard_cache(redis_oml_connection, redis_calldata_connection)

    def handle(self, *args, **options):
        try:
            self.reiniciar_estadisticas()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
