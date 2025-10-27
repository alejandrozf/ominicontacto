# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
import requests
import json
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from orquestador_app.core.apis_urls import (
    URL_SEND_TEMPLATE, URL_SEND_MESSAGE, META_URL_SEND_MESSAGE, URL_SYNC_TEMPLATES,
    META_SYNC_TEMPLATES
)
from whatsapp_app.models import MensajeWhatsapp, ConfiguracionProveedor


headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}


def send_text_message(line, destination, message):
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        response = meta_send_text_message(line, destination, message)
        if response.status_code == 200:
            return response.json()['messages'][0]['id']
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        response = gupshup_send_text_message(line, destination, message).json()
        if response['status'] == "submitted":
            return response['messageId']
    return None


def autoresponse_welcome(line, conversation, timestamp):
    try:
        message = line.mensaje_bienvenida.configuracion
        if message:
            message_id = send_text_message(line, conversation.destination, message)
            if message_id:
                MensajeWhatsapp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': line.numero,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "text"
                    }
                )
    except Exception as e:
        print("autoresponse_welcome >>>>>>>>", e)


def autoreponse_destino_interactivo(line, destino, conversation):
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        meta_autoreponse_destino_interactivo(line, destino, conversation)
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        gupshup_autoreponse_destino_interactivo(line, destino, conversation)


def gupshup_autoreponse_destino_interactivo(line, destino, conversation):
    try:
        destination_entrante = destino
        menu_header = destination_entrante.content_object.menu_header
        menu_body = destination_entrante.content_object.menu_body
        menu_footer = destination_entrante.content_object.menu_footer
        menu_button = destination_entrante.content_object.menu_button
        message = {
            'type': 'list',
            'title': _(menu_header),
            'body': _(menu_body),
            'footer': _(menu_footer),
            'globalButtons': [{'type': 'text', 'title': _(menu_button)}],
            'items': [{
                'title': _(menu_button), 'subtitle': _(menu_button),
                'options': [
                    {
                        'type': 'text',
                        'title': opt.opcion_menu_whatsapp.opcion.valor,
                        'description': opt.opcion_menu_whatsapp.descripcion}
                    for opt in destination_entrante.destinos_siguientes.all()
                ]
            }]
        }
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            'channel': 'whatsapp',
            'source': line.numero,
            'src.name': line.configuracion['app_name'],
            'destination': conversation.destination,
            'message': json.dumps(message, default=str)
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data).json()
        if response['status'] == 'submitted':
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            content = {"text": json.dumps(message, default=str), 'type': 'list'},
            MensajeWhatsapp.objects.get_or_create(
                message_id=response['messageId'],
                conversation=conversation,
                defaults={
                    'origen': line.numero,
                    'timestamp': timestamp,
                    'sender': {'destino_entrante': destination_entrante.id},
                    'content': content,
                    'type': 'list-gupshup',
                }
            )
    except Exception as e:
        print("autoreponse_destino_interactivo >>>>>>>>>>>>", e)


def meta_autoreponse_destino_interactivo(line, destino, conversation):
    try:
        headers = {
            "accept": "application/json",
            # "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + line.proveedor.configuracion['access_token']
        }
        destination_entrante = destino
        menu_header = destination_entrante.content_object.menu_header
        menu_body = destination_entrante.content_object.menu_body
        menu_footer = destination_entrante.content_object.menu_footer
        menu_button = destination_entrante.content_object.menu_button
        message = {
            'type': 'list',
            'header': {
                "type": "text",
                "text": _(menu_header)
            },
            'body': {
                "text": _(menu_body)
            },
            'footer': {
                "text": _(menu_footer)
            },
            'action': {
                'button': _(menu_button),
                'sections': [{
                    'title': _(menu_button),
                    'rows': [
                        {
                            'id': opt.opcion_menu_whatsapp.opcion.id,
                            'title': opt.opcion_menu_whatsapp.opcion.valor,
                            'description': opt.opcion_menu_whatsapp.descripcion
                        }
                        for opt in destination_entrante.destinos_siguientes.all()
                    ]
                }]}
        }

        data = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': conversation.destination,
            'type': 'interactive',
            'interactive': json.dumps(message, default=str)
        }
        response = requests.post(
            META_URL_SEND_MESSAGE.format(line.numero), headers=headers, data=data)
        if response.status_code == 200:
            message_id = response.json()['messages'][0]['id']
            timestamp = timezone.now().astimezone(timezone.get_current_timezone())
            content = {"text": json.dumps(message, default=str), 'type': 'list'},
            MensajeWhatsapp.objects.get_or_create(
                message_id=message_id,
                conversation=conversation,
                defaults={
                    'origen': line.numero,
                    'timestamp': timestamp,
                    'sender': {'destino_entrante': destination_entrante.id},
                    'content': content,
                    'type': 'list-meta',
                }
            )
    except Exception as e:
        print("autoreponse_destino_interactivo >>>>>>>>>>>>", e)


def autoresponse_goodbye(conversation):
    try:
        message = conversation.line.mensaje_despedida.configuracion
        timestamp = timezone.now().astimezone(timezone.get_current_timezone())
        if message:
            message_id = send_text_message(conversation.line, conversation.destination, message)
            if message_id:
                MensajeWhatsapp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': conversation.line.numero,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "text"
                    }
                )
    except Exception as e:
        print("autoresponse_goobye >>>>>>>>", e)


def autoresponse_out_of_time(line, conversation, timestamp):
    try:
        message = line.mensaje_fueradehora.configuracion
        if message:
            message_id = send_text_message(line, conversation.destination, message)
            if message_id:
                MensajeWhatsapp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': line.numero,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "text"
                    }
                )
    except Exception as e:
        print("autoresponse_out_of_time >>>>>>>>", e)


