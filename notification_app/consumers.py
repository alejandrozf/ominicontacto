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
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer


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
