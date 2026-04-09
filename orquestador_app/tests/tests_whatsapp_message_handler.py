# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import asyncio
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from orquestador_app.core.whatsapp.message_handler import handle_meta_messages


class HandleMetaMessagesTest(SimpleTestCase):

    def test_status_sent_without_conversation_does_not_fail(self):
        line = object()
        event = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "entry-id",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "5493513036130",
                            "phone_number_id": "961887093678879",
                        },
                        "statuses": [{
                            "id": "wamid.test",
                            "status": "sent",
                            "timestamp": "1774643340",
                            "recipient_id": "5493516571322",
                            "pricing": {
                                "billable": False,
                                "pricing_model": "PMP",
                                "category": "service",
                                "type": "free_customer_service",
                            },
                        }],
                    },
                    "field": "messages",
                }],
            }],
        }

        with patch(
            "orquestador_app.core.whatsapp.message_handler.outbound_chat_event",
            new=AsyncMock(),
        ) as outbound_mock:
            asyncio.run(handle_meta_messages(line, event))

        outbound_mock.assert_awaited_once()
        self.assertIsNone(outbound_mock.await_args.kwargs["expire"])
