from json import loads
from redis.exceptions import TimeoutError
from orquestador_app.core.argtype import RedisServer
from orquestador_app.core.asyncio import CancelledError
from orquestador_app.core.asyncio import Loop
from orquestador_app.core.asyncio import create_task
from orquestador_app.core.gupshup_send_menssage import handler_autoresponses
from django.contrib.contenttypes.models import ContentType
from whatsapp_app.models import (
    Linea, ConversacionWhatsapp, MensajeWhatsapp)
from notification_app.notification import AgentNotifier
from django.utils import timezone
from datetime import datetime


streams = {}


async def connect_to_stream(name: str, line: Linea, redis_host: RedisServer):
    try:
        redis = redis_host.client()
        streams = {
            name: "0-0"
        }
        while True:
            try:
                payloads = []
                for stream, msgs in await redis.xread(streams=streams, block=1000 * 10):
                    stream = stream.decode("utf-8")
                    for msg_id, msg in msgs:
                        msg_id = msg_id.decode("utf-8")
                        payload = list(msg.items())[0][1].decode("utf-8")
                        stream_id_part = f'\"stream_id\":\"{msg_id}\"'
                        payload = f'{payload[:-1]},{stream_id_part}' + '}'
                        payloads.append(payload)
                    streams[stream] = msg_id
                    await handler_messages(line, payloads)
            except TimeoutError:
                pass
    except CancelledError:
        pass
    except Exception as exception:
        print(">>>>>>>>", exception)
    finally:
        await redis.close(close_connection_pool=True)


def get_stream_name(line):
    return 'whatsapp_webhook_gupshup_{}'.format(line.configuracion["app_id"])


async def subscribe(line: Linea, redis_host: RedisServer, loop: Loop):
    cname = get_stream_name(line)
    tname = f"redis-stream id={line.id} name={cname}"
    create_task(loop, await connect_to_stream(cname, line, redis_host), tname)


async def unsubscribe(line):
    task = streams.pop(line)
    task.cancel()
    del task


def get_streams_status():
    return [task.get_name() for task in streams.values()]


async def handler_messages(line, payloads):
    try:
        destination_entrante = line.destino
        if destination_entrante.content_type == ContentType.objects.get(model='campana'):
            agent_notifier = AgentNotifier()
            campana = destination_entrante.content_object
            for msg in payloads:
                msg_json = loads(msg)
                if msg_json['type'] == 'message-event'\
                        and not msg_json['payload']['type'] == 'enqueued':
                    # buscar el mensaje que gener el evento:
                    message_id = msg_json['payload']['gsId']
                    message = MensajeWhatsapp.objects.get(message_id=message_id)
                    message.status = msg_json['payload']['type']
                    message.save()
                    print("notificar al agente estatus de su mensaje ==>",
                          msg_json['payload']['type'])
                    if msg_json['payload']['type'] == 'sent':
                        destination = msg_json['payload']['destination']
                        timestamp = datetime.fromtimestamp(
                            msg_json['timestamp'] / 1000, timezone.get_current_timezone())
                        expire =\
                            datetime.fromtimestamp(
                                msg_json['payload']['conversation']['expiresAt'],
                                timezone.get_current_timezone())
                        conversation_type = msg_json['payload']['conversation']['type']
                        if not message.conversation:  # crear coneveracion
                            conversation = ConversacionWhatsapp.objects.create(
                                destination=destination,
                                expire=expire,
                                campana=campana,
                                conversation_type=conversation_type,
                                timestamp=timestamp
                            )
                            conversation.save()
                            message.conversation = conversation
                            message.save()
                            previous_messages = MensajeWhatsapp.objects.filter(
                                origen=destination,
                                timestamp__lte=timestamp,
                                conversation__isnull=True
                            ).update(conversation=conversation)
                            if previous_messages:
                                conversation.is_active = True
                                conversation.save()
                        else:  # extension de conversacion expirada
                            print("expirada", expire)
                            message.conversation.timestamp = timestamp
                            message.conversation.expire = expire
                            message.conversation.save()
                print(msg_json)
                if msg_json['type'] == 'message':  # mensajes enviados por cliente
                    # crear mensaje
                    message_id = msg_json['payload']['id']
                    timestamp = datetime.fromtimestamp(
                        msg_json['timestamp'] / 1000, timezone.get_current_timezone())
                    origen = msg_json['payload']['source']
                    type = msg_json['payload']['type']
                    content = msg_json['payload']['payload']
                    sender = msg_json['payload']['sender']
                    conversation = ConversacionWhatsapp.objects.filter(
                        campana=campana, destination=origen, expire__gte=timestamp).last()
                    print("conversation >>>>>", conversation)
                    message, created_message =\
                        MensajeWhatsapp.objects.get_or_create(message_id=message_id, defaults={
                            'origen': origen,
                            'timestamp': timestamp,
                            'sender': sender,
                            'content': content,
                            'type': type,
                        })
                    if conversation:
                        message.conversation = conversation
                        message.save()
                        conversation_new = False
                        if not conversation.is_active:
                            conversation.is_active = True
                            conversation.save()
                    else:  # mensaje de bienvenida
                        conversation_new = True
                    if created_message and conversation:
                        # evento mensaje nuevo
                        if conversation and conversation.agent:
                            message = {
                                'chat_id': message.conversation.id,
                                'campaing_id': campana.id,
                                'message_id': message.id,
                                'content': message.content,
                                'origen': origen,
                                'timestamp': timestamp,
                                'sender': sender,
                                'type': type
                            }
                            print("new message...")
                            await agent_notifier.notify_whatsapp_new_message(
                                conversation.agent.user_id, message)
                        else:
                            message = {
                                'campaing_id': campana.id,
                                'message_id': message.id,
                                'content': message.content,
                                'origen': origen,
                                'timestamp': timestamp,
                                'sender': sender,
                                'type': type
                            }
                            agentes = campana.obtener_agentes()
                            for agente in agentes:
                                print("new message...")
                                await agent_notifier.notify_whatsapp_new_message(
                                    agente.user_id, message)
                    print("conversation_new", conversation_new)
                    handler_autoresponses(line, origen, sender, conversation_new)
        else:
            pass
    except Exception as e:
        print("Error----->>>>", e)
        # raise
