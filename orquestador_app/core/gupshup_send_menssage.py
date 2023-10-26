import requests
import json
from django.utils import timezone
from orquestador_app.core.apis_urls import (
    URL_SEND_TEMPLATE, URL_SEND_MESSAGE, URL_SYNC_TEMPLATES,
    URL_SEND_MENU_OPTION)
from whatsapp_app.models import MensajeWhatsapp


headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}


def autoresponse_out_of_time(line, destination, sender):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        template = line.mensaje_fueradehora
        params = [sender['name']]
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template.identificador, "params": [sender['name']]})
        }
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data).json()
        if response["status"] == "submitted":
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            text = template.texto.replace('{{', '{').replace('}}', '}').format("", *params)
            MensajeWhatsapp.objects.create(
                message_id=response['messageId'],
                origen=line.numero,
                timestamp=timestamp,
                sender={},
                content={"text": text, "type": "template"},
                type="template",
            )
        return response
    except Exception as e:
        print(e)


def autoresponse_welcome(line, conversation, sender):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        template = line.mensaje_bienvenida
        params = [sender['name']]
        data = {
            'source': line.numero,
            'destination': conversation.destination,
            'template': json.dumps({"id": template.identificador, "params": params})
        }
        message_outbound = None
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data).json()
        if response['status'] == "submitted":
            text = template.texto.replace('{{', '{').replace('}}', '}').format("", *params)
            content = {"text": text, "type": "template"},
            message_outbound = MensajeWhatsapp.objects.create(
                message_id=response['messageId'],
                conversation=conversation,
                origen=line.numero,
                sender={},
                content=content,
                type='template',
            )
        return message_outbound
    except Exception as e:
        print(">>>>>>>>", e)


def autoreponse_destino_interactivo(line, conversation, sender):
    try:
        message = {
            'type': 'list',
            'title': 'Seleccione un destino',
            'body': 'Click Main Menu',
            'globalButtons': [{'type': 'text', 'title': 'Main Menu'}],
            'items': [{
                'title': 'Destinos', 'subtitle': 'Seleccione un destino',
                'options': [
                    {'type': 'text', 'title': 'Book 1', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 2', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 3', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 4', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 5', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 6', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 7', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 8', 'description': 'Book description'},
                    {'type': 'text', 'title': 'Book 9', 'description': 'Book description'},
                ]
            }]
        }
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": conversation.destination,
            "message": json.dumps(message)
        }
        response = requests.post(URL_SEND_MENU_OPTION, headers=headers, data=data).json()
        message_outbound = None
        if response['status'] == "submitted":
            content = {"text": json.dumps(message), "type": "list"},
            message_outbound = MensajeWhatsapp.objects.create(
                message_id=response['messageId'],
                conversation=conversation,
                origen=line.numero,
                sender={},
                content=content,
                type='list',
            )
        return message_outbound
    except Exception as e:
        print(e)


def autoresponse_goodbye(line, destination):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": json.dumps(line.mensaje_despedida.configuracion)
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
        return response
    except Exception as e:
        print(e)


def send_template_message(line, destination, template_id, params):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        print("===> HEADERS send_template_message")
        print(headers)
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template_id, "params": params})
        }
        print("===> data send_template_message")
        print(data)
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data)
        print("===> response send_template_message")
        print(response.json())
        return response.json()
    except Exception as e:
        print(e)


def send_text_message(line, destination, message):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": message['text']
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print(e)


def is_out_of_time(line, timestamp):
    if line.horario:
        time = timestamp.time()
        weekday = timestamp.weekday()
        monthday = timestamp.day
        month = timestamp.month
        validaciones_tiempo = line.horario.validaciones_tiempo.all()

        for validacion in validaciones_tiempo:
            if validacion.tiempo_inicial and validacion.tiempo_inicial > time:
                return True
            if validacion.tiempo_final and validacion.tiempo_final < time:
                return True
            if validacion.dia_semana_inicial and validacion.dia_semana_inicial > weekday:
                return True
            if validacion.dia_semana_final and validacion.dia_semana_final < weekday:
                return True
            if validacion.dia_mes_inicio and validacion.dia_mes_inicio > monthday:
                return True
            if validacion.dia_mes_final and validacion.dia_mes_final < monthday:
                return True
            if validacion.mes_inicio and validacion.mes_inicio > month:
                return True
            if validacion.mes_final and validacion.mes_final < month:
                return True
    return False


def sync_templates(line):
    try:
        appname = line.configuracion['app_name']
        url = URL_SYNC_TEMPLATES.format(appname)  # mover
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        response = requests.get(url, headers=headers)
        templates = json.loads(response.text)['templates']
        return templates
    except Exception as e:
        print(e)
