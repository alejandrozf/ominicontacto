# -*- coding: utf-8 -*-
# Copyright (C) 2025 Freetech Solutions

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

import asyncio
import functools
import json
import logging
import logging.config
import signal
import sys
import typing
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.management import BaseCommand
from django.db import models
from django.db.models import F
from django.db.models.functions import Concat

from redis.asyncio import Redis
from orquestador_app.core.facebook.message_handler import (
    facebook_messenger_handler_messages)
from orquestador_app.core.whatsapp.message_handler import (
    handle_gupshup_message,
    handle_meta_messages,
)
from whatsapp_app.models import ConfiguracionProveedor as ProviderConfig
from whatsapp_app.models import Linea as Line
from facebook_meta_app.models import PaginaMetaFacebook as Page

logger = logging.getLogger(__name__)


class EventsProcessor(object):

    def __init__(self):
        self.master_job = None
        self.redis_client = None
        self.shutdown = asyncio.Event()
        self.slave_tasks = {}

    async def __aenter__(self):
        while not self.shutdown.is_set():
            try:
                self.redis_client = Redis(host=settings.REDIS_HOSTNAME, decode_responses=True)
                await self.redis_client.ping()
                logger.info("connect-to-redis %r", self.redis_client)
                break
            except Exception as exception:
                logger.exception("connect-to-redis %r", exception)
                await asyncio.sleep(1)
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, functools.partial(self.loop_signal_handler, sig))
        self.master_job = asyncio.create_task(
            self.read_stream("whatsapp_enabled_lines", self.handle_master_stream_message_whatsapp),
            name="whatsapp_enabled_lines (suscriber)",
        )
        self.master_job = asyncio.create_task(
            self.read_stream("facebook_enabled_pages", self.handle_master_stream_message_page),
            name="facebook_enabled_pages (suscriber)",
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        tasks = []
        tasks.append(self.master_job)
        tasks.extend(self.slave_tasks.values())
        for task in tasks:
            task.cancel()
            logger.info("task -> cancel")
            for info in task._repr_info()[1:]:
                logger.info("task    %s", info)
        if self.redis_client:
            tasks.append(self.redis_client.aclose())
        await asyncio.gather(*tasks, return_exceptions=True)

    def loop_signal_handler(self, sig: signal.Signals):
        if sig == signal.SIGINT and sys.stderr.writable():
            sys.stderr.write("\b\b\r")
            sys.stderr.flush()
        logger.info("loop-signal-handler %r", sig)
        self.shutdown.set()

    async def read_stream(self, name: str, callback: typing.Callable, fromid="0-0"):
        logger.info("redis-stream-reader %r start", name)
        streams = {
            name: fromid
        }
        while not self.shutdown.is_set():
            try:
                response = await self.redis_client.xread(streams, block=1000 * 2, count=1)
                if response:
                    for msgid, event in response[0][1]:
                        await callback(event)
                    streams[name] = msgid
            except asyncio.TimeoutError:
                logger.info("redis-stream-reader %r timeout", name)
            except asyncio.CancelledError:
                logger.info("redis-stream-reader %r cancelled", name)
                break
            except Exception as exception:
                logger.exception("redis-stream-reader %r %r", name, exception)
                await asyncio.sleep(1)

    async def handle_master_stream_message_whatsapp(self, message: dict):
        line_id = message.get("value")
        try:
            line = await self._get_line(line_id)
            if line.pk in self.slave_tasks:
                task = self.slave_tasks.pop(line.pk)
                task.cancel()
                logger.info("task -> cancel")
                for info in task._repr_info()[1:]:
                    logger.info("task    %s", info)
                await asyncio.gather(task, return_exceptions=True)
            if line.is_active:
                self.slave_tasks[line.pk] = asyncio.create_task(
                    self.read_stream(
                        line.stream_name,
                        functools.partial(self.handle_slave_streams_message_whatsapp, line),
                        fromid=settings.ORCHESTRATOR_SLAVE_STREAM_FROMID,
                    ),
                    name=f"{line.stream_name} (suscriber)",
                )
        except (Line.DoesNotExist, Line.MultipleObjectsReturned) as exception:
            logger.error("process-main-stream-message %r %r", line_id, exception)
        else:
            logger.info("process-main-stream-message %r", line_id)

    async def handle_master_stream_message_page(self, message: dict):
        page_id = message.get("value")
        try:
            page = await self._get_page(page_id)
            if page.pk in self.slave_tasks:
                task = self.slave_tasks.pop(page.pk)
                task.cancel()
                logger.info("task -> cancel")
                for info in task._repr_info()[1:]:
                    logger.info("task    %s", info)
                await asyncio.gather(task, return_exceptions=True)
            if page.is_active:
                self.slave_tasks[page.pk] = asyncio.create_task(
                    self.read_stream(
                        page.stream_name,
                        functools.partial(self.handle_slave_streams_message_page, page),
                        fromid=settings.ORCHESTRATOR_SLAVE_STREAM_FROMID,
                    ),
                    name=f"{page.stream_name} (suscriber)",
                )
        except (Page.DoesNotExist, Page.MultipleObjectsReturned) as exception:
            logger.error("process-main-stream-message %r %r", page_id, exception)
        else:
            logger.info("process-main-stream-message %r", page_id)

    async def handle_slave_streams_message_whatsapp(self, line: Line, event: dict):
        try:
            if event.get("action") == "stop":
                self.shutdown.set()
                return
            payload = json.loads(event.get("value"))
            if line.provider_type == ProviderConfig.TIPO_GUPSHUP:
                await handle_gupshup_message(line, payload)
            elif line.provider_type == ProviderConfig.TIPO_META:
                await handle_meta_messages(line, payload)
        except Exception as exception:
            logger.error("handle_slave_streams_message %r %r", line.id, exception)
            logger.error("Event:", event)

    async def handle_slave_streams_message_page(self, page: Page, event: dict):
        try:
            if event.get("action") == "stop":
                self.shutdown.set()
                return
            print("Received event for page:", page.id)
            print("Event data:", event)
            payload = json.loads(event.get("value"))
            print("Payload data:", payload)
            await facebook_messenger_handler_messages(page, payload)
        except Exception as exception:
            logger.error("handle_slave_streams_message_page %r %r", page.id, exception)
            logger.error("Event:", event)

    @database_sync_to_async
    def _get_line(self, pk):
        queryset = (
            Line.objects_default.only(
                "pk",
                "is_active",
                "nombre",
                "numero",
            ).annotate(
                provider_type=models.F("proveedor__tipo_proveedor"),
                stream_name=models.functions.Concat(
                    models.Value("whatsapp_webhook"),
                    models.Case(
                        models.When(
                            proveedor__tipo_proveedor=ProviderConfig.TIPO_GUPSHUP,
                            then=models.Value("_gupshup_")
                        ),
                        models.When(
                            proveedor__tipo_proveedor=ProviderConfig.TIPO_META,
                            then=models.Value("_meta_")
                        ),
                    ),
                    models.fields.json.KeyTextTransform("app_id", "configuracion"),
                    output_field=models.CharField(),
                ),
            ).prefetch_related(
                "horario__validaciones_tiempo",
            )
        )
        return queryset.get(pk=pk)

    @database_sync_to_async
    def _get_page(self, pk):
        queryset = (
            Page.objects_default.only(
                "pk",
                "is_active",
                "page_id",
                "name",
            ).annotate(
                stream_name=Concat(
                    models.Value("facebook_meta_webhook_page_"),
                    F("app_id"),
                    output_field=models.CharField(),
                ),
            ).prefetch_related(
                "horario__validaciones_tiempo",
            )
        )
        return queryset.get(pk=pk)


class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "msg-formatter": {
                    "format": "%(levelname).3s | %(name)s (%(threadName)s) %(message)s"
                },
            },
            "handlers": {
                "msg-handler": {
                    "class": "logging.StreamHandler",
                    "formatter": "msg-formatter",
                },
            },
            "loggers": {
                "orquestador_app": {
                    "handlers": ["msg-handler"],
                    "level": "DEBUG" if options["verbosity"] > 1 else "INFO",
                    "propagate": False,
                },
            },
        })
        asyncio.run(self.ahandle(), debug=False)

    async def ahandle(self):
        async with EventsProcessor() as processor:
            await processor.shutdown.wait()
