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
from .apis_urls import META_URL_SEND_MESSAGE
from facebook_meta_app.models import MessageMessengerMetaApp


def autoresponse_welcome(conversation, timestamp):
    try:
        message = conversation.page.welcome_message.configuracion
        if message:
            message_id = send_text_message(conversation.page, conversation.page_client_id, message)
            if message_id:
                MessageMessengerMetaApp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': conversation.page.page_id,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "message"
                    }
                )
    except Exception as e:
        print("autoresponse_welcome >>>>>>>>", e)


def autoresponse_goodbye(conversation, timestamp):
    try:
        message = conversation.page.goodbye_message.configuracion
        if message:
            message_id = send_text_message(conversation.page, conversation.page_client_id, message)
            if message_id:
                MessageMessengerMetaApp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': conversation.page.page_id,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "message"
                    }
                )
    except Exception as e:
        print("autoresponse_goodbye >>>>>>>>", e)


def autoresponse_out_of_time(conversation, timestamp):
    try:
        message = conversation.page.out_of_time_message.configuracion
        if message:
            message_id = send_text_message(conversation.page, conversation.page_client_id, message)
            if message_id:
                MessageMessengerMetaApp.objects.get_or_create(
                    message_id=message_id,
                    conversation=conversation,
                    defaults={
                        'origen': conversation.page.page_id,
                        'timestamp': timestamp,
                        'sender': {},
                        'content': message,
                        'type': "text"
                    }
                )
    except Exception as e:
        print("autoresponse_out_of_time >>>>>>>>", e)


def autoreponse_destino_interactivo(destination_entrante, conversation, timestamp):
    try:
        menu_header = destination_entrante.content_object.menu_header
        text = menu_header
        buttons = []
        for opt in destination_entrante.destinos_siguientes.all():
            button = {
                "content_type": "text",
                "title": opt.opcion_menu_messenger_meta_app.opcion.valor,
                "payload": opt.opcion_menu_messenger_meta_app.descripcion
            }

            # Agrega URL o payload según corresponda
            # if opcion.url:
            #     button["url"] = opcion.valor
            # if opcion.payload:
            #     button["payload"] = opcion.valor
            buttons.append(button)

        page = conversation.page
        message_id = send_quick_reply(page, conversation.page_client_id, text, buttons)
        if message_id:
            message = {
                'text': text,
                'buttons': buttons
            }
            content = {"text": json.dumps(message, default=str), 'type': 'list'},
            MessageMessengerMetaApp.objects.get_or_create(
                message_id=message_id,
                conversation=conversation,
                defaults={
                    'origen': page.numero,
                    'timestamp': timestamp,
                    'sender': {'destino_entrante': destination_entrante.id},
                    'content': content,
                    'type': 'list-meta',
                }
            )
    except Exception as e:
        print("autoreponse_destino_interactivo >>>>>>>>>>>>", e)


def send_text_message(page, recipient_id, message_text):
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text["text"]},
    }
    params = {"access_token": page_access_token}
    response = requests.post(url, headers=headers, params=params, json=payload)
    if response.status_code == 200:
        return response.json()['message_id']
    return None


def send_quick_reply(page, recipient_id, text, quick_replies):
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {
            "text": text,
            "quick_replies": quick_replies
        },
    }
    params = {"access_token": page_access_token}
    response = requests.post(url, headers=headers, params=params, json=payload)
    if response.status_code == 200:
        return response.json()['message_id']
    return None


def send_button_template(page, recipient_id, text, buttons):
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        },
    }
    params = {"access_token": page_access_token}
    response = requests.post(url, headers=headers, params=params, json=payload)
    print("send_button_template response >>>>", response.text)
    if response.status_code == 200:
        return response.json()['message_id']
    return None


def send_generic_template(page, recipient_id, elements):
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        },
    }
    params = {"access_token": page_access_token}
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()


def send_media_message(page, recipient_id, type, media_url):
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": type,
                "payload": {
                    "url": media_url,
                    "is_reusable": True
                }
            }
        },
    }
    params = {"access_token": page_access_token}
    response = requests.post(url, headers=headers, params=params, json=payload)
    if response.status_code == 200:
        return response.json()['message_id']
    return None
