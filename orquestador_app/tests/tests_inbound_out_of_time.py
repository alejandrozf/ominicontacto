# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from unittest.mock import patch

from django.test import TestCase
from asgiref.sync import async_to_sync
from django.utils.timezone import make_aware

from configuracion_telefonia_app.tests.factories import GrupoHorarioFactory, ValidacionTiempoFactory
from facebook_meta_app.models import ConversationMessengerMetaApp, PaginaMetaFacebook
from ominicontacto_app.tests.factories import CampanaFactory
from orquestador_app.core.facebook.inbound_chat_event_management import (
    s2a_inbound_chat_event as facebook_inbound_chat_event,
)
from orquestador_app.core.whatsapp.inbound_chat_event_management import (
    s2a_inbound_chat_event as whatsapp_inbound_chat_event,
)
from whatsapp_app.models import ConversacionWhatsapp
from whatsapp_app.tests.factories import DestinoEntranteFactory, LineaFactory


def _business_hours_schedule():
    grupo_horario = GrupoHorarioFactory()
    ValidacionTiempoFactory(
        grupo_horario=grupo_horario,
        tiempo_inicial=datetime.time(9, 0, 0),
        tiempo_final=datetime.time(18, 0, 0),
        dia_semana_inicial=1,
        dia_semana_final=1,
        dia_mes_inicio=None,
        dia_mes_final=None,
        mes_inicio=None,
        mes_final=None
    )
    return grupo_horario


class InboundOutOfTimeTest(TestCase):

    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.redis_2')
    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_welcome')
    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_out_of_time')
    def test_new_whatsapp_conversation_out_of_time_is_closed_by_system(
            self, autoresponse_out_of_time, autoresponse_welcome, redis_mock):
        line = LineaFactory(horario=_business_hours_schedule())
        timestamp = make_aware(datetime.datetime(2026, 4, 14, 18, 1, 0))
        # Paso parametros posicionales para q async_to_sync no tenga problemas con context
        # line, timestamp, message_id, origen, content, sender, context, type
        notifications = async_to_sync(whatsapp_inbound_chat_event)(
            line,  # line
            timestamp,  # timestamp
            'wa-out-of-time-1',  # message_id
            '5493512518376',  # origen
            {'text': 'hola'},  # content
            {'name': 'Cliente'},  # sender
            {},  # context
            'text',  # type
        )

        conversation = ConversacionWhatsapp.objects.get(
            whatsapp_id='5493512518376',
            line=line,
        )

        self.assertEqual(notifications, [])
        self.assertFalse(conversation.is_active)
        self.assertTrue(conversation.is_disposition)
        autoresponse_welcome.assert_not_called()
        autoresponse_out_of_time.assert_called_once_with(line, conversation, timestamp)
        redis_mock.sadd.assert_not_called()
        redis_mock.publish.assert_not_called()

    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.redis_2')
    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_out_of_time')
    def test_existing_whatsapp_conversation_started_within_business_hours_does_not_autorespond(
            self, autoresponse_out_of_time, redis_mock):
        line = LineaFactory(horario=_business_hours_schedule())
        conversation = ConversacionWhatsapp.objects.create(
            line=line,
            campana=line.destino.content_object,
            client=None,
            destination='5493517585765',
            whatsapp_id='5493517585765',
            is_active=False,
            expire=make_aware(datetime.datetime(2026, 4, 14, 18, 0, 0)),
            timestamp=make_aware(datetime.datetime(2026, 4, 14, 17, 59, 0)),
            date_last_interaction=make_aware(datetime.datetime(2026, 4, 14, 17, 59, 0)),
            client_alias='Cliente',
        )
        timestamp = make_aware(datetime.datetime(2026, 4, 14, 18, 2, 0))

        # Paso parametros posicionales para q async_to_sync no tenga problemas con context
        # line, timestamp, message_id, origen, content, sender, context, type
        async_to_sync(whatsapp_inbound_chat_event)(
            line,  # line
            timestamp,  # timestamp
            'wa-in-hours-1',  # message_id
            '5493517585765',  # origen
            {'text': 'sigo escribiendo'},  # content
            {'name': 'Cliente'},  # sender
            {},  # context
            'text',  # type
        )

        conversation.refresh_from_db()

        self.assertFalse(conversation.is_disposition)
        self.assertTrue(conversation.is_active)
        autoresponse_out_of_time.assert_not_called()
        redis_mock.sadd.assert_called()
        redis_mock.publish.assert_called()

    @patch('orquestador_app.core.facebook.inbound_chat_event_management.redis_2')
    @patch('orquestador_app.core.facebook.inbound_chat_event_management.autoresponse_welcome')
    @patch('orquestador_app.core.facebook.inbound_chat_event_management.autoresponse_out_of_time')
    def test_new_facebook_conversation_out_of_time_is_closed_by_system(
            self, autoresponse_out_of_time, autoresponse_welcome, redis_mock):
        campana = CampanaFactory()
        destino = DestinoEntranteFactory(content_object=campana)
        page = PaginaMetaFacebook.objects.create(
            name='Page test',
            description='',
            access_token='token',
            verify_token='verify',
            app_id='app-id',
            page_id='page-id',
            destination=destino,
            horario=_business_hours_schedule(),
        )
        timestamp = make_aware(datetime.datetime(2026, 4, 14, 18, 1, 0))
        # Paso parametros posicionales para q async_to_sync no tenga problemas con context
        notifications = async_to_sync(facebook_inbound_chat_event)(
            page,  # page
            timestamp,  # timestamp
            'fb-out-of-time-1',  # message_id
            'fb-user-1',  # origen
            {'text': 'hola'},  # content
            {'name': 'Cliente FB'},  # sender
            {},  # context
            'message',  # type
            None,  # file
        )

        conversation = ConversationMessengerMetaApp.objects.get(
            page=page,
            page_client_id='fb-user-1',
        )

        self.assertEqual(notifications, [])
        self.assertFalse(conversation.is_active)
        self.assertTrue(conversation.is_disposition)
        autoresponse_welcome.assert_not_called()
        autoresponse_out_of_time.assert_called_once_with(conversation, timestamp)
        redis_mock.sadd.assert_not_called()
        redis_mock.publish.assert_not_called()
