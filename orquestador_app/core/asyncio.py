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
from asyncio import FIRST_COMPLETED
from asyncio import AbstractEventLoop as Loop
from asyncio import CancelledError
from asyncio import Future
from asyncio import Queue
from asyncio import Task
from asyncio import all_tasks
from asyncio import current_task
from asyncio import gather
from asyncio import get_event_loop
from asyncio import set_event_loop_policy
from asyncio import sleep
from asyncio import wait
from asyncio import run


_tasks = set()


def create_task(loop: Loop, coro, name: str):
    task = loop.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_done_callback)
    return task


def _done_callback(task):
    _tasks.remove(task)


__all__ = [
    "FIRST_COMPLETED",
    "CancelledError",
    "Future",
    "Loop",
    "Queue",
    "Task",
    "all_tasks",
    "create_task",
    "current_task",
    "gather",
    "get_event_loop",
    "set_event_loop_policy",
    "sleep",
    "wait",
    "run",
]
