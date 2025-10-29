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
from asgiref.sync import sync_to_async
from notification_app.notification import AgentNotifier
an = AgentNotifier()

logger = logging.getLogger(__name__)


@sync_to_async
def hydrate_kwargs(kwargs):
    # accessing these attributes trigger queries if necessary
    if "conversation" in kwargs:
        if kwargs["conversation"].agent:
            kwargs["conversation"].agent.user
        kwargs["conversation"].mensajes.count()
    if "line" in kwargs:
        pass
    if "message" in kwargs:
        if kwargs["message"].conversation:
            if kwargs["message"].conversation.client:
                kwargs["message"].conversation.client.bd_contacto


async def send_notify(notify_type, **kwargs):
    await hydrate_kwargs(kwargs)
    try:
        logger.debug("send-notify notify_type=%r kwargs=%r", notify_type, kwargs)
        notify = getattr(an, notify_type)
        agents = []
        if kwargs.get('conversation', None):
            if kwargs['conversation'].agent:
                agents.append(kwargs['conversation'].agent)
            elif kwargs['conversation'].campana:
                agents.extend(kwargs['conversation'].campana.obtener_agentes())
            for agent in agents:
                logger.debug("notify agent agent=%r", agent)
                await notify(agent.user_id, **kwargs)
    except Exception as e:
        logger.exception("error en send_notify %r", e)