def send_template_message(line, destination, template, data):
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        response = meta_send_template_message(line, destination, template, data)
        if response.status_code == 200:
            return response.json()['messages'][0]['id']
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        response = gupshup_send_template_message(line, destination, template, data).json()
        if response['status'] == "submitted":
            return response['messageId']
    return None


def gupshup_send_template_message(line, destination, template, data):
    try:
        headers = {
            "accept": "application/json",
            # "Content-Type": "application/x-www-form-urlencoded",
            "apikey": line.proveedor.configuracion['api_key']
        }
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template.identificador, "params": data["params"]})
        }
        if template.tipo == 'IMAGE':
            message = json.dumps({'image': {'link': template.link_media}, 'type': 'IMAGE'})
            data.update({"message": message})
        elif template.tipo == 'DOCUMENT':
            message = json.dumps({'document': {'link': template.link_media}, 'type': 'DOCUMENT'})
            data.update({"message": message})
        elif template.tipo == 'VIDEO':
            message = json.dumps({'video': {'link': template.link_media}, 'type': 'video'})
            data.update({"message": message})
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data)
        print(response.json())
        return response
    except Exception as e:
        print("error en send_template_message >>>>>>>", e)


def meta_send_template_message(line, destination, template, data):
    try:
        headers = {
            "accept": "application/json",
            "Authorization": 'Bearer ' + line.proveedor.configuracion['access_token']
        }
        header_parameters = []
        if template.tipo == 'TEXT':
            for param in data["params_header"]:
                header_parameters.append({
                    "type": template.tipo.lower(),
                    "text": param
                })
        elif template.tipo in ('IMAGE', 'VIDEO', 'DOCUMENT'):
            header_parameters.append({
                "type": template.tipo.lower(),
                template.tipo.lower(): json.dumps({'link': template.link_media})
            })
        else:
            raise NotImplementedError()

        body_parameters = []
        for param in data["params"]:
            body_parameters.append({
                "type": "text",
                "text": param
            })
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destination,
            "type": "template",
            "template": json.dumps({
                "name": template.nombre,
                "language": {
                    "code": template.idioma
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": header_parameters
                    },
                    {
                        "type": "body",
                        "parameters": body_parameters
                    },
                ]
            })
        }
        response = requests.post(
            META_URL_SEND_MESSAGE.format(line.numero), headers=headers, data=payload)
        return response
    except Exception as e:
        print("send_text_message >>>>>>", e)


def gupshup_send_text_message(line, destination, message):
    try:
        headers = {
            "accept": "application/json",
            "apikey": line.proveedor.configuracion['api_key']
        }
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": message['text']
        }
        print("headers>>", headers)
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
        return response
    except Exception as e:
        print("send_text_message >>>>>>", e)


def meta_send_text_message(line, destination, message):
    try:
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + line.proveedor.configuracion['access_token']
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destination,
            "type": "text",
            "text": json.dumps({
                "preview_url": False,
                "body": message['text']
            })
        }
        response = requests.post(
            META_URL_SEND_MESSAGE.format(line.numero), headers=headers, data=data)
        return response
    except Exception as e:
        print("meta_send_text_message >>>>>>", e)


def send_multimedia_file(line, destination, message):
    if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
        response = meta_send_multimedia_file_message(line, destination, message)
        if response.status_code == 200:
            return response.json()['messages'][0]['id']
    elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
        response = gupshup_send_multimedia_file_message(line, destination, message)
        if response['status'] == "submitted":
            return response['messageId']
    return None


def gupshup_send_multimedia_file_message(line, destination, message):
    try:
        headers = {
            "accept": "application/json",
            # "Content-Type": "application/x-www-form-urlencoded",
            "apikey": line.proveedor.configuracion['api_key']
        }
        data = {
            "channel": "whatsapp",
            "source": line.numero,
            "src.name": line.configuracion['app_name'],
            "destination": destination,
            "message": json.dumps(message)
        }
        response = requests.post(URL_SEND_MESSAGE, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print("send_text_message >>>>>>", e)


def meta_send_multimedia_file_message(line, destination, message):
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            'Authorization': 'Bearer ' + line.proveedor.configuracion['access_token']
        }
        media_type = message['type'] if message['type'] != 'file' else 'document'
        link = message['previewUrl'] if 'previewUrl' in message else ''
        caption = message['filename'] if 'filename' in message else ''
        data = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destination,
            "type": media_type,
            media_type: json.dumps({
                "link": link,
                "caption": caption
            })
        })
        response = requests.post(
            META_URL_SEND_MESSAGE.format(line.numero), headers=headers, data=data)
        return response
    except Exception as e:
        print("meta_send_multimedia_file_message >>>>>>", e)


def sync_templates(line):
    try:
        if line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_META:
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + line.proveedor.configuracion['access_token']
            }
            waba_id = line.configuracion['waba_id']
            url = META_SYNC_TEMPLATES.format(waba_id)

            response = requests.get(url, headers=headers)
            templates = response.json()['data']
            return templates
        elif line.proveedor.tipo_proveedor == ConfiguracionProveedor.TIPO_GUPSHUP:
            headers = {
                "accept": "application/json",
                "apikey": line.proveedor.configuracion['api_key']
            }
            app_id = line.configuracion['app_id']
            url = URL_SYNC_TEMPLATES.format(app_id)
            response = requests.get(url, headers=headers)
            templates = json.loads(response.text)['templates']
            return templates
        return []
    except Exception as e:
        print(">>>>>", e)
