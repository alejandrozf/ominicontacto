import requests
import json
from django.utils import timezone
from orquestador_app.core.apis_urls import URL_SEND_TEMPLATE, URL_SEND_MESSAGE, URL_SYNC_TEMPLATES
from whatsapp_app.models import MensajeWhatsapp

headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}


def autoresponse_out_of_time(line, destination, sender):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        template_id = "a7da0ec0-5861-43f5-82f5-03311df7f00f"
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template_id, "params": [sender['name']]})
        }
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data).json()
        print("===> send_template_message")
        print("response", response)
        if response["status"] == "submitted":
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            # text = template.texto.replace('{{', '{').\
            #     replace('}}', '}').format("", *data['params'])
            MensajeWhatsapp.objects.create(
                message_id=response['messageId'],
                origen=line.numero,
                timestamp=timestamp,
                sender={},
                content={"text": "text", "type": "template"},
                type="template",
            )
        return response
    except Exception as e:
        print(e)


def autoresponse_welcome(line, destination, sender):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        template_id = "a7da0ec0-5861-43f5-82f5-03311df7f00f"
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template_id, "params": [sender['name']]})
        }
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data).json()
        print("===> send_template_message")
        print("response", response)
        if response["status"] == "submitted":
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            # text = template.texto.replace('{{', '{').\
            #     replace('}}', '}').format("", *data['params'])
            MensajeWhatsapp.objects.create(
                message_id=response['messageId'],
                origen=line.numero,
                timestamp=timestamp,
                sender={},
                content={"text": "text", "type": "template"},
                type="template",
            )
        return response
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


def handler_autoresponses(line, destination, sender, conversation):
    if False:  # validar horario
        autoresponse_out_of_time(line, destination)
    elif not conversation:
        autoresponse_welcome(line, destination, sender)
    # elif conversation_expired:
    #     autoresponse_goodbye(line, destination)


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
