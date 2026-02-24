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
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ominicontacto_app.services.redis.redis_streams import RedisStreams

from facebook_meta_app.models import PaginaMetaFacebook


class WebhookFacebookMessengerView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.redis_stream = RedisStreams()
        return super(WebhookFacebookMessengerView, self).dispatch(request, *args, **kwargs)

    def get(self, request, app_id):
        try:
            mode = request.GET.get("hub.mode", None)
            token = request.GET.get("hub.verify_token", None)
            challenge = request.GET.get("hub.challenge", None)
            if token:
                pagina = PaginaMetaFacebook.objects.filter(app_id=app_id).first()
                if mode and pagina:
                    if mode == "subscribe" and\
                       token == pagina.verify_token:
                        return HttpResponse(challenge, status=status.HTTP_200_OK)
                return HttpResponse(challenge, status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(challenge, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error en webhook facebook messenger: {}".format(e))
            return HttpResponse(challenge, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, app_id):
        stream_name = 'facebook_meta_webhook_page_{}'.format(app_id)
        self.redis_stream.write_stream(stream_name, request.body, max_stream_length=100000)
        return HttpResponse(status=status.HTTP_200_OK)
