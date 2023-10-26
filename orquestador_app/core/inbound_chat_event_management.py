from django.contrib.contenttypes.models import ContentType
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp
from orquestador_app.core.gupshup_send_menssage import (
    autoresponse_welcome, autoreponse_destino_interactivo)
from orquestador_app.core.notify_agents import send_notify


async def inbound_chat_event(line, timestamp, message_id, origen, content, sender, type):
    try:
        destination_entrante = line.destino
        campana = None
        if destination_entrante.content_type == ContentType.objects.get(model='campana'):
            campana = destination_entrante.content_object
        # campana = None
        conversation =\
            ConversacionWhatsapp.objects.filter(destination=origen, expire__gte=timestamp).last()
        print(">>>>>> conversation", conversation)
        if not conversation:
            conversation = ConversacionWhatsapp.objects.create(
                campana=campana,
                destination=origen,
                is_active=True,
                agent=None
            )
            if campana:
                autoresponse_welcome(line, conversation, sender)
            else:
                autoreponse_destino_interactivo(line, conversation, sender)  # mensaje con opciones
        elif not conversation.is_active:
            conversation.is_active = True
            conversation.save()
        message_inbound, created_message =\
            MensajeWhatsapp.objects.get_or_create(message_id=message_id, conversation=conversation,
                                                  defaults={
                                                      'origen': origen,
                                                      'timestamp': timestamp,
                                                      'sender': sender,
                                                      'content': content,
                                                      'type': type})
        if type == 'list_reply':
            print(">>>>> actulizar campana de la conversacion")
            print(">>>>> content:", content)
            print(message_inbound.conversation.campana)

        if created_message:
            if conversation.agent:
                await send_notify('notify_whatsapp_new_message',
                                  conversation=conversation,
                                  message=message_inbound)
            elif conversation.campana:
                await send_notify('notify_whatsapp_new_chat', conversation=conversation)
    except Exception as e:
        print(">>>>>>>> Error: ", e)
