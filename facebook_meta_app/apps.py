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
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FacebookMetaAppConfig(AppConfig):
    name = 'facebook_meta_app'

    def configuraciones_de_permisos(self):
        return [
            # Configuración general de Messenger
            {'nombre': 'messenger_meta_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},

            # Plantillas de mensaje
            {'nombre': 'facebook_message_templates_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'facebook_message_template_groups',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},

            # API v1 / routers
            {'nombre': 'page',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'destination',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'campaigns',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'facebook_reports',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'chat',
             'roles': ['Agente', 'Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'contact',
             'roles': ['Agente']},
            {'nombre': 'disposition_chat',
             'roles': ['Agente']},
            {'nombre': 'transfer',
             'roles': ['Agente']},

            # Templates
            {'nombre': 'templates_messenger',
             'roles': ['Agente']},
            {'nombre': 'group_template_messenger',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'templates',
             'roles': ['Agente']},
        ]

    informacion_de_permisos = {
        'messenger_meta_configuration': {
            'descripcion': _('Configuración general de Messenger'),
            'version': '1.26.0'
        },
        'facebook_message_templates_configuration': {
            'descripcion': _('Configuración de plantillas de mensajes'),
            'version': '1.26.0'
        },
        'facebook_message_template_groups': {
            'descripcion': _('Grupos de plantillas de mensajes'),
            'version': '1.26.0'
        },
        'page': {'descripcion': _('Configuración de página'), 'version': '1.26.0'},
        'destination': {'descripcion': _('Destinos'), 'version': '1.26.0'},
        'campaigns': {'descripcion': _('Campañas'), 'version': '1.26.0'},
        'facebook_reports': {'descripcion': _('Reportes Meta/Facebook'), 'version': '1.26.0'},
        'chat': {'descripcion': _('Conversaciones / Chat'), 'version': '1.26.0'},
        'contact': {'descripcion': _('Contactos'), 'version': '1.26.0'},
        'disposition_chat': {'descripcion': _('Disposición de chat'), 'version': '1.26.0'},
        'transfer': {'descripcion': _('Transferencia de agentes'), 'version': '1.26.0'},
        'templates_messenger': {'descripcion': _('Plantillas Messenger'), 'version': '1.26.0'},
        'group_template_messenger':
        {'descripcion': _('Grupos de plantillas Messenger'), 'version': '1.26.0'},
        'templates': {'descripcion': _('Templates por campaña'), 'version': '1.26.0'},
    }
