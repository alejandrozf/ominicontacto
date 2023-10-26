from whatsapp_app.models import MensajeWhatsapp
from orquestador_app.core.notify_agents import send_notify
from orquestador_app.core.check_expired import check_expired


async def outbound_chat_event(timestamp, message_id, status, expire):
    try:
        message = MensajeWhatsapp.objects.get(message_id=message_id)
        message.status = status
        message.save()
        await send_notify(
            'notify_whatsapp_message_status',
            conversation=message.conversation,
            message=message
        )
        await check_expired(expire, timestamp, message)
    except Exception as e:
        print(">>>>>>>> Error: ", e)
