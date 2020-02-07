# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.translation import ugettext as _
from django.apps import AppConfig


class ConfiguracionTelefoniaAppConfig(AppConfig):
    name = 'configuracion_telefonia_app'

    def supervision_menu_items(self, request):
        if request.user.get_es_administrador_o_supervisor_normal():
            children = []
            if request.user.get_is_administrador():
                children += [
                    {
                        'label': _('Troncales SIP'),
                        'url': reverse('lista_troncal_sip', args=(1,)),
                    },
                    {
                        'label': _('Rutas entrantes'),
                        'url': reverse('lista_rutas_entrantes', args=(1,)),
                    },
                    {
                        'label': _('Rutas salientes'),
                        'url': reverse('lista_rutas_salientes', args=(1,)),
                    },
                    {
                        'label': _('IVR'),
                        'url': reverse('lista_ivrs', args=(1,)),
                    },
                ]
            children += [
                {
                    'label': _('Grupos horarios'),
                    'url': reverse('lista_grupos_horarios', args=(1,)),
                },
                {
                    'label': _('Validaciones Horarias'),
                    'url': reverse('lista_validaciones_fecha_hora', args=(1,)),
                },
                {
                    'label': _('Identificación de Clientes'),
                    'url': reverse('lista_identificador_cliente', args=(1,)),
                },
                {
                    'label': _('Destinos personalizados'),
                    'url': reverse('lista_destinos_personalizados', args=(1,)),
                },
                {
                    'label': _('Adicionar audios'),
                    'url': reverse('adicionar_audios_asterisk'),
                },
            ]

            return [
                {
                    'label': _('Telefonía'),
                    'icon': 'icon-phone',
                    'id': 'menuTelefonia',
                    'children': children,
                },
            ]
        return None
