import datetime
import time
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification_app.consumers import AgentConsole
from ominicontacto_app.services.redis.redis_streams import RedisStreams


class AgentNotifier:

    TYPE_UNPAUSE_CALL = 'unpause-call'

    def get_group_name(self, user_id=None):
        if user_id is not None:
            return AgentConsole.GROUP_USER_OBJ.format(user_id=user_id)
        else:
            return AgentConsole.GROUP_USER_CLS

    def send_message(self, type, message, user_id=None):
        # si user_id=None se envia mensaje a todos los agentes conectados

        async_to_sync(get_channel_layer().group_send)(self.get_group_name(user_id), {
            "type": "broadcast",
            "payload": {
                "type": type,
                "args": message
            }
        })


class RedisStreamNotifier:

    def __init__(self):
        self.redis_stream = RedisStreams()

    def send(self, type_event, actives=None):
        if type_event == 'auth_event':
            stream_name = 'auth_event_{}'.format(str(datetime.date.today()))
        elif type_event == 'calification':
            stream_name = 'calification_event_{}'.format(str(datetime.date.today()))
        content = {
            'event': type_event,
            'timestamp': time.time(),
            'actives': actives
        }
        self.redis_stream.write_stream(stream_name, json.dumps(content), max_stream_length=100000)
