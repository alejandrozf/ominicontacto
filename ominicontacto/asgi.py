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
import os
import django
import notification_app.routing

from channels.routing import ProtocolTypeRouter
from channels.routing import ChannelNameRouter
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from ominicontacto_app.bgtasks import BackgroundTasksConsumerClient  # noqa: E402
from ominicontacto_app.bgtasks import BackgroundTasksConsumerWorker  # noqa: E402

if not os.getenv('WALLBOARD_VERSION', '') == '':
    import wallboard_app.routing

django.setup()

websocket_urlpatterns = [
    path(
        "channels/background-tasks",
        BackgroundTasksConsumerClient.as_asgi(),
        kwargs={"viewname": "channels-background-tasks"}
    ),
]
websocket_urlpatterns.extend(notification_app.routing.websocket_urlpatterns)
if not os.getenv('WALLBOARD_VERSION', '') == '':
    websocket_urlpatterns.extend(wallboard_app.routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    "channel": ChannelNameRouter({
        "background-tasks": BackgroundTasksConsumerWorker.as_asgi(),
    }),
})
