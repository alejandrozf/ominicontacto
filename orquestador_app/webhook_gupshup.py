# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3,
# as published by the Free Software Foundation.

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
from whatsapp_app.models import Linea, ConfiguracionProveedor
from ominicontacto_app.services.redis.redis_streams import RedisStreams

logger = logging.getLogger(__name__)


class WebhookGupshupView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.redis_stream = RedisStreams()
        return super(
            WebhookGupshupView, self
        ).dispatch(request, *args, **kwargs)

    def _get_linea(self, identificador):
        return Linea.objects.filter(
            proveedor__tipo_proveedor=ConfiguracionProveedor.TIPO_GUPSHUP,
            configuracion__contains={
                'app_id': identificador
            }
        ).first()

    def _verify_signature(self, request, linea):
        """
        Gupshup puede firmar webhooks con el header 'X-Gupshup-Signature'.
        Si la linea tiene configurado 'app_secret' se valida esa firma.
        Se mantiene compatibilidad hacia atras con 'webhook_secret'
        para configuraciones previas. Si no hay secreto configurado,
        se permite el request (se recomienda complementar con
        IP whitelisting de los rangos de Gupshup).
        """
        webhook_secret = ''
        if linea:
            webhook_secret = (
                linea.configuracion.get('app_secret')
                or linea.configuracion.get('webhook_secret')
                or ''
            )
        if not webhook_secret:
            return True

        signature_header = request.headers.get('X-Gupshup-Signature', '')
        if not signature_header:
            logger.warning(
                "Webhook Gupshup (app_id=%s): request sin header "
                "X-Gupshup-Signature.",
                linea.configuracion.get('app_id') if linea else 'desconocido'
            )
            return False

        expected = hmac.new(
            webhook_secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature_header, expected):
            logger.warning(
                "Webhook Gupshup (app_id=%s): firma invalida. "
                "Posible solicitud no autorizada.",
                linea.configuracion.get('app_id') if linea else 'desconocido'
            )
            return False

        return True

    def get(self, request, identificador):
        return HttpResponse("OK", status=status.HTTP_200_OK)

    def post(self, request, identificador):
        linea = self._get_linea(identificador)
        if not self._verify_signature(request, linea):
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        stream_name = 'whatsapp_webhook_gupshup_{}'.format(
            identificador
        )
        self.redis_stream.write_stream(
            stream_name,
            request.body,
            max_stream_length=settings.WHATSAPP_WEBHOOK_STREAM_MAXLEN,
        )
        return HttpResponse(status=status.HTTP_200_OK)
