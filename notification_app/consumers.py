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
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import redis.asyncio as redis_async
import asyncio

from django.conf import settings

REDIS_URL = f'redis://{settings.REDIS_HOSTNAME}:6379'

REDIS_PUBSUB_CHANNEL = "OML:CHANNEL:DIALER"


class AgentConsole(AsyncJsonWebsocketConsumer):

    GROUP_USER_CLS = "agent-console"
    GROUP_USER_OBJ = "agent-console-{user_id}"
    GROUPS = [
        GROUP_USER_CLS,
        GROUP_USER_OBJ,
    ]

    async def connect(self):
        self.user = self.scope["user"]

        group_name = AgentConsole.GROUP_USER_OBJ.format(user_id=self.user.id)
        await get_channel_layer().group_send(group_name, {
            "type": "broadcast",
            "payload": {
                "type": "logout",
            }})

        if self.user.is_authenticated and self.user.is_agente:
            for group in self.GROUPS:
                await self.channel_layer.group_add(
                    group.format(user_id=self.user.id), self.channel_name)
            return await self.accept()
        return await self.close()

    async def disconnect(self, close_code):
        for group in self.GROUPS:
            await self.channel_layer.group_discard(
                group.format(user_id=self.user.id), self.channel_name)

    async def broadcast(self, event):
        await self.send_json(event["payload"])


class AgentConsoleWhatsapp(AsyncJsonWebsocketConsumer):

    GROUP_USER_CLS = "agent-console-whatsapp"
    GROUP_USER_OBJ = "agent-console-whatsapp-{user_id}"
    GROUPS = [
        GROUP_USER_CLS,
        GROUP_USER_OBJ,
    ]

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated and self.user.is_agente:
            for group in self.GROUPS:
                await self.channel_layer.group_add(
                    group.format(user_id=self.user.id), self.channel_name)
            return await self.accept()
        return await self.close()

    async def disconnect(self, close_code):
        for group in self.GROUPS:
            await self.channel_layer.group_discard(
                group.format(user_id=self.user.id), self.channel_name)

    async def broadcast(self, event):
        await self.send_json(event["payload"])


class RedisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Subscribe to Redis PUBSUB
        self.redis = await redis_async.from_url(REDIS_URL)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(REDIS_PUBSUB_CHANNEL)

        # Start listening for messages
        asyncio.create_task(self.listen_to_redis())

    async def disconnect(self, close_code):
        await self.pubsub.unsubscribe(REDIS_PUBSUB_CHANNEL)
        await self.redis.close()

    async def listen_to_redis(self):
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                data = message["data"].decode("utf-8")
                await self.send(text_data=data)
