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

import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from whatsapp_app.models import Linea


class WebhookMetaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, identificador):
        print("get")
        try:
            mode = request.GET.get("hub.mode", None)
            token = request.GET.get("hub.verify_token", None)
            challenge = request.GET.get("hub.challenge", None)
            # Check if a token and mode were sent
            print(token)
            if token:
                line_token = Linea.objects.filter(
                    identificador=identificador).first().token_validacion
                if mode and token == token:
                    # Check the mode and token sent are correct
                    if mode == "subscribe" and token == line_token:
                        return HttpResponse(challenge, status=status.HTTP_200_OK)
                return HttpResponse(challenge, status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(challenge, status=status.HTTP_200_OK)

        except Exception:
            return HttpResponse(challenge, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, identificador):
        if request.body:
            body = json.loads(request.body)
            identificador = Linea.objects.get(identificador=identificador).proveedor.identificador
            if body["entry"][0]["id"] == identificador or True:
                if body["entry"][0]["changes"][0]['field'] == 'messages':
                    messages(body["entry"][0]["changes"][0]['value'])
                if body["entry"][0]["changes"][0]['field'] == 'message_template_status_update':
                    message_template_status_update(body["entry"][0]["changes"][0]['value'])
            return HttpResponse("OK", status=status.HTTP_200_OK)
        return HttpResponse("OK", status=status.HTTP_403_FORBIDDEN)


def messages(value):
    if 'contacts' in value and 'messages' in value:
        print('From: ', value['contacts'][0], 'messages: ', value['messages'][0]['text']['body'])
    if 'statuses' in value:
        print(
            'recipient_id: ', value['statuses'][0]['recipient_id'],
            'status: ', value['statuses'][0]['status']
        )


def message_template_status_update(value):
    print('template_id:', value['message_template_id'], 'status', value['event'])
