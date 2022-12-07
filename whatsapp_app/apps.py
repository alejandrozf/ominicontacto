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
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'whatsapp_lines_configuration',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'whatsapp_templates_configuration',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'message_templates_configuration',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
        ]

    informacion_de_permisos = {
        'whatsapp_providers_configuration':
            {'descripcion': _('Configuración de proveedores de Whatsapp'),
             'version': '1.26.0'},
        'whatsapp_lines_configuration':
            {'descripcion': _('Configuración de lineas de Whatsapp'),
             'version': '1.26.0'},
        'whatsapp_templates_configuration':
            {'descripcion': _('Configuración de templates de Whatsapp'),
             'version': '1.26.0'},
        'message_templates_configuration':
            {'descripcion': _('Configuración de plantillas de mensaje'),
             'version': '1.26.0'},
    }
