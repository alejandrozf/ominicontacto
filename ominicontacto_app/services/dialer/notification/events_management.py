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

from ominicontacto_app.services.dialer.notification.subscription import SUBSCRIBERS_KEY
from notification_app.notification import DialerStatsNotifier


class OmnidialerEventManager(object):

    def __init__(self, redis_connection) -> None:
        self.redis_connection = redis_connection
        self.notifier = DialerStatsNotifier()

    async def manage_event(self, event_data):
        await self.notifier.notify(event_data, 'omnidialer')

        # Igoro los EVENT
        if event_data.get('type') == 'EVENT':
            return

        print('OmnidialerEventManager - Evento recibido:', event_data)
        subscriptors = self._get_event_subscriptors(event_data)
        print('SUBSCRIPTORS:', subscriptors)
        for subscriptor_id in subscriptors:
            await self.notifier.notify(event_data, subscriptor_id)

    def _get_event_subscriptors(self, event_data):
        camp_id = event_data.get('camp_id')
        print('CAMP ID:', camp_id)
        if camp_id:
            subscriptions_key = SUBSCRIBERS_KEY.format(camp_id)
            return self.redis_connection.smembers(subscriptions_key)  # db 2
