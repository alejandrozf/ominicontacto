from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification_app.consumers import AgentConsole


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
