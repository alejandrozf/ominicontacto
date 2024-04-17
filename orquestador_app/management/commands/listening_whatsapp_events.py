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
import threading
from django.conf import settings
from django.core.management.base import BaseCommand
from orquestador_app.core.argtype import redis_host
from orquestador_app.core.asyncio import get_event_loop
from orquestador_app.core.asyncio import create_task
from orquestador_app.core.asyncio import run
from orquestador_app.core.asyncio import Loop
from orquestador_app.core.argtype import RedisServer
from orquestador_app.core.redis import subscribe, unsubscribe  # noqa: F401
from whatsapp_app.models import Linea

logger = logging.getLogger(__name__)


def wrap_async_func(func, *args):
    method = eval(func)
    run(method(*args))


async def start(redis_host, lines_id, loop):
    enabled_lines = Linea.objects_default.filter(id__in=lines_id)
    for ws_linea in enabled_lines:
        if ws_linea.is_active:
            print("subscribe linea activa con id:", ws_linea.id)
            args = ['subscribe', ws_linea, redis_host, loop]
        else:
            print("unsubscribe linea inactiva con id:", ws_linea.id)
            args = ['unsubscribe', ws_linea]

        _thread_line = threading.Thread(
            target=wrap_async_func,
            args=args
        )
        _thread_line.setDaemon(True)
        _thread_line.start()
    if len(enabled_lines) < len(lines_id):
        print("No se encontraron todas las lineas: ", lines_id, enabled_lines)


async def searching_enabled_lines(stream_name, redis_host: RedisServer, loop: Loop):
    try:
        redis = redis_host.client()
        streams = {
            stream_name: "0"
        }
        while True:
            try:
                lines = set()
                for stream, msgs in await redis.xread(streams=streams, block=300):
                    stream = stream.decode("utf-8")
                    for msg_id, msg in msgs:
                        msg_id = msg_id.decode("utf-8")
                        payload = list(msg.items())[0][1].decode("utf-8")
                        lines.add(payload)
                    streams[stream] = msg_id
                    if lines:
                        _thread_lines = threading.Thread(
                            target=wrap_async_func,
                            args=[
                                'start',
                                redis,
                                lines,
                                loop
                            ]
                        )
                        _thread_lines.setDaemon(True)
                        _thread_lines.start()
            except TimeoutError:
                pass
    except Exception as exception:
        print(">>>>>>>>", exception)
    finally:
        await redis.close(close_connection_pool=True)


async def subscribe_stream(stream_name, redis, loop):
    tname = f"redis-stream {stream_name}"
    create_task(loop, await searching_enabled_lines(stream_name, redis, loop), tname)


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            host = settings.REDIS_HOSTNAME
            port = settings.CONSTANCE_REDIS_CONNECTION['port']
            redis = redis_host("redis://{}:{}".format(host, port))
            loop = get_event_loop()
            try:
                stream_name = 'whatsapp_enabled_lines'
                loop.run_until_complete(subscribe_stream(stream_name, redis, loop))
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
        except Exception as e:
            logger.error('Fallo del comando: {0}'.format(e))
