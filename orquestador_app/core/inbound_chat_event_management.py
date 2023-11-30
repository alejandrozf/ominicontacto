from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp
from orquestador_app.core.gupshup_send_menssage import (
    autoresponse_welcome, autoreponse_destino_interactivo, send_text_message)
from orquestador_app.core.notify_agents import send_notify


async def inbound_chat_event(line, timestamp, message_id, origen, content, sender, type):
    try:
        destination_entrante = line.destino
        conversation =\
            ConversacionWhatsapp.objects.filter(
                line=line, destination=origen, expire__gte=timestamp).last()
        if not conversation:
            campana = None
            if destination_entrante.content_type == ContentType.objects.get(model='campana'):
                campana = destination_entrante.content_object
            conversation = ConversacionWhatsapp.objects.create(
                line=line,
                campana=campana,
                destination=origen,
                is_active=True,
                agent=None,
                expire=(
                    timestamp + timezone.timedelta(days=1)) - timezone.timedelta(
                        seconds=timestamp.second, microseconds=timestamp.microsecond),
                timestamp=timestamp,
                date_last_interaction=timestamp
            )
            autoresponse_welcome(line, conversation, timestamp)
        else:
            if not conversation.is_active:
                conversation.is_active = True
            if conversation.saliente and not conversation.atendida:
                conversation.atendida = True
            conversation.date_last_interaction = timestamp
            conversation.save()

        message_inbound, created_message =\
            MensajeWhatsapp.objects.get_or_create(message_id=message_id, conversation=conversation,
                                                  defaults={
                                                      'origen': origen,
                                                      'timestamp': timestamp,
                                                      'sender': sender,
                                                      'content': content,
                                                      'type': type})
        if created_message:
            if conversation.agent:
                await send_notify('notify_whatsapp_new_message',
                                  conversation=conversation,
                                  message=message_inbound)
            elif conversation.campana:
                await send_notify('notify_whatsapp_new_chat', conversation=conversation)

        if not conversation.campana:
            if type == 'list_reply':
                asignar_campana(line, conversation, content)
            else:
                autoreponse_destino_interactivo(line, conversation)

    except Exception as e:
        print("inbound_chat_event >>>>>>>> Error: ", e)


def asignar_campana(line, conversation, content):
    try:
        destination_entrante = line.destino
        destino = destination_entrante.destinos_siguientes.filter(
            opcion_menu_whatsapp__opcion__valor=content['title']).last()
        auto_response = {}
        if destino:
            conversation.campana = destino.destino_siguiente.content_object
            conversation.save()
            if destination_entrante.content_object.texto_derivacion:
                auto_response = {"text": destination_entrante.content_object.texto_derivacion}
        else:
            if destination_entrante.content_object.texto_opcion_incorrecta:
                auto_response =\
                    {"text": destination_entrante.content_object.texto_opcion_incorrecta}
        if auto_response:
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            orquestador_response = send_text_message(line, conversation.destination, auto_response)
            if orquestador_response["status"] == "submitted":
                MensajeWhatsapp.objects.get_or_create(
                    message_id=orquestador_response['messageId'],
                    conversation=conversation,
                    defaults={
                        'origen': line.numero,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': auto_response,
                        'type': 'text'
                    }
                )
    except Exception as e:
        print("asignar_campana >>>>>>>", e)
