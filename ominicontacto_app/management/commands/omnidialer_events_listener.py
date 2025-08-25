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

import json
import logging

from django.core.management.base import BaseCommand
from ominicontacto_app.services.redis.connection import create_redis_connection

from ominicontacto_app.services.dialer.notification.events_management import OmnidialerEventManager
from ominicontacto_app.services.dialer.notification.asyncio import get_event_loop, create_task
# from wallboard_app.management.utils.asyncio import get_event_loop, create_task

OMNIDIALER_EVENTS_CHANNEL = 'OML:CHANNEL:DIALER'
CALLDATA_DB = 2
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Atiende eventos del canal de OMniDialer para actualizar datos de campañas'

    async def manage_events(self, channels, redis_connection, loop):
        event_manager = OmnidialerEventManager(redis_connection)
        # Subscribe to a channel
        pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)

        pubsub.subscribe(channels)

        # Listen for messages indefinitely
        for message in pubsub.listen():
            if message['type'] == 'message':
                message_data = message['data']
                try:
                    event_data = json.loads(message_data)
                    await event_manager.manage_event(event_data)
                except Exception as e:
                    logging.error(e, exc_info=True)

    async def subscribe_channels(self, channels, redis, loop):
        create_task(loop, await self.manage_events(channels, redis, loop))

    def handle(self, *args, **options):
        try:
            # Connect to Redis server
            redis_connection = create_redis_connection(db=CALLDATA_DB)
            loop = get_event_loop()
            try:
                channels = [OMNIDIALER_EVENTS_CHANNEL, ]
                loop.run_until_complete(self.subscribe_channels(channels, redis_connection, loop))
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
