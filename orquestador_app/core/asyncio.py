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

_tasks = set()


def create_task(loop: Loop, coro, name: str):
    task = loop.create_task(coro, name=name)
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
]
