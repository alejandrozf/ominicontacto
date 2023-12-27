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
from json import loads
from redis.exceptions import TimeoutError
from orquestador_app.core.argtype import RedisServer
from orquestador_app.core.asyncio import CancelledError
from orquestador_app.core.asyncio import Loop
from orquestador_app.core.asyncio import create_task
from orquestador_app.core.outbound_chat_event_management import outbound_chat_event
from orquestador_app.core.inbound_chat_event_management import inbound_chat_event
from whatsapp_app.models import Linea

from django.utils import timezone
from datetime import datetime

import logging as _logging

logger = _logging.getLogger(__name__)


streams = dict()


async def connect_to_stream(name: str, line: Linea, redis: RedisServer):
    redis = redis.client()
    try:
        print("connect to stream for line >>>", line.nombre)
        streams = {
            name: "0-0"
        }
        while True:
            try:
                payloads = []
                for stream, msgs in await redis.xread(streams=streams, block=1000 * 10):
                    stream = stream.decode("utf-8")
                    for msg_id, msg in msgs:
                        msg_id = msg_id.decode("utf-8")
                        payload = list(msg.items())[0][1].decode("utf-8")
                        stream_id_part = f'\"stream_id\":\"{msg_id}\"'
                        payload = f'{payload[:-1]},{stream_id_part}' + '}'
                        payloads.append(payload)
                    streams[stream] = msg_id
                    await handler_messages(line, payloads)
            except TimeoutError:
                pass
    except CancelledError:
        pass
    except Exception as exception:
        print("error connect_to_stream >>>>>>>>", exception)


def get_stream_name(line):
    return 'whatsapp_webhook_gupshup_{}'.format(line.configuracion["app_id"])


async def subscribe(line: Linea, redis_host: RedisServer, loop: Loop):
    cname = get_stream_name(line)
    tname = f"redis-stream id={line.id} name={cname}"
    streams[line.id] = create_task(loop, connect_to_stream(cname, line, redis_host), tname)


async def unsubscribe(line):
    try:
        print("unsubscribe to stream line >>>", line.nombre)
        task = streams.pop(line.id)
        task.cancel()
        del task
    except Exception as e:
        print("error >>>", e)


async def handler_messages(line, payloads):
    try:
        for msg in payloads:
            msg_json = loads(msg)
            timestamp = datetime.fromtimestamp(
                msg_json['timestamp'] / 1000, timezone.get_current_timezone())
            if msg_json['type'] == 'message-event'\
                    and not msg_json['payload']['type'] == 'enqueued':  # salientes
                message_id = msg_json['payload']['gsId']
                status = msg_json['payload']['type']
                destination = msg_json['payload']['destination']
                expire = None
                if status == 'failed':
                    logger.error(msg_json['payload']['payload']['reason'])
                if status == 'sent':
                    expire = datetime.fromtimestamp(
                        msg_json['payload']['conversation']['expiresAt'],
                        timezone.get_current_timezone())
                await outbound_chat_event(
                    timestamp, message_id, status, expire=expire, destination=destination)
            if msg_json['type'] == 'message':  # entrante
                message_id = msg_json['payload']['id']
                origen = msg_json['payload']['source']
                type = msg_json['payload']['type']
                content = msg_json['payload']['payload']
                sender = msg_json['payload']['sender']
                await inbound_chat_event(
                    line,
                    timestamp,
                    message_id,
                    origen,
                    content,
                    sender,
                    type,
                )
    except Exception as e:
        print("Error----->>>>", e)
