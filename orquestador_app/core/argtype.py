
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
