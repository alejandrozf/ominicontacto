from channels.consumer import SyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.apps import apps

from .mixins import SearchRecordingsMixin

BACKGROUND_TASKS_MIXINS = [
    SearchRecordingsMixin,
]

if apps.is_installed("premium_reports_app"):
    BACKGROUND_TASKS_MIXINS.extend(
        getattr(apps.get_app_config("premium_reports_app"), "BACKGROUND_TASKS_CONSUMERS", [])
    )


class BackgroundTasksConsumerClient(AsyncJsonWebsocketConsumer, *BACKGROUND_TASKS_MIXINS):
    groups = [
        "background-tasks",
        "background-tasks.user-{user_id}",
    ]

    async def websocket_connect(self, message):
        self.groups = [group.format(user_id=self.scope["user"].id) for group in self.groups]
        await super().websocket_connect(message)

    async def connect(self):
        if self.scope["user"].is_authenticated:
            tiene_permiso_oml = database_sync_to_async(self.scope["user"].tiene_permiso_oml)
            if await tiene_permiso_oml(self.scope["url_route"]["kwargs"]["viewname"]):
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def receive_json(self, content, **kwargs):
        await self.dispatch(content)


class BackgroundTasksConsumerWorker(SyncConsumer, *BACKGROUND_TASKS_MIXINS):
    pass
