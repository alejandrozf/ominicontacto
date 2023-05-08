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
from __future__ import unicode_literals

from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class WhatsappAppConfig(AppConfig):
    name = 'whatsapp_app'

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'whatsapp_providers_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'whatsapp_lines_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'message_templates_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'whatsapp_message_template_groups',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'whatsapp_template_groups',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'proveedor-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'proveedor-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'linea-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'linea-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'destino-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'plantilla-mensaje-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'plantilla-mensaje-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'template-whatsapp-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'template-whatsapp-sincronizar-templates',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'campana-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'grupo-plantilla-whatsapp-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'grupo-plantilla-whatsapp-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'grupo-template-whatsapp-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'grupo-template-whatsapp-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'configuracion-whatsapp-campana-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'configuracion-whatsapp-campana-templates',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'configuracion-whatsapp-campana-detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-agent-chats-lists',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-attend-chat',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-messages',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-send-menssage-attachment',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-send-menssage-text',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-send-message-template',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'conversacion-send-message-whatsapp-template',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'transfer-agents',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'transfer-to-agent',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
        ]

    informacion_de_permisos = {
        'whatsapp_providers_configuration':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'whatsapp_lines_configuration':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'message_templates_configuration':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'whatsapp_message_template_groups':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'whatsapp_template_groups':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'proveedor-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'proveedor-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'linea-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'linea-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'destino-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'plantilla-mensaje-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'plantilla-mensaje-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'template-whatsapp-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'template-whatsapp-sincronizar-templates':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'campana-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'grupo-plantilla-whatsapp-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'grupo-plantilla-whatsapp-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'grupo-template-whatsapp-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'grupo-template-whatsapp-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'configuracion-whatsapp-campana-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'configuracion-whatsapp-campana-templates':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'configuracion-whatsapp-campana-detail':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-list':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-agent-chats-lists':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-attend-chat':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-messages':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-send-menssage-attachment':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-send-menssage-text':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-send-message-template':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'conversacion-send-message-whatsapp-template':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'transfer-to-agent':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
        'transfer-agents':
            {'descripcion': _('Configuración Whatsapp'),
             'version': '1.26.0'},
    }
