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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SupervisionAppConfig(AppConfig):
    name = 'supervision_app'

    def supervision_menu_items(self, request, permissions):
        items = []
        if 'supervision_agentes' in permissions:
            items.append({
                'label': _('Agentes'),
                'url': reverse('supervision_agentes'),
            })
        if 'supervision_campanas_entrantes' in permissions:
            items.append({
                'label': _('Campañas Entrantes'),
                'url': reverse('supervision_campanas_entrantes'),
            })
        if 'supervision_campanas_salientes' in permissions:
            items.append({
                'label': _('Campañas Salientes'),
                'url': reverse('supervision_campanas_salientes'),
            })
        if 'supervision_campanas_dialer' in permissions:
            items.append({
                'label': _('Campañas Dialer'),
                'url': reverse('supervision_campanas_dialer'),
            })
        if items:
            return [{
                'order': 900,
                'label': _('Supervisión'),
                'icon': 'icon-headset',
                'id': 'menuSupervise',
                'children': items
            }]
        return None

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'supervision_agentes',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'supervision_campanas_entrantes',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'supervision_campanas_salientes',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'supervision_campanas_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
        ]

    informacion_de_permisos = {
        'supervision_agentes':
            {'descripcion': _('Estado de agentes en supervisión'), 'version': '1.7.0'},
        'supervision_campanas_entrantes':
            {'descripcion': _('Estado de campañas entrantes en supervisión'), 'version': '1.7.0'},
        'supervision_campanas_salientes':
            {'descripcion': _('Estado de campañas salientes (no dialer) en supervision'),
             'version': '1.7.0'},
        'supervision_campanas_dialer':
            {'descripcion': _('Estado de campañas dialer en supervision'), 'version': '1.13.0'},
    }
