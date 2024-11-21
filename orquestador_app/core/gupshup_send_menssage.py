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
    URL_SEND_TEMPLATE, URL_SEND_MESSAGE, URL_SYNC_TEMPLATES)
from whatsapp_app.models import MensajeWhatsapp


headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}


def autoresponse_welcome(line, conversation, timestamp):
    try:
        message = line.mensaje_bienvenida.configuracion
        if message:
            response = send_text_message(line, conversation.destination, message)
            if response['status'] == "submitted":
                MensajeWhatsapp.objects.get_or_create(
                    message_id=response['messageId'],
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
                    {'type': 'text',
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
                    'type': 'list',
                }
            )
    except Exception as e:
        print("autoreponse_destino_interactivo >>>>>>>>>>>>", e)


def autoresponse_goodbye(conversation):
    try:
        message = conversation.line.mensaje_despedida.configuracion
        timestamp = timezone.now().astimezone(timezone.get_current_timezone())
        if message:
            response = send_text_message(conversation.line, conversation.destination, message)
            if response['status'] == "submitted":
                MensajeWhatsapp.objects.get_or_create(
                    message_id=response['messageId'],
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
            response = send_text_message(line, conversation.destination, message)
            if response['status'] == "submitted":
                MensajeWhatsapp.objects.get_or_create(
                    message_id=response['messageId'],
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


def send_template_message(line, destination, template_id, template_tipo, params, media_id=None):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        data = {
            'source': line.numero,
            'destination': destination,
            'template': json.dumps({"id": template_id, "params": params})
        }
        if template_tipo == 'IMAGE':
            message = json.dumps({'image': {'id': media_id}, 'type': template_tipo})
            data.update({"message": message})
        elif template_tipo == 'DOCUMENT':
            message = json.dumps({'document': {'id': media_id, 'link': ''}, 'type': template_tipo})
            data.update({"message": message})
        elif template_tipo == 'VIDEO':
            message = json.dumps({'video': {'id': media_id, 'link': ''}, 'type': template_tipo})
            data.update({"message": message})
        response = requests.post(URL_SEND_TEMPLATE, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print("error en send_template_message >>>>>>>", e)


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
        print("send_text_message >>>>>>", e)


def send_multimedia_file(line, destination, message):
    try:
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
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


def sync_templates(line):
    try:
        app_id = line.configuracion['app_id']
        url = URL_SYNC_TEMPLATES.format(app_id)
        headers.update({'apikey': line.proveedor.configuracion['api_key']})
        response = requests.get(url, headers=headers)
        templates = json.loads(response.text)['templates']
        return templates
    except Exception as e:
        print(e)
