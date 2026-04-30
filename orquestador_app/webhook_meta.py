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
import hashlib
import hmac
import logging

from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ominicontacto_app.services.redis.redis_streams import RedisStreams

from whatsapp_app.models import Linea, ConfiguracionProveedor

logger = logging.getLogger(__name__)


class WebhookMetaView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.redis_stream = RedisStreams()
        return super(WebhookMetaView, self).dispatch(request, *args, **kwargs)

    def _get_linea(self, app_id):
        return Linea.objects.filter(
            proveedor__tipo_proveedor=ConfiguracionProveedor.TIPO_META,
            configuracion__contains={'app_id': app_id}
        ).first()

    def _verify_signature(self, request, linea):
        """
        Verifica la firma HMAC-SHA256 enviada por Meta en el header X-Hub-Signature-256.
        Retorna True si la firma es válida o si no hay app_secret configurado (backward compat).
        Retorna False si el header existe pero la firma no coincide.
        """
        app_secret = linea.configuracion.get('app_secret', '')
        if not app_secret:
            return True  # backward-compatible: sin secret configurado se permite

        signature_header = request.headers.get('X-Hub-Signature-256', '')
        if not signature_header:
            logger.warning(
                "Webhook Meta (app_id=%s): request sin header X-Hub-Signature-256.",
                linea.configuracion.get('app_id')
            )
            return False

        expected = 'sha256=' + hmac.new(
            app_secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature_header, expected):
            logger.warning(
                "Webhook Meta (app_id=%s): firma HMAC invalida. "
                "Posible solicitud no autorizada.",
                linea.configuracion.get('app_id')
            )
            return False

        return True

    def get(self, request, app_id):
        try:
            mode = request.GET.get("hub.mode", None)
            token = request.GET.get("hub.verify_token", None)
            challenge = request.GET.get("hub.challenge", None)
            if token:
                line_token = self._get_linea(app_id)
                if mode and line_token:
                    if mode == "subscribe" and \
                       token == line_token.configuracion['verification_token']:
                        return HttpResponse(challenge, status=status.HTTP_200_OK)
                return HttpResponse(challenge, status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(challenge, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error en verificacion GET webhook Meta: %s", e)
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, app_id):
        linea = self._get_linea(app_id)
        if linea is None:
            logger.warning("Webhook Meta: no se encontro Linea para app_id=%s", app_id)
            return HttpResponse(status=status.HTTP_200_OK)

        if not self._verify_signature(request, linea):
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        stream_name = 'whatsapp_webhook_meta_{}'.format(app_id)
        self.redis_stream.write_stream(
            stream_name,
            request.body,
            max_stream_length=settings.WHATSAPP_WEBHOOK_STREAM_MAXLEN,
        )
        return HttpResponse(status=status.HTTP_200_OK)
