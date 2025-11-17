from django.utils import timezone
from datetime import datetime
from json import loads
from orquestador_app.core.whatsapp.outbound_chat_event_management import outbound_chat_event
from orquestador_app.core.whatsapp.inbound_chat_event_management import inbound_chat_event
from orquestador_app.core.whatsapp.media_management import meta_get_media_content
import logging as _logging

logger = _logging.getLogger(__name__)


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
                    elif 'button_reply' in value_object['messages'][0]['interactive']:
                        type = 'button_reply'
                        content = value_object['messages'][0]['interactive']['button_reply']
                if type == 'button':
                    type = 'button'
                    content = value_object['messages'][0]['button']
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
