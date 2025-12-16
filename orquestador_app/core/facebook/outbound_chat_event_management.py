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
from facebook_meta_app.models import MessageMessengerMetaApp
from orquestador_app.core.notify_agents import send_notify
from orquestador_app.core.whatsapp.check_expired import check_expired


async def outbound_chat_event(timestamp, message_id, status, expire, destination, error_ex):
    notifications = await s2a_outbound_chat_event(
        timestamp,
        message_id,
        status,
        expire,
        destination,
        error_ex,
    )
    for ntype, nargs in notifications:
        await send_notify(ntype, **nargs)


async def s2a_outbound_chat_event(timestamp, message_id, status,
                                  expire, destination, error_ex):
    notifications = []
    try:
        print("status de mensaje saliente ====>", status, message_id)
        message = MessageMessengerMetaApp.objects.get(message_id=message_id)
        message.status = status
        if status == 'failed':
            message.fail_reason = error_ex['reason']
        if not message.conversation.page_client_id:
            message.conversation.page_client_id = destination
        message.save()
        if status != 'failed' and message.conversation.error:
            message.conversation.error = False
            message.conversation.error_ex = {}
            message.conversation.save()
        if status == 'failed' and not message.conversation.error:
            message.conversation.error = True
            message.conversation.error_ex = error_ex
            message.conversation.save()
        if status == 'delivered':
            if not message.conversation.saliente and not message.conversation.atendida:
                message.conversation.atendida = True
                message.conversation.save()
        notifications.append((
            'notify_whatsapp_message_status', {
                'conversation': message.conversation,
                'message': message
            }
        ))
        for notification in check_expired(expire, timestamp, message):
            notifications.append(notification)
    except Exception as e:
        print(">>>>>>>> Error: ", e)
    return notifications
