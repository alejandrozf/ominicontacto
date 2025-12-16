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
        message = conversation.page.out_of_hours_message.configuracion
        if message:
            message_id = send_text_message(conversation.page, conversation.page_client_id, message)
            print("autoresponse_out_of_time message_id >>>>>", message_id)
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
            MessageMessengerMetaApp.objects.get_or_create(
                message_id=message_id,
                conversation=conversation,
                defaults={
                    'origen': page.page_id,
                    'timestamp': timestamp,
                    'sender': {'destino_entrante': destination_entrante.id},
                    'content': message,
                    'type': 'list',
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


def upload_media_to_meta(page, type_file, file_path):
    """
    Sube un archivo a Messenger y devuelve attachment_id.
    """
    page_access_token = page.access_token
    page_id = page.page_id

    url = f"https://graph.facebook.com/v18.0/{page_id}/message_attachments"

    with open(file_path, "rb") as f:
        files = {
            "filedata": f
        }
        payload = {
            "message": json.dumps({
                "attachment": {
                    "type": type_file,
                    "payload": {"is_reusable": True}
                }
            })
        }

        response = requests.post(
            url,
            params={"access_token": page_access_token},
            data=payload,
            files=files
        )

    if response.ok:
        resp_json = response.json()
        attachment_id = resp_json.get("attachment_id")
        if attachment_id:
            return attachment_id
        else:
            raise Exception(f"No se obtuvo attachment_id: {resp_json}")
    else:
        raise Exception(f"Error al subir archivo a Meta: {response.status_code} {response.text}")


def send_media_message(page, recipient_id, type_file, attachment_id):
    """
    Envía un mensaje de media a Messenger usando attachment_id.
    """
    page_access_token = page.access_token
    page_id = page.page_id
    url = META_URL_SEND_MESSAGE.format(page_id)

    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": type_file,
                "payload": {
                    "attachment_id": attachment_id
                }
            }
        }
    }
    response = requests.post(url, params={"access_token": page_access_token}, json=payload)
    if response.ok:
        return response.json().get("message_id")
    else:
        raise Exception(f"Error enviando mensaje: {response.status_code} {response.text}")
