from django.utils import timezone
from datetime import datetime
from whatsapp_app.models import Linea as Line
from orquestador_app.core.whatsapp.outbound_chat_event_management import outbound_chat_event
from orquestador_app.core.whatsapp.inbound_chat_event_management import inbound_chat_event
from orquestador_app.core.whatsapp.media_management import meta_get_media_content
import logging as _logging

logger = _logging.getLogger(__name__)


def _extract_forward_flags(*candidates):
    flags = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("forwarded") is True or candidate.get("isForwarded") is True:
            flags["forwarded"] = True
        if (
            candidate.get("frequently_forwarded") is True
            or candidate.get("frequentlyForwarded") is True
        ):
            flags["frequently_forwarded"] = True
    return flags


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
            context = event["payload"]["context"] if 'context' in event["payload"] else {}
            if type in ["video", "image", "document"]:
                if context:
                    type = "reply_" + type
            if type == "text":
                if context:
                    type = "reply_text"
            if type == "quick_reply":
                type = event["payload"]["payload"]["type"]

            content = event["payload"]["payload"]
            forward_flags = _extract_forward_flags(
                event["payload"],
                event["payload"].get("payload"),
                context,
            )
            if isinstance(content, dict):
                content.update(forward_flags)

            await inbound_chat_event(
                line,
                event_timestamp,
                event["payload"]["id"],
                event["payload"]["source"],
                content,
                event["payload"]["sender"],
                context,
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
            message = value_object["messages"][0]
            event_timestamp = datetime.fromtimestamp(
                int(message["timestamp"]),
                timezone.get_current_timezone(),
            )
            type = message["type"]
            context = None
            forward_flags = _extract_forward_flags(message, message.get(type))
            if type == "text":
                content = {
                    type: message[type]["body"]
                }
                content.update(forward_flags)
                if 'context' in message:
                    context = message["context"]
                    type = "reply_text"

            if type in ["video", "image", "document"]:
                content = meta_get_media_content(line, type, message)
                content.update(forward_flags)
                if 'context' in message:
                    context = message["context"]
                    type = "reply_" + type

            if type == "interactive":
                context = message.get("context")
                if "list_reply" in message["interactive"]:
                    type = "list_reply"
                    content = message["interactive"]["list_reply"]
                    content.update(forward_flags)
            if type == "button":
                context = message.get("context")
                type = "button"
                content = message["button"]
                content.update(forward_flags)
            sender = value_object["contacts"][0]
            await inbound_chat_event(
                line,
                event_timestamp,
                message["id"],
                message["from"],
                content,
                sender,
                context,
                type,
            )
    except Exception:
        logger.exception("handle_meta_messages event=%r", event)
