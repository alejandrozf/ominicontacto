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
from ominicontacto_app.services.redis.connection import create_redis_connection
from ominicontacto_app.models import Campana

# Manejo las suscripciones por campaña
SUBSCRIBERS_KEY = "OML:DIALER-STATS:SUBSCRIBERS:{0}"


class DialerStatsSubscriptionManager():
    _redis_connection = None

    @property
    def redis_connection(self):
        if self._redis_connection is None:
            self._redis_connection = create_redis_connection(db=2)
        return self._redis_connection

    def get_dialer_campaigns_ids(self, user):
        campanas = Campana.objects.obtener_campanas_dialer()
        if not user.get_is_administrador():
            campanas = Campana.objects.obtener_campanas_asignadas_o_creadas_by_user(campanas, user)
        return campanas.values_list('id', flat=True)

    def add_subscription(self, user):
        for campana_id in self.get_dialer_campaigns_ids(user):
            subscribers_key = SUBSCRIBERS_KEY.format(campana_id)
            self.redis_connection.sadd(subscribers_key, user.id)

    def remove_subscription(self, user):
        for campana_id in self.get_dialer_campaigns_ids(user):
            subscribers_key = SUBSCRIBERS_KEY.format(campana_id)
            self.redis_connection.srem(subscribers_key, user.id)
