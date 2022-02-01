from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('channels/agent-console', consumers.AgentConsole.as_asgi()),
]
