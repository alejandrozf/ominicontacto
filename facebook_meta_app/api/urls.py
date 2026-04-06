# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions
from django.urls import path
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

import facebook_meta_app.api.v1.page_configuration
import facebook_meta_app.api.v1.campaign
import facebook_meta_app.api.v1.conversation
import facebook_meta_app.api.v1.destination
import facebook_meta_app.api.v1.transfer
import facebook_meta_app.api.v1.contact
import facebook_meta_app.api.v1.disposition
import facebook_meta_app.api.v1.reporte
import facebook_meta_app.api.v1.templates_messenger
import facebook_meta_app.api.v1.templates_group
import facebook_meta_app.api.v1.templates

from facebook_meta_app.api import ViewSetRouter


router = ViewSetRouter(trailing_slash=False)
routes = (
    (r"page", facebook_meta_app.api.v1.page_configuration.ViewSet),
    (r"destination", facebook_meta_app.api.v1.destination.ViewSet),
    (r"campaigns", facebook_meta_app.api.v1.campaign.ViewSet),
    (r"chat", facebook_meta_app.api.v1.conversation.ViewSet),
    (r"contact/(?P<campana_pk>[^/.]+)", facebook_meta_app.api.v1.contact.ViewSet),
    (r"disposition_chat", facebook_meta_app.api.v1.disposition.ViewSet),
    (r"transfer", facebook_meta_app.api.v1.transfer.ViewSet),
    (r"templates_messenger", facebook_meta_app.api.v1.templates_messenger.ViewSet),
    (r"group_template_messenger", facebook_meta_app.api.v1.templates_group.ViewSet),
    (r"templates/(?P<campana_pk>[^/.]+)", facebook_meta_app.api.v1.templates.ViewSet),

)

for route in routes:
    router.register(*route)

api_urls_v1 = router.urls

urlpatterns = [
    path(
        'reports/',
        facebook_meta_app.api.v1.reporte.ReportAPIView.as_view(),
        name='api_facebook_reports',
    ),
    path(
        'chat/<int:campaing_id>/filter_chats',
        facebook_meta_app.api.v1.conversation.ReportConversationAPIView.as_view(),
        name='api_campaign_facebook_report_conversations',
    ),
] + api_urls_v1
