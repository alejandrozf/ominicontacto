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
from redis.exceptions import TimeoutError
from orquestador_app.core.argtype import RedisServer
from orquestador_app.core.asyncio import CancelledError, Loop, create_task
from orquestador_app.core.facebook.message_handler import facebook_messenger_handler_messages
from orquestador_app.core.whatsapp.message_handler import (gupshup_handler_messages,
                                                           meta_handler_messages)
from whatsapp_app.models import Linea, ConfiguracionProveedor
from facebook_meta_app.models import PaginaMetaFacebook

import logging

logger = logging.getLogger(__name__)

whatsapp_streams = dict()
page_streams = dict()


# ----------------------------
#  CONNECT TO STREAM
# ----------------------------
async def connect_to_stream(name: str, medium: object, redis: RedisServer):
    """
    Listener estable para un stream de Redis.
    Usa xread con bloqueos cortos (500ms) para evitar timeouts por firewalls/proxies.
    """
    redis_client = redis.client()
    streams = {name: "0-0"}
    print(">>>>>>>>", streams)
    while True:
        try:
            payloads = []
            # Bloque corto para evitar que la conexión quede idle
            for stream, msgs in await redis_client.xread(streams=streams, block=500):
                stream_dec = stream.decode("utf-8") if isinstance(stream, bytes) else str(stream)
                for msg_id, msg in msgs:
                    msg_id_dec = msg_id.decode("utf-8") if isinstance(msg_id, bytes) \
                        else str(msg_id)
                    try:
                        payload = list(msg.items())[0][1].decode("utf-8")
                        # Añadimos el stream_id al payload
                        payload = f'{payload[:-1]},"stream_id":"{msg_id_dec}"}}'
                        payloads.append(payload)
                    except Exception:
                        payloads.append(str(msg))
                    streams[stream_dec] = msg_id_dec

                if payloads:
                    await handler_messages(medium, payloads)

        except TimeoutError:
            # simplemente continuar el loop
            await asyncio.sleep(0.01)
        except CancelledError:
            logger.info(f"Stream {name} cancelado.")
            return
        except Exception as e:
            logger.exception(f"Error en connect_to_stream ({name}): {e}")
            await asyncio.sleep(1)


# ----------------------------
#  LINE STREAMS
# ----------------------------
async def line_streams_subscribe(line: Linea, redis_host: RedisServer, loop: Loop):
    if line and line.id in whatsapp_streams:
        logger.info(f"Cancelling old subscription for line {line.nombre}")
        task = whatsapp_streams.pop(line.id)
        task.cancel()
        del task

    cname = line.get_stream_name
    tname = f"redis-stream id={line.id} name={cname}"
    whatsapp_streams[line.id] = create_task(loop, connect_to_stream(cname, line, redis_host), tname)


async def line_streams_unsubscribe(line):
    if line.id not in whatsapp_streams:
        return
    try:
        logger.info(f"Unsubscribe to stream line {line.nombre}")
        task = whatsapp_streams.pop(line.id)
        task.cancel()
        del task
    except Exception as e:
        logger.warning(f"Error unsubscribing line {line.nombre}: {e}")


# ----------------------------
#  PAGE STREAMS
# ----------------------------
async def page_streams_subscribe(page: PaginaMetaFacebook, redis_host: RedisServer, loop: Loop):
    if page and page.id in page_streams:
        logger.info(f"Cancelling old subscription for page {page.nombre}")
        task = page_streams.pop(page.id)
        task.cancel()
        del task

    cname = page.get_stream_name
    tname = f"redis-stream id={page.id} name={cname}"
    page_streams[page.id] = create_task(loop, connect_to_stream(cname, page, redis_host), tname)


async def page_streams_unsubscribe(page):
    if page.id not in page_streams:
        return
    try:
        logger.info(f"Unsubscribe to stream page {page.nombre}")
        task = page_streams.pop(page.id)
        task.cancel()
        del task
    except Exception as e:
        logger.warning(f"Error unsubscribing page {page.nombre}: {e}")


# ----------------------------
#  HANDLER DE MENSAJES
# ----------------------------
async def handler_messages(medium=None, payloads=None):
    print(payloads)
    if isinstance(medium, Linea):
        if medium.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            await gupshup_handler_messages(medium, payloads)
        elif medium.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            await meta_handler_messages(medium, payloads)
    elif isinstance(medium, PaginaMetaFacebook):
        await facebook_messenger_handler_messages(medium, payloads)
