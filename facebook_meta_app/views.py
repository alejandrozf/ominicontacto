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
from django.views.generic import TemplateView

from ominicontacto_app.models import Campana


class MessengerMetaConfigurationView(TemplateView):
    """Configuración de pages de messenger"""
    template_name = "page_configuration.html"


class FacebookMessageTemplatesConfigurationView(TemplateView):
    """Configuración plantillas de mensaje"""
    template_name = "facebook_message_templates_configuration.html"


class FacebookMessageTemplateGroupView(TemplateView):
    """Configuración para grupos de plantillas de mensajes"""
    template_name = "facebook_message_template_groups.html"


class CampaignReportConversationsListView(TemplateView):
    """Vista de reporte de conversaciones de Meta/Facebook para una campaña."""
    template_name = "facebook_campaign_report_conversations.html"

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_context_data(self, **kwargs):
        context = super(CampaignReportConversationsListView, self).get_context_data(**kwargs)
        context['campaign'] = self.get_object()
        return context


class GeneralReportListView(TemplateView):
    """Vista de reporte general de Meta/Facebook para una campaña."""
    template_name = "facebook_report_general.html"

    def get_object(self, queryset=None):
        return Campana.objects.get(pk=self.kwargs['pk_campana'])

    def get_context_data(self, **kwargs):
        context = super(GeneralReportListView, self).get_context_data(**kwargs)
        context['campaign'] = self.get_object()
        return context
