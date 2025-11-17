from django.utils import timezone
from datetime import datetime
from json import loads
from orquestador_app.core.facebook.outbound_chat_event_management import outbound_chat_event
from orquestador_app.core.facebook.inbound_chat_event_management import inbound_chat_event


async def facebook_messenger_handler_messages(page, payloads):
    try:
        for msg in payloads:
            msg_json = loads(msg)
            expire = None
            for entry in msg_json['entry']:
                for messaging_event in entry['messaging']:
                    timestamp = datetime.fromtimestamp(
                        int(messaging_event['timestamp']) / 1000,
                        timezone.get_current_timezone())

                    if 'message' in messaging_event:
                        message_id = messaging_event['message']['mid']
                        origen = messaging_event['sender']['id']
                        type = 'message'
                        content = {}
                        if 'text' in messaging_event['message']:
                            content = {'text': messaging_event['message']['text']}
                        elif 'attachments' in messaging_event['message']:
                            attachment = messaging_event['message']['attachments'][0]
                            type = attachment['type']
                            content = {type: attachment['payload']}
                        sender = {'id': messaging_event['sender']['id']}

                    if 'postback' in messaging_event:
                        message_id = messaging_event['postback']['mid']\
                            if 'mid' in messaging_event['postback'] else ''
                        origen = messaging_event['sender']['id']
                        type = 'postback'
                        content = {'postback': messaging_event['postback']}
                        sender = {'id': messaging_event['sender']['id']}

                    if 'quick_reply' in messaging_event:
                        message_id = messaging_event['quick_reply']['mid']\
                            if 'mid' in messaging_event['quick_reply'] else ''
                        origen = messaging_event['sender']['id']
                        type = 'quick_reply'
                        content = {'quick_reply': messaging_event['quick_reply']}
                        sender = {'id': messaging_event['sender']['id']}

                    if 'delivery' in messaging_event:
                        message_id = messaging_event['delivery']['mids'][0]\
                            if 'mids' in messaging_event['delivery'] else ''
                        origen = messaging_event['sender']['id']
                        type = 'delivery'
                        content = {'delivery': messaging_event['delivery']}
                        sender = {'id': messaging_event['sender']['id']}

                    if 'read' in messaging_event:
                        message_id = messaging_event['read']['watermark']\
                            if 'watermark' in messaging_event['read'] else ''
                        origen = messaging_event['sender']['id']
                        type = 'read'
                        content = {'read': messaging_event['read']}
                        sender = {'id': messaging_event['sender']['id']}

                    if type in ['delivery', 'read']:
                        await outbound_chat_event(
                            timestamp, message_id, status=type, expire=expire,
                            destination=origen, error_ex={})
                    elif type in ['message', 'postback', 'quick_reply']:
                        await inbound_chat_event(
                            page,
                            timestamp,
                            message_id,
                            origen,
                            content,
                            sender,
                            context=None,
                            type=type,
                        )
    except Exception as e:
        print("Error facebook messenger handler >>>>", e)
