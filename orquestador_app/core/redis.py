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
from orquestador_app.core.media_management import meta_get_media_content
from whatsapp_app.models import Linea, ConfiguracionProveedor

from django.utils import timezone
from datetime import datetime

import logging as _logging

logger = _logging.getLogger(__name__)


streams = dict()


async def connect_to_stream(name: str, line: Linea, redis: RedisServer):
    redis = redis.client()
    try:
        print("connect to stream for line >>>", line.nombre, line.destino)
        print("connect to stream >>>", name)
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
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        return 'whatsapp_webhook_gupshup_{}'.format(line.configuracion["app_id"])
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        return 'whatsapp_webhook_meta_{}'.format(line.configuracion["app_id"])


async def subscribe(line: Linea, redis_host: RedisServer, loop: Loop):
    if line.id in streams:
        print("cancelling old subcription task for line >>>", line.nombre)
        task = streams.pop(line.id)
        task.cancel()
        del task
    cname = get_stream_name(line)
    tname = f"redis-stream id={line.id} name={cname}"
    streams[line.id] = create_task(loop, connect_to_stream(cname, line, redis_host), tname)


async def unsubscribe(line):
    if line.id not in streams:
        return
    try:
        print("unsubscribe to stream line >>>", line.nombre)
        task = streams.pop(line.id)
        task.cancel()
        del task
    except Exception as e:
        print("error >>>", e)


async def meta_handler_messages(line, payloads):
    try:
        for msg in payloads:
            msg_json = loads(msg)
            value_object = msg_json['entry'][0]['changes'][0]['value']
            if 'statuses' in value_object:
                timestamp = datetime.fromtimestamp(
                    int(value_object['statuses'][0]['timestamp']), timezone.get_current_timezone())
                status = value_object['statuses'][0]['status']
                message_id = value_object['statuses'][0]['id']
                destination = value_object['statuses'][0]['recipient_id']
                expire = None
                error_ex = {}
                if 'errors' in value_object['statuses'][0]:
                    error_ex = value_object['statuses'][0]['errors'][0]
                if status == 'sent':
                    expire = datetime.fromtimestamp(
                        int(value_object['statuses'][0]['conversation']['expiration_timestamp']),
                        timezone.get_current_timezone())
                await outbound_chat_event(
                    timestamp, message_id, status, expire=expire,
                    destination=destination, error_ex=error_ex)
            if 'messages' in value_object:
                timestamp = datetime.fromtimestamp(
                    int(value_object['messages'][0]['timestamp']), timezone.get_current_timezone())
                message_id = value_object['messages'][0]['id']
                origen = value_object['messages'][0]['from']
                type = value_object['messages'][0]['type']
                context = None
                if type == 'text':
                    content = {type: value_object['messages'][0][type]['body']}
                if type in ['video', 'image', 'document']:
                    content = meta_get_media_content(line, type, value_object['messages'][0])
                if type == 'interactive':
                    context = value_object['messages'][0]['context']
                    if 'list_reply' in value_object['messages'][0]['interactive']:
                        type = 'list_reply'
                        content = value_object['messages'][0]['interactive']['list_reply']
                sender = value_object['contacts'][0]
                await inbound_chat_event(
                    line,
                    timestamp,
                    message_id,
                    origen,
                    content,
                    sender,
                    context,
                    type,
                )
    except Exception as e:
        print(">>>>>", e)


async def gupshup_handler_messages(line, payloads):
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
                error_ex = {}
                expire = None
                if status == 'failed':
                    logger.error(msg_json['payload']['payload']['reason'])
                    error_ex = msg_json['payload']['payload']
                if status == 'sent':
                    expire = datetime.fromtimestamp(
                        msg_json['payload']['conversation']['expiresAt'],
                        timezone.get_current_timezone())
                await outbound_chat_event(
                    timestamp, message_id, status, expire=expire,
                    destination=destination, error_ex=error_ex)
            if msg_json['type'] == 'message':  # entrante
                message_id = msg_json['payload']['id']
                origen = msg_json['payload']['source']
                type = msg_json['payload']['type']
                content = msg_json['payload']['payload']
                context = msg_json['payload']['context'] if type == 'list_reply' else {}
                sender = msg_json['payload']['sender']
                await inbound_chat_event(
                    line,
                    timestamp,
                    message_id,
                    origen,
                    content,
                    sender,
                    context,
                    type,
                )
    except Exception as e:
        print("Error----->>>>", e)


async def handler_messages(line, payloads):
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        await gupshup_handler_messages(line, payloads)
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        await meta_handler_messages(line, payloads)
