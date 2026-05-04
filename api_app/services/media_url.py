# -*- coding: utf-8 -*-

import time
from copy import deepcopy
from urllib.parse import urlencode, urljoin, urlparse

from django.conf import settings
from django.core import signing


WHATSAPP_MEDIA_PREFIX = 'archivos_whatsapp/'
WHATSAPP_MEDIA_SIGNATURE_SALT = 'whatsapp-media-url'


def _get_base_url(request=None):
    if getattr(settings, 'OML_PUBLIC_MEDIA_BASE_URL', None):
        return settings.OML_PUBLIC_MEDIA_BASE_URL
    if request is not None:
        return request.build_absolute_uri('/')[:-1]
    return None


def _build_media_path(relative_path):
    media_root = settings.MEDIA_URL.rstrip('/') + '/'
    return media_root + relative_path.lstrip('/')


def get_canonical_media_reference(media_path):
    if not isinstance(media_path, str) or not media_path:
        return media_path

    parsed = urlparse(media_path)
    candidate_path = parsed.path if parsed.scheme or parsed.netloc else media_path
    return '/' + candidate_path.lstrip('/')


def _sign_media_path(media_path, expires_at):
    payload = '{}:{}'.format(media_path, expires_at)
    signed_payload = signing.Signer(salt=WHATSAPP_MEDIA_SIGNATURE_SALT).sign(payload)
    return signed_payload.rsplit(':', 1)[1]


def build_public_media_url(request, media_path):
    canonical_reference = get_canonical_media_reference(media_path)
    if not isinstance(canonical_reference, str) or not canonical_reference:
        return canonical_reference

    parsed = urlparse(canonical_reference)
    if parsed.scheme or parsed.netloc:
        return canonical_reference

    base_url = _get_base_url(request)
    if not base_url:
        return canonical_reference
    return urljoin(base_url.rstrip('/') + '/', canonical_reference.lstrip('/'))


def build_signed_whatsapp_attachment_url(request, media_path):
    canonical_reference = get_canonical_media_reference(media_path)
    expires_in = getattr(settings, 'OML_SIGNED_MEDIA_URL_EXPIRE_SECONDS', 900)
    expires_at = int(time.time()) + int(expires_in)
    signature = _sign_media_path(canonical_reference, expires_at)
    query = urlencode({
        'expires': expires_at,
        'signature': signature,
    })
    path_with_signature = '{}?{}'.format(canonical_reference, query)
    base_url = _get_base_url(request)
    if not base_url:
        return path_with_signature
    return urljoin(base_url.rstrip('/') + '/', path_with_signature.lstrip('/'))


def sign_outbound_whatsapp_attachment_content(content, media_path, request=None):
    if not isinstance(content, dict):
        return content
    signed_content = deepcopy(content)
    signed_url = build_signed_whatsapp_attachment_url(request, media_path)
    for key in ('previewUrl', 'originalUrl', 'url'):
        if key in signed_content:
            signed_content[key] = signed_url
    return signed_content


def validate_whatsapp_media_signature(request, media_path):
    canonical_reference = get_canonical_media_reference(media_path)

    expires = request.GET.get('expires')
    signature = request.GET.get('signature')
    if not expires or not signature:
        return False, {
            'reason': 'missing_signature_params',
            'media_path': canonical_reference,
            'expires': expires,
            'has_signature': bool(signature),
        }

    try:
        expires = int(expires)
    except (TypeError, ValueError):
        return False, {
            'reason': 'invalid_expires',
            'media_path': canonical_reference,
            'expires': request.GET.get('expires'),
            'has_signature': True,
        }

    if time.time() > expires:
        return False, {
            'reason': 'expired',
            'media_path': canonical_reference,
            'expires': expires,
            'has_signature': True,
        }

    payload = '{}:{}'.format(canonical_reference, expires)
    signed_payload = '{}:{}'.format(payload, signature)
    try:
        signing.Signer(salt=WHATSAPP_MEDIA_SIGNATURE_SALT).unsign(signed_payload)
    except signing.BadSignature:
        return False, {
            'reason': 'bad_signature',
            'media_path': canonical_reference,
            'expires': expires,
            'has_signature': True,
        }
    return True, {
        'reason': 'valid',
        'media_path': canonical_reference,
        'expires': expires,
        'has_signature': True,
    }
