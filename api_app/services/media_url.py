# -*- coding: utf-8 -*-

from urllib.parse import urljoin

from django.conf import settings


def build_public_media_url(request, media_path):
    base_url = getattr(settings, 'OML_PUBLIC_MEDIA_BASE_URL', None) or \
        request.build_absolute_uri('/')[:-1]
    return urljoin(base_url.rstrip('/') + '/', media_path.lstrip('/'))
