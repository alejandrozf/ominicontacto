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
from argparse import ArgumentTypeError
from typing import NamedTuple
from urllib.parse import urlparse

from redis.asyncio import Redis


class Address(NamedTuple):
    host: str
    port: int


class RedisServer(NamedTuple):
    address: Address

    def client(self):
        return Redis(
            host=self.address.host,
            port=self.address.port,
            socket_timeout=10,
        )


def redis_host(value: str):
    if value:
        url = urlparse(value)
        if url.hostname:
            if url.scheme == "redis":
                return RedisServer(Address(url.hostname, url.port or 6379))
        raise ArgumentTypeError("redisrc formats: redis://host[:port]")
    return None
