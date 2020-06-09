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

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiAppConfig(AppConfig):
    name = 'api_app'

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'api_agentes_activos_de_grupo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_campanas_de_supervisor',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_campana_opciones_calificacion',
             'roles': ['Agente', ]},
            {'nombre': 'api_campana_opciones_calificacion_intern',
             'roles': ['Agente', ]},
            {'nombre': 'api_disposition',
             'roles': ['Agente', ]},
            {'nombre': 'api_disposition_new_contact',
             'roles': ['Agente', ]},
            {'nombre': 'api_new_contact',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente', ]},
            {'nombre': 'api_campaign_database_metadata',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', 'Agente', ]},
            {'nombre': 'api_new_role',
             'roles': ['Administrador', ]},
            {'nombre': 'api_delete_role',
             'roles': ['Administrador', ]},
            {'nombre': 'api_update_role_permissions',
             'roles': ['Administrador', ]},
            {'nombre': 'api_agentes_activos',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_supervision_campanas_entrantes',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_supervision_campanas_salientes',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_accion_sobre_agente',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_supervision_llamadas_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_supervision_calificaciones_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'api_contactos_campana',
             'roles': ['Agente', ]},
            {'nombre': 'api_click2call',
             'roles': ['Agente', ]},
            {'nombre': 'api_agent_asterisk_login',
             'roles': ['Agente', ]},
            {'nombre': 'api_agent_asterisk_logout',
             'roles': ['Agente', ]},
            {'nombre': 'api_agente_logout',
             'roles': ['Agente', ]},
            {'nombre': 'api_make_pause',
             'roles': ['Agente', ]},
            {'nombre': 'api_make_unpause',
             'roles': ['Agente', ]},
            {'nombre': 'api_credenciales_sip_agente',
             'roles': ['Agente', ]},
        ]

    informacion_de_permisos = {
        'api_agentes_activos_de_grupo':
            {'descripcion': _('Lista de agentes activos de un Grupo'), 'version': '1.6.2'},
        'api_campanas_de_supervisor':
            {'descripcion': _('Campañas relacionadas a un supervisor'), 'version': '1.6.2'},
        'api_campana_opciones_calificacion':
            {'descripcion': _('Opciones de calificacion de una campaña (id campaña externo)'),
             'version': '1.6.2'},
        'api_campana_opciones_calificacion_intern':
            {'descripcion': _('Opciones de calificacion de una campaña (id campaña oml)'),
             'version': '1.6.2'},
        'api_disposition':
            {'descripcion': _('Ver/editar calificación cliente'), 'version': '1.6.2'},
        'api_disposition_new_contact':
            {'descripcion': _('Crear calificacion cliente'), 'version': '1.6.2'},
        'api_new_contact':
            {'descripcion': _('Crear contacto'), 'version': '1.6.2'},
        'api_campaign_database_metadata':
            {'descripcion': _('Metadata de la base de datos de una campaña'), 'version': '1.6.2'},
        'api_new_role':
            {'descripcion': _('Crear nuevo rol'), 'version': '1.6.3'},
        'api_delete_role':
            {'descripcion': _('Eliminar rol'), 'version': '1.6.3'},
        'api_update_role_permissions':
            {'descripcion': _('Actualizar permisos de Rol'), 'version': '1.6.3'},
        'api_agentes_activos':
            {'descripcion': _('Devuelve información de los agentes en el sistema'),
             'version': '1.6.2'},
        'api_supervision_campanas_entrantes':
            {'descripcion': _('Reporte de llamadas entrantes de supervisión.'), 'version': '1.6.2'},
        'api_supervision_campanas_salientes':
            {'descripcion': _('Reporte de llamadas salientes de supervisión.'), 'version': '1.6.2'},
        'api_accion_sobre_agente':
            {'descripcion':
             _('Ejecuta acciones de supervisión sobre agente (Deslogueo, pausas, etc..)'),
             'version': '1.6.2'},
        'api_supervision_llamadas_campana':
            {'descripcion': _('Cantidades por tipos de llamada en una campaña'),
             'version': '1.6.2'},
        'api_supervision_calificaciones_campana':
            {'descripcion': _('Cantidades por tipo de calificación en una campaña'),
             'version': '1.6.2'},
        'api_contactos_campana':
            {'descripcion': _('Contactos de una campaña'), 'version': '1.6.2'},
        'api_click2call':
            {'descripcion': _('Ejecuta un click 2 call'), 'version': '1.6.2'},
        'api_agent_asterisk_login':
            {'descripcion': _('Ejecuta el login del agente en Asterisk.'), 'version': '1.6.2'},
        'api_agent_asterisk_logout':
            {'descripcion': _('Ejecuta el logout del agente en Asterisk'), 'version': '1.6.2'},
        'api_agente_logout':
            {'descripcion': _('Logout del agente en OML'), 'version': '1.6.2'},
        'api_make_pause':
            {'descripcion': _('Pone al agente en una pausa'), 'version': '1.6.2'},
        'api_make_unpause':
            {'descripcion': _('Saca al agente de una pausa'), 'version': '1.6.2'},
        'api_credenciales_sip_agente':
            {'descripcion': _('Devuelve credenciales SIP de un agente'), 'version': '1.6.2'},

    }
