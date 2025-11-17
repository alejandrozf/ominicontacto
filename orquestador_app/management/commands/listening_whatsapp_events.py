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
import asyncio
import logging
import signal

from django.conf import settings
from django.core.management.base import BaseCommand

from orquestador_app.core.argtype import redis_host
from orquestador_app.core.asyncio import get_event_loop, Loop
from orquestador_app.core.webhook_streams import (
    line_streams_subscribe,
    page_streams_subscribe,
)
from whatsapp_app.models import Linea
from facebook_meta_app.models import PaginaMetaFacebook

logger = logging.getLogger(__name__)
logging.getLogger("aioredis").setLevel(logging.WARNING)


# ---------------------------
# Listener genérico que lee mensajes nuevos
# ---------------------------
async def stream_listener(stream_name: str, redis_url: str, loop: Loop,
                          objects, subscribe_fn, stop_event: asyncio.Event):
    rhost = redis_host(redis_url)
    redis_client = rhost.client()
    streams = {stream_name: "0"}  # leer todos los mensajes nuevos desde el inicio

    # Suscribir los objetos existentes
    for obj in objects:
        if getattr(obj, "is_active", False):
            await subscribe_fn(obj, rhost, loop)

    while not stop_event.is_set():
        try:
            result = await redis_client.xread(streams=streams, block=500)
            if not result:
                continue

            for stream, msgs in result:
                stream_dec = stream.decode() if isinstance(stream, bytes) else str(stream)
                for msg_id, msg in msgs:
                    msg_id_dec = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                    payload = {
                        k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in msg.items()
                    }
                    payload["stream_id"] = msg_id_dec
                    # Log simple del mensaje recibido
                    logger.info(f"[{stream_dec}] Nuevo mensaje: {payload}")
                    streams[stream_dec] = msg_id_dec

        except asyncio.CancelledError:
            logger.info(f"Stream {stream_name} cancelado.")
            return
        except Exception as e:
            logger.warning(f"Error leyendo stream {stream_name}: {e}")
            await asyncio.sleep(1)


# ---------------------------
# Crear listeners para líneas y páginas
# ---------------------------
async def subscribe_streams(line_stream_name, page_stream_name, redis_url, loop: Loop,
                            stop_event: asyncio.Event):
    # Obtener todas las líneas y páginas activas
    line_objs = Linea.objects_default.filter(is_active=True)
    page_objs = PaginaMetaFacebook.objects.filter(is_active=True)

    loop.create_task(stream_listener(
        line_stream_name, redis_url, loop, line_objs, line_streams_subscribe, stop_event
    ))

    loop.create_task(stream_listener(
        page_stream_name, redis_url, loop, page_objs, page_streams_subscribe, stop_event
    ))


# ---------------------------
# Comando Django
# ---------------------------
class Command(BaseCommand):
    help = "Listener funcional para Redis Streams (mensajes nuevos en tiempo real)"

    def handle(self, *args, **options):
        host = settings.REDIS_HOSTNAME
        port = settings.CONSTANCE_REDIS_CONNECTION["port"]
        redis_url = f"redis://{host}:{port}"

        loop = get_event_loop()
        stop_event = asyncio.Event()

        def _stop(signame=None):
            logger.info("Signal received: %s. Deteniendo loop...", signame)
            loop.call_soon_threadsafe(stop_event.set)

            async def canceller():
                await asyncio.sleep(1)
                for task in asyncio.all_tasks(loop=loop):
                    if task is not asyncio.current_task(loop=loop):
                        task.cancel()
            loop.create_task(canceller())

        try:
            loop.add_signal_handler(signal.SIGTERM, lambda: _stop("SIGTERM"))
            loop.add_signal_handler(signal.SIGINT, lambda: _stop("SIGINT"))
        except NotImplementedError:
            import signal as s
            s.signal(s.SIGINT, lambda *_: _stop("SIGINT"))

        line_stream = "whatsapp_enabled_lines"
        page_stream = "facebook_enabled_pages"

        loop.create_task(subscribe_streams(line_stream, page_stream, redis_url, loop, stop_event))
        logger.info("Iniciando listeners para streams %s y %s", line_stream, page_stream)

        try:
            loop.run_forever()
        finally:
            logger.info("Shutdown iniciado...")
            stop_event.set()
            tasks = asyncio.all_tasks(loop=loop)
            for t in tasks:
                t.cancel()
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
            logger.info("Shutdown completo.")
