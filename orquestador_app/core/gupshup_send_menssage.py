import requests
import json
from orquestador_app.core.apis_urls import URL_SEND_TEMPLATE, URL_SEND_MESSAGE, URL_SYNC_TEMPLATES


headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}


def autoresponse_out_of_time(line, destination):
    # validar fuera de horario
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": json.dumps(line.mensaje_fueradehora.configuracion)
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
        return response
    except Exception as e:
        print(e)


def autoresponse_welcome(line, destination):
    try:
        print("mensaje_bienvenida", line.id, line.mensaje_bienvenida)
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": json.dumps(line.mensaje_bienvenida.configuracion)
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
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


def handler_autoresponses(line, destination, conversation_new):
    if False:  # validar horario
        autoresponse_out_of_time(line, destination)
    elif conversation_new:
        autoresponse_welcome(line, destination)
    # elif conversation_expired:
    #     autoresponse_goodbye(line, destination)


def sync_templates(line):
    try:
        appname = line.configuracion['app_name']
        url = URL_SYNC_TEMPLATES.format(appname)  # mover
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        response = requests.get(url, headers=headers)
        templates = json.loads(response.text)['templates']
        for t in templates:
            print("---", t['data'])
        return templates
    except Exception as e:
        print(e)
