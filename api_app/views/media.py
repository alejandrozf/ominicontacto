# -*- coding: utf-8 -*-

import logging
import mimetypes
import os

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.utils._os import safe_join
from django.views import View

from api_app.services.media_url import (
    WHATSAPP_MEDIA_PREFIX,
    _build_media_path,
    validate_whatsapp_media_signature,
)
from whatsapp_app.models import MensajeWhatsapp

logger = logging.getLogger(__name__)


def requires_signed_whatsapp_media(path):
    relative_path = '{}{}'.format(WHATSAPP_MEDIA_PREFIX, path)
    return MensajeWhatsapp.objects.filter(file=relative_path).exists()


class SignedWhatsappMediaView(View):
    def get(self, request, path):
        media_path = _build_media_path('{}{}'.format(WHATSAPP_MEDIA_PREFIX, path))
        if requires_signed_whatsapp_media(path):
            is_valid, validation_details = validate_whatsapp_media_signature(
                request, media_path
            )
            if not is_valid:
                logger.warning(
                    'Signed WhatsApp media request rejected: '
                    'reason=%s path=%s expires=%s has_signature=%s '
                    'client_ip=%s request_path=%s',
                    validation_details.get('reason'),
                    validation_details.get('media_path'),
                    validation_details.get('expires'),
                    validation_details.get('has_signature'),
                    request.META.get('REMOTE_ADDR'),
                    request.path,
                )
                return HttpResponseForbidden()

        absolute_path = safe_join(settings.MEDIA_ROOT, WHATSAPP_MEDIA_PREFIX, path)
        if (
            not absolute_path or
            not os.path.exists(absolute_path) or
            not os.path.isfile(absolute_path)
        ):
            raise Http404()

        content_type, encoding = mimetypes.guess_type(absolute_path)
        response = FileResponse(open(absolute_path, 'rb'), content_type=content_type)
        if encoding:
            response['Content-Encoding'] = encoding
        return response
