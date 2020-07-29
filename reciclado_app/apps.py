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
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RecicladoAppConfig(AppConfig):
    name = 'reciclado_app'

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'reciclar_campana_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'reciclar_campana_preview',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
        ]

    informacion_de_permisos = {
        'reciclar_campana_dialer':
            {'descripcion': _('Reciclado de campañas Dialer'), 'version': '1.7.0'},
        'reciclar_campana_preview':
            {'descripcion': _('Reciclado de campañas Preview'), 'version': '1.8.0'},
    }
