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
from django.core.management.base import BaseCommand
from orquestador_app.core.argtype import redis_host
from orquestador_app.core.asyncio import get_event_loop
from orquestador_app.core.asyncio import Loop
from orquestador_app.core.argtype import RedisServer
from orquestador_app.core.redis import subscribe, unsubscribe
from whatsapp_app.models import Linea

logger = logging.getLogger(__name__)


async def linea_handler(line: Linea, redis_host: RedisServer, loop: Loop):
    try:
        await subscribe(line, redis_host, loop)
    finally:
        await unsubscribe(line)


def start(redis_host):
    loop = get_event_loop()
    try:
        for ws_linea in Linea.objects.filter(is_active=True):
            loop.run_until_complete(linea_handler(ws_linea, redis_host, loop))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            redis = redis_host("redis://redis:6379")
            start(redis)
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
