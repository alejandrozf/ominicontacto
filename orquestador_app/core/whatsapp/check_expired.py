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
import logging

logger = logging.getLogger(__name__)


def check_expired(expire, timestamp, message):
    notifications = []
    try:
        if expire:
            if message.conversation.expire:
                if message.conversation.expire < expire:  # expired conversation
                    message.conversation.expire = expire
                    message.conversation.save()
                    notifications.append(('notify_whatsapp_chat_expired', {
                        'conversation': message.conversation,
                    }))
            else:
                message.conversation.expire = expire
                message.conversation.timestamp = timestamp
                message.conversation.save()
    except Exception as e:
        logger.exception("error en check_expired %r", e)
    return notifications
