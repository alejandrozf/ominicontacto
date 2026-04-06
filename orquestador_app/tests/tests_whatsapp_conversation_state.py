# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from asgiref.sync import async_to_sync
from configuracion_telefonia_app.models import OpcionDestino
from ominicontacto_app.tests.factories import CampanaFactory
from orquestador_app.core.whatsapp.inbound_chat_event_management import asignar_campana
from orquestador_app.core.whatsapp.outbound_chat_event_management import s2a_outbound_chat_event
from whatsapp_app.models import MensajeWhatsapp, OpcionMenuInteractivoWhatsapp
from whatsapp_app.tests.factories import (
    ConversacionFactory,
    DestinoEntranteFactory,
    MenuInteractivoFactory,
)


class WhatsAppConversationStateTest(TestCase):

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
