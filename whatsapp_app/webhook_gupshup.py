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


class WebhookGupshupView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.redis_stream = RedisStreams()
        return super(WebhookGupshupView, self).dispatch(request, *args, **kwargs)

    def get(self, request, identificador):
        print("get", identificador, request.body)
        return HttpResponse("OK", status=status.HTTP_200_OK)

    def post(self, request, identificador):
        stream_name = 'whatsapp_webhook_gupshup_{}'.format(identificador)
        self.redis_stream.write_stream(stream_name, request.body, max_stream_length=100000)
        return HttpResponse(status=status.HTTP_200_OK)
