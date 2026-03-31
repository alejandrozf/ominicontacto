# -*- coding: utf-8 -*-

from django.test import RequestFactory, SimpleTestCase
from django.test.utils import override_settings

from api_app.services.media_url import build_public_media_url


class MediaUrlServiceTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(OML_PUBLIC_MEDIA_BASE_URL='https://omlwh.sanatorioallende.com')
    def test_build_public_media_url_uses_configured_public_base_url(self):
        request = self.factory.get('/', HTTP_HOST='oml.sanatorioallende.com')

        media_url = build_public_media_url(
            request, '/media/archivos_whatsapp/archivo.pdf')

        self.assertEqual(
            media_url,
            'https://omlwh.sanatorioallende.com/media/archivos_whatsapp/archivo.pdf'
        )

    @override_settings(OML_PUBLIC_MEDIA_BASE_URL=None)
    def test_build_public_media_url_falls_back_to_request_host(self):
        request = self.factory.get('/', HTTP_HOST='oml.sanatorioallende.com')

        media_url = build_public_media_url(
            request, '/media/archivos_whatsapp/archivo.pdf')

        self.assertEqual(
            media_url,
            'http://oml.sanatorioallende.com/media/archivos_whatsapp/archivo.pdf'
        )
