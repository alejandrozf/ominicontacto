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
from notification_app.notification import AgentNotifier
an = AgentNotifier()


async def send_notify(notify_type, **kwargs):
    try:
        print("notify_type >>>>", notify_type)
        notify = getattr(an, notify_type)
        agents = []
        if kwargs.get('conversation', None):
            if kwargs['conversation'].agent:
                agents.append(kwargs['conversation'].agent)
            elif kwargs['conversation'].campana:
                agents = kwargs['conversation'].campana.obtener_agentes()
            for agent in agents:
                print("notify agent >>>", agent)
                await notify(agent.user_id, **kwargs)
    except Exception as e:
        print('error en send_notify >>>>', e)
