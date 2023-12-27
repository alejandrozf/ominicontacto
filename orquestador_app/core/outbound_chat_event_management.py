# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from whatsapp_app.models import MensajeWhatsapp
from orquestador_app.core.notify_agents import send_notify
from orquestador_app.core.check_expired import check_expired


async def outbound_chat_event(timestamp, message_id, status, expire, destination):
    try:
        message = MensajeWhatsapp.objects.get(message_id=message_id)
        message.status = status
        if not message.conversation.whatsapp_id:
            message.conversation.whatsapp_id = destination
        message.save()
        if status != 'failed' and message.conversation.error:
            message.conversation.error = False
            message.conversation.save()
        if status == 'failed' and not message.conversation.error:
            message.conversation.error = True
            message.conversation.save()
        if status == 'delivered':
            if not message.conversation.saliente and not message.conversation.atendida:
                message.conversation.atendida = True
                message.conversation.save()
        await send_notify(
            'notify_whatsapp_message_status',
            conversation=message.conversation,
            message=message
        )
        await check_expired(expire, timestamp, message)
    except Exception as e:
        print(">>>>>>>> Error: ", e)
