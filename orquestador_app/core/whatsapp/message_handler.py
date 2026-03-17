from django.utils import timezone
from datetime import datetime
from whatsapp_app.models import Linea as Line
from orquestador_app.core.whatsapp.outbound_chat_event_management import outbound_chat_event
from orquestador_app.core.whatsapp.inbound_chat_event_management import inbound_chat_event
from orquestador_app.core.whatsapp.media_management import meta_get_media_content
import logging as _logging

logger = _logging.getLogger(__name__)


async def handle_gupshup_message(line: Line, event: dict):
    try:
        event_timestamp = datetime.fromtimestamp(
            event["timestamp"] / 1000,
            timezone.get_current_timezone(),
        )
        # salientes
        if event["type"] == "message-event" and not event["payload"]["type"] == "enqueued":
            error_ex = None
            expire = None
            if event["payload"]["type"] == "failed":
                logger.error(event["payload"]["payload"]["reason"])
                error_ex = event["payload"]["payload"]
            if event["payload"]["type"] == "sent":
                expire = datetime.fromtimestamp(
                    event["payload"]["conversation"]["expiresAt"],
                    timezone.get_current_timezone(),
                )
            await outbound_chat_event(
                event_timestamp,
                event["payload"]["gsId"],
                event["payload"]["type"],
                expire=expire,
                destination=event["payload"]["destination"],
                error_ex=error_ex,
            )
        # entrante

        elif event["type"] == "message":
            print("event['payload']:", event["payload"])
            type = event["payload"]["type"]
            print("type:", type)
            if type in ["video", "image", "document"]:
                if 'context' in event["payload"]:
                    type = "reply_" + type
            if type == "text":
                if 'context' in event["payload"]:
                    type = "reply_text"
            if type == "quick_reply":
                type = event["payload"]["payload"]["type"]

            await inbound_chat_event(
                line,
                event_timestamp,
                event["payload"]["id"],
                event["payload"]["source"],
                event["payload"]["payload"],
                event["payload"]["sender"],
                event["payload"]["context"] if 'context' in event["payload"] else {},
                type,
            )
    except Exception:
        logger.exception("handle_gupshup_message event=%r", event)


async def handle_meta_messages(line: Line, event: dict):
    try:
        if event.get("object") != "whatsapp_business_account":
            logger.error("Not whatsapp_business_account by line:", line.id)
            logger.error("Event:", event)
        value_object = event["entry"][0]["changes"][0]["value"]
        if "statuses" in value_object:
            event_timestamp = datetime.fromtimestamp(
                int(value_object["statuses"][0]["timestamp"]),
                timezone.get_current_timezone(),
            )
            status = value_object["statuses"][0]["status"]
            expire = None
            error_ex = {}
            if "errors" in value_object["statuses"][0]:
                error_ex = value_object["statuses"][0]["errors"][0]
            if status == "sent":
                expire = datetime.fromtimestamp(
                    int(value_object["statuses"][0]["conversation"]["expiration_timestamp"]),
                    timezone.get_current_timezone(),
                )
            await outbound_chat_event(
                event_timestamp,
                value_object["statuses"][0]["id"],
                status,
                expire=expire,
                destination=value_object["statuses"][0]["recipient_id"],
                error_ex=error_ex,
            )
        if "messages" in value_object:
            event_timestamp = datetime.fromtimestamp(
                int(value_object["messages"][0]["timestamp"]),
                timezone.get_current_timezone(),
            )
            type = value_object["messages"][0]["type"]
            context = None
            if type == "text":
                content = {
                    type: value_object["messages"][0][type]["body"]
                }
                if 'context' in value_object["messages"][0]:
                    context = value_object["messages"][0]["context"]
                    type = "reply_text"

            if type in ["video", "image", "document"]:
                content = meta_get_media_content(line, type, value_object["messages"][0])
                if 'context' in value_object["messages"][0]:
                    context = value_object["messages"][0]["context"]
                    type = "reply_" + type

            if type == "interactive":
                context = value_object["messages"][0]["context"]
                if "list_reply" in value_object["messages"][0]["interactive"]:
                    type = "list_reply"
                    content = value_object["messages"][0]["interactive"]["list_reply"]
            if type == "button":
                context = value_object["messages"][0]["context"]
                type = "button"
                content = value_object["messages"][0]["button"]
            sender = value_object["contacts"][0]
            await inbound_chat_event(
                line,
                event_timestamp,
                value_object["messages"][0]["id"],
                value_object["messages"][0]["from"],
                content,
                sender,
                context,
                type,
            )
    except Exception:
        logger.exception("handle_meta_messages event=%r", event)
