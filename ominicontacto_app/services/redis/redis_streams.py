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
from __future__ import unicode_literals

import redis
from django.conf import settings


class RedisStreams(object):

    def __init__(self, connection=None):
        super().__init__()
        self.connection = connection
        if connection is None:
            self.connection = redis.Redis(host=settings.REDIS_HOSTNAME,
                                          port=settings.CONSTANCE_REDIS_CONNECTION['port'],
                                          decode_responses=True)

    def write_stream(self, stream_name, content, max_stream_length=100):
        self.connection.execute_command('XADD', stream_name, 'MAXLEN',
                                        '~', max_stream_length, '*', 'value', content)

    def flush(self, stream_name):
        self.connection.xtrim(name=stream_name, maxlen=0, approximate=False)
