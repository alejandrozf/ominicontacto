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

from django.urls import path
from django.contrib.auth.decorators import login_required
from django.conf.urls import include

from whatsapp_app.views import (
    WhatsappProvidersConfigurationView, WhatsappLinesConfigurationView,
    MessageTemplatesConfigurationView, MessageTemplateGroupView)
from whatsapp_app.api.urls import api_urls_v1


urlpatterns = [
    path('connections/whatsapp/providers/',
         login_required(WhatsappProvidersConfigurationView.as_view()),
         name='whatsapp_providers_configuration',
         ),
    path('connections/whatsapp/lines/',
         login_required(WhatsappLinesConfigurationView.as_view()),
         name='whatsapp_lines_configuration',
         ),
    path('resources/message_templates/',
         login_required(MessageTemplatesConfigurationView.as_view()),
         name='message_templates_configuration',
         ),
    path('resources/message_template_groups/',
         login_required(MessageTemplateGroupView.as_view()),
         name='whatsapp_message_template_groups',
         ),
    path('api/v1/whatsapp/', include((api_urls_v1, 'whatsapp_app'), namespace='v1')),
]
