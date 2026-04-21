# -*- coding: utf-8 -*-

import os
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.test import RequestFactory, SimpleTestCase
from django.test.utils import override_settings

from api_app.services.media_url import (
    build_public_media_url,
    build_signed_whatsapp_attachment_url,
    sign_outbound_whatsapp_attachment_content,
    validate_whatsapp_media_signature,
)
from api_app.views.media import SignedWhatsappMediaView


class MediaUrlServiceTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(OML_PUBLIC_MEDIA_BASE_URL='https://media.example.test')
    def test_build_public_media_url_uses_configured_public_base_url(self):
        request = self.factory.get('/', HTTP_HOST='app.example.test')

        media_url = build_public_media_url(
            request, '/media/archivos_whatsapp/archivo.pdf')
        self.assertEqual(
            media_url,
            'https://media.example.test/media/archivos_whatsapp/archivo.pdf'
        )

    @override_settings(OML_PUBLIC_MEDIA_BASE_URL=None)
    def test_build_public_media_url_falls_back_to_request_host(self):
        request = self.factory.get('/', HTTP_HOST='app.example.test')

        media_url = build_public_media_url(
            request, '/media/archivos_whatsapp/archivo.pdf')
        self.assertEqual(
            media_url,
            'http://app.example.test/media/archivos_whatsapp/archivo.pdf'
        )

    def test_build_signed_whatsapp_attachment_url_adds_signature_and_expiration(self):
        request = self.factory.get('/', HTTP_HOST='app.example.test')
        media_url = build_signed_whatsapp_attachment_url(
            request, '/media/archivos_whatsapp/archivo.pdf'
        )
        parsed = urlparse(media_url)
        query = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, 'http')
        self.assertEqual(parsed.netloc, 'app.example.test')
        self.assertEqual(parsed.path, '/media/archivos_whatsapp/archivo.pdf')
        self.assertIn('expires', query)
        self.assertIn('signature', query)

    def test_sign_outbound_whatsapp_attachment_content_replaces_media_urls(self):
        request = self.factory.get('/', HTTP_HOST='app.example.test')
        content = sign_outbound_whatsapp_attachment_content({
            'previewUrl': 'https://old-public-host/media/archivos_whatsapp/archivo.pdf',
            'originalUrl': '/media/archivos_whatsapp/archivo.pdf',
            'url': '/media/archivos_whatsapp/archivo.pdf',
        }, '/media/archivos_whatsapp/archivo.pdf', request=request)

        self.assertTrue(content['previewUrl'].startswith(
            'http://app.example.test/media/archivos_whatsapp/archivo.pdf?'
        ))
        self.assertTrue(content['originalUrl'].startswith(
            'http://app.example.test/media/archivos_whatsapp/archivo.pdf?'
        ))
        self.assertTrue(content['url'].startswith(
            'http://app.example.test/media/archivos_whatsapp/archivo.pdf?'
        ))


class SignedWhatsappMediaViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_validate_whatsapp_media_signature_reports_expired_reason(self):
        with self.settings(OML_SIGNED_MEDIA_URL_EXPIRE_SECONDS=-1):
            signed_url = build_signed_whatsapp_attachment_url(
                None, '/media/archivos_whatsapp/archivo.txt'
            )
        parsed = urlparse(signed_url)
        request = self.factory.get('{}?{}'.format(parsed.path, parsed.query))

        is_valid, details = validate_whatsapp_media_signature(
            request, '/media/archivos_whatsapp/archivo.txt'
        )

        self.assertFalse(is_valid)
        self.assertEqual(details['reason'], 'expired')

    @patch('api_app.views.media.requires_signed_whatsapp_media', return_value=True)
    def test_signed_media_view_returns_file_when_signature_is_valid(self, _requires_signature):
        with TemporaryDirectory() as tempdir:
            whatsapp_dir = os.path.join(tempdir, 'archivos_whatsapp')
            os.makedirs(whatsapp_dir)
            absolute_path = os.path.join(whatsapp_dir, 'archivo.txt')
            with open(absolute_path, 'wb') as media_file:
                media_file.write(b'contenido')

            with self.settings(MEDIA_ROOT=tempdir, OML_PUBLIC_MEDIA_BASE_URL=None):
                signed_url = build_signed_whatsapp_attachment_url(
                    None, '/media/archivos_whatsapp/archivo.txt'
                )
                parsed = urlparse(signed_url)
                request = self.factory.get('{}?{}'.format(parsed.path, parsed.query))

                response = SignedWhatsappMediaView.as_view()(request, path='archivo.txt')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(b''.join(response.streaming_content), b'contenido')

    @patch('api_app.views.media.requires_signed_whatsapp_media', return_value=True)
    def test_signed_media_view_rejects_unsigned_requests(self, _requires_signature):
        with TemporaryDirectory() as tempdir:
            whatsapp_dir = os.path.join(tempdir, 'archivos_whatsapp')
            os.makedirs(whatsapp_dir)
            absolute_path = os.path.join(whatsapp_dir, 'archivo.txt')
            with open(absolute_path, 'wb') as media_file:
                media_file.write(b'contenido')

            with self.settings(MEDIA_ROOT=tempdir):
                request = self.factory.get('/media/archivos_whatsapp/archivo.txt')
                with self.assertLogs('api_app.views.media', level='WARNING') as logs:
                    response = SignedWhatsappMediaView.as_view()(request, path='archivo.txt')

            self.assertEqual(response.status_code, 403)
            self.assertIn('reason=missing_signature_params', logs.output[0])

    @patch('api_app.views.media.requires_signed_whatsapp_media', return_value=False)
    def test_unsigned_inbound_media_stays_accessible(self, _requires_signature):
        with TemporaryDirectory() as tempdir:
            whatsapp_dir = os.path.join(tempdir, 'archivos_whatsapp')
            os.makedirs(whatsapp_dir)
            absolute_path = os.path.join(whatsapp_dir, 'archivo.txt')
            with open(absolute_path, 'wb') as media_file:
                media_file.write(b'contenido')

            with self.settings(MEDIA_ROOT=tempdir):
                request = self.factory.get('/media/archivos_whatsapp/archivo.txt')
                response = SignedWhatsappMediaView.as_view()(request, path='archivo.txt')

            self.assertEqual(response.status_code, 200)
