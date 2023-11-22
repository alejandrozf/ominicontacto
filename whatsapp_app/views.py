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


class WhatsappProvidersConfigurationView(TemplateView):
    """Configuración de proveedores de Whatsapp"""
    template_name = "whatsapp_providers_configuration.html"


class WhatsappLinesConfigurationView(TemplateView):
    """Configuración de lineas de Whatsapp"""
    template_name = "whatsapp_lines_configuration.html"


class MessageTemplatesConfigurationView(TemplateView):
    """Configuración plantillas de mensaje"""
    template_name = "message_templates_configuration.html"


class MessageTemplateGroupView(TemplateView):
    """Configuración para grupos de plantillas de mensajes"""
    template_name = "message_template_groups.html"
