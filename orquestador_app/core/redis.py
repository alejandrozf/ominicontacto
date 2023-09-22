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
            campana = destination_entrante.content_object
            for msg in payloads:
                msg_json = loads(msg)
                if msg_json['type'] == 'message-event' and \
                        msg_json['payload']['type'] == 'sent':  # conversaciones desde el agente
                    destination = msg_json['payload']['destination']
                    timestamp = msg_json['timestamp']
                    conversation_id = msg_json['payload']['id']
                    expire = msg_json['payload']['conversation']['expiresAt']
                    conversacion_type = msg_json['payload']['conversation']['type']
                    obj, created = ConversacionWhatsapp.objects.get_or_create(
                        destination=destination, expire=int(expire), campana=campana,
                        defaults={
                            'conversation_id': conversation_id,
                            'conversation_type': conversacion_type,
                            'timestamp': timestamp
                        })
                if msg_json['type'] == 'message':  # mensajes enviados por cliente
                    # crear mensaje
                    timestamp = int(msg_json['timestamp'])
                    origen = msg_json['payload']['source']
                    type = msg_json['payload']['type']
                    content = msg_json['payload']['payload']
                    sender = msg_json['payload']['sender']
                    conversation = ConversacionWhatsapp.objects.filter(
                        campana=campana, destination=origen, timestamp__lte=timestamp).last()
                    if conversation:
                        conversation_new = False
                        obj, created = MensajeWhatsapp.objects.get_or_create(
                            conversation=conversation,
                            origen=origen,
                            timestamp=timestamp,
                            defaults={
                                'sender': sender,
                                'content': content,
                                'type': type,
                            }
                        )
                        if created:
                            # evento mensaje nuevo
                            agent_notifier = AgentNotifier()
                            message = {
                                'chat_id': obj.conversation.id,
                                'campaing_id': campana.id,
                                'message_id': obj.id,
                                'content': obj.content,
                                'origen': origen,
                                'timestamp': timestamp,
                                'sender': sender,
                                'type': type
                            }
                            if conversation.agent:
                                print("new message...")
                                await agent_notifier.notify_whatsapp_new_message(
                                    conversation.agent.user_id, message)
                            else:
                                agentes = campana.obtener_agentes()
                                for agente in agentes:
                                    print("new message...")
                                    await agent_notifier.notify_whatsapp_new_message(
                                        agente.user_id, message)
                    else:  # mensaje de bienvenida
                        conversation_new = True
                    handler_autoresponses(line, origen, conversation_new)
        else:
            pass
    except Exception as e:
        print(e)
