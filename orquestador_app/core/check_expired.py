from orquestador_app.core.notify_agents import send_notify


async def check_expired(expire, timestamp, message):
    try:
        if expire:
            if message.conversation.expire:
                if message.conversation.expire < expire:  # expired conversation
                    message.conversation.expire = expire
                    message.conversation.save()
                    await send_notify('notify_whatsapp_chat_expired',
                                      conversation=message.conversation)
            else:
                message.conversation.expire = expire
                message.conversation.timestamp = timestamp
                message.conversation.save()
    except Exception as e:
        print('error en check_expired >>>', e)
