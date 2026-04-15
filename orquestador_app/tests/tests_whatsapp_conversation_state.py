# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import make_aware
from asgiref.sync import async_to_sync
from configuracion_telefonia_app.models import OpcionDestino
from configuracion_telefonia_app.tests.factories import GrupoHorarioFactory, ValidacionTiempoFactory
from ominicontacto_app.tests.factories import CampanaFactory
from orquestador_app.core.whatsapp.inbound_chat_event_management import (
    asignar_campana,
    s2a_inbound_chat_event as whatsapp_inbound_chat_event,
)
from orquestador_app.core.whatsapp.outbound_chat_event_management import s2a_outbound_chat_event
from whatsapp_app.models import ConversacionWhatsapp, MensajeWhatsapp, OpcionMenuInteractivoWhatsapp
from whatsapp_app.tests.factories import (
    ConversacionFactory,
    DestinoEntranteFactory,
    LineaFactory,
    MenuInteractivoFactory,
)


def _schedule_until_2210():
    grupo_horario = GrupoHorarioFactory()
    ValidacionTiempoFactory(
        grupo_horario=grupo_horario,
        tiempo_inicial=datetime.time(9, 0, 0),
        tiempo_final=datetime.time(22, 10, 0),
        dia_semana_inicial=1,
        dia_semana_final=1,
        dia_mes_inicio=None,
        dia_mes_final=None,
        mes_inicio=None,
        mes_final=None,
    )
    return grupo_horario


class WhatsAppConversationStateTest(TestCase):

    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.redis_2')
    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_welcome')
    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_out_of_time')
    def test_new_inbound_conversation_started_out_of_time_is_closed_by_system(
            self, autoresponse_out_of_time, autoresponse_welcome, redis_mock):
        line = LineaFactory(horario=_schedule_until_2210())
        timestamp = make_aware(datetime.datetime(2026, 4, 14, 22, 11, 0))

        # Paso parametros posicionales para q async_to_sync no tenga problemas con context
        # line, timestamp, message_id, origen, content, sender, context, type
        notifications = async_to_sync(whatsapp_inbound_chat_event)(
            line,  # line
            timestamp,  # timestamp
            'wa-out-of-time-system-close-1',  # message_id
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
        self.assertEqual(conversation.expire, make_aware(datetime.datetime(2026, 4, 15, 22, 11, 0)))
        self.assertEqual(conversation.date_last_interaction, timestamp)
        self.assertFalse(conversation.is_active)
        self.assertTrue(conversation.is_disposition)
        autoresponse_welcome.assert_not_called()
        autoresponse_out_of_time.assert_called_once_with(line, conversation, timestamp)
        redis_mock.sadd.assert_not_called()
        redis_mock.publish.assert_not_called()

    @patch('orquestador_app.core.whatsapp.inbound_chat_event_management.autoresponse_out_of_time')
    def test_existing_inbound_conversation_started_before_cutoff_does_not_trigger_out_of_time(
            self, autoresponse_out_of_time):
        line = LineaFactory(horario=_schedule_until_2210())
        conversation = ConversacionWhatsapp.objects.create(
            line=line,
            campana=line.destino.content_object,
            client=None,
            destination='5493517585765',
            whatsapp_id='5493517585765',
            is_active=True,
            expire=make_aware(datetime.datetime(2026, 4, 15, 22, 4, 0)),
            timestamp=make_aware(datetime.datetime(2026, 4, 14, 22, 4, 0)),
            date_last_interaction=make_aware(datetime.datetime(2026, 4, 14, 22, 4, 0)),
            client_alias='Cliente',
        )
        timestamp = make_aware(datetime.datetime(2026, 4, 14, 22, 11, 0))

        # Paso parametros posicionales para q async_to_sync no tenga problemas con context
        # line, timestamp, message_id, origen, content, sender, context, type
        async_to_sync(whatsapp_inbound_chat_event)(
            line,  # line
            timestamp,  # timestamp
            'wa-after-cutoff-1',  # message_id
            '5493517585765',  # origen
            {'text': 'sigo escribiendo'},  # content
            {'name': 'Cliente'},  # sender
            {},  # context
            'text',  # type
        )

        conversation.refresh_from_db()

        self.assertFalse(conversation.is_disposition)
        self.assertTrue(conversation.is_active)
        self.assertEqual(conversation.date_last_interaction, timestamp)
        autoresponse_out_of_time.assert_not_called()

    def test_outbound_delivered_from_automatic_message_keeps_conversation_unattended(self):
        conversation = ConversacionFactory(
            saliente=False,
            atendida=False,
        )
        message = MensajeWhatsapp.objects.create(
            message_id='auto-msg-1',
            conversation=conversation,
            origen=conversation.line.numero,
            sender={},
            content={'text': 'welcome'},
            type='text',
            status='submitted',
        )

        notifications = async_to_sync(s2a_outbound_chat_event)(
            timestamp=message.timestamp,
            message_id=message.message_id,
            status='delivered',
            expire=conversation.expire,
            destination=conversation.destination,
            error_ex={},
        )

        conversation.refresh_from_db()
        message.refresh_from_db()

        self.assertFalse(conversation.atendida)
        self.assertEqual(message.status, 'delivered')
        self.assertEqual(len(notifications), 1)

    def test_assigning_menu_reply_to_campaign_marks_conversation_attended(self):
        campana = CampanaFactory()
        menu = MenuInteractivoFactory(texto_derivacion='')
        destino_menu = DestinoEntranteFactory(content_object=menu)
        destino_campana = DestinoEntranteFactory(content_object=campana)
        opcion = OpcionDestino.crear_opcion_destino(destino_menu, destino_campana, 'Laboratorio')
        OpcionMenuInteractivoWhatsapp.objects.create(
            opcion=opcion,
            descripcion='Laboratorio central',
        )
        conversation = ConversacionFactory(
            line__destino=destino_menu,
            campana=None,
            atendida=False,
            destination='5493512780071',
        )
        origin_message = MensajeWhatsapp.objects.create(
            message_id='menu-msg-1',
            conversation=conversation,
            origen=conversation.line.numero,
            sender={'destino_entrante': destino_menu.id},
            content={'type': 'list'},
            type='list-meta',
            status='delivered',
        )

        notifications = asignar_campana(
            line=conversation.line,
            conversation=conversation,
            content={'title': 'Laboratorio'},
            context={'id': origin_message.message_id},
        )

        conversation.refresh_from_db()

        self.assertEqual(conversation.campana_id, campana.id)
        self.assertTrue(conversation.atendida)
        self.assertEqual(len(notifications), 1)
