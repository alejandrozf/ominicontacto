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
            {'nombre': 'reenviar_key_registro',
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
            {'nombre': 'api_reasignar_agenda_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_data_agenda_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_contactados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_calificados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_no_atendidos',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_calificaciones_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_formulario_gestion_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'api_exportar_csv_resultados_base_contactados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
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
            {'nombre': 'api_make_ringing',
             'roles': ['Agente', ]},
            {'nombre': 'api_credenciales_sip_agente',
             'roles': ['Agente', ]},
            {'nombre': 'api_set_estado_revision',
             'roles': ['Agente', ]},
            {'nombre': 'api_upload_base_contactos',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_status_calificacion_llamada',
             'roles': ['Agente', ]},
            {'nombre': 'api_grabacion_archivo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_grabacion_descarga_masiva',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_contactos_asignados_campana_preview',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_evento_hold',
             'roles': ['Agente', ]},
            {'nombre': 'api_audios_listado',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_grupos',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_agentes',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_dashboard_supervision',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_audit_supervisor',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_database_metadata_columns_fields',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
        ]

    informacion_de_permisos = {
        'api_agentes_activos_de_grupo':
            {'descripcion': _('Lista de agentes activos de un Grupo'), 'version': '1.7.0'},
        'api_campanas_de_supervisor':
            {'descripcion': _('Campañas relacionadas a un supervisor'), 'version': '1.7.0'},
        'api_campana_opciones_calificacion':
            {'descripcion': _('Opciones de calificacion de una campaña (id campaña externo)'),
             'version': '1.7.0'},
        'api_campana_opciones_calificacion_intern':
            {'descripcion': _('Opciones de calificacion de una campaña (id campaña oml)'),
             'version': '1.7.0'},
        'api_disposition':
            {'descripcion': _('Ver/editar calificación cliente'), 'version': '1.7.0'},
        'api_disposition_new_contact':
            {'descripcion': _('Crear calificacion cliente'), 'version': '1.7.0'},
        'api_new_contact':
            {'descripcion': _('Crear contacto'), 'version': '1.7.0'},
        'api_campaign_database_metadata':
            {'descripcion': _('Metadata de la base de datos de una campaña'), 'version': '1.7.0'},
        'api_new_role':
            {'descripcion': _('Crear nuevo rol'), 'version': '1.7.0'},
        'api_delete_role':
            {'descripcion': _('Eliminar rol'), 'version': '1.7.0'},
        'api_update_role_permissions':
            {'descripcion': _('Actualizar permisos de Rol'), 'version': '1.7.0'},
        'api_agentes_activos':
            {'descripcion': _('Devuelve información de los agentes en el sistema'),
             'version': '1.7.0'},
        'api_supervision_campanas_entrantes':
            {'descripcion': _('Reporte de llamadas entrantes de supervisión.'), 'version': '1.7.0'},
        'api_supervision_campanas_salientes':
            {'descripcion': _('Reporte de llamadas salientes no dialer de supervisión.'),
             'version': '1.7.0'},
        'api_accion_sobre_agente':
            {'descripcion':
             _('Ejecuta acciones de supervisión sobre agente (Deslogueo, pausas, etc..)'),
             'version': '1.7.0'},
        'api_supervision_llamadas_campana':
            {'descripcion': _('Cantidades por tipos de llamada en una campaña'),
             'version': '1.7.0'},
        'api_supervision_calificaciones_campana':
            {'descripcion': _('Cantidades por tipo de calificación en una campaña'),
             'version': '1.7.0'},
        'api_reasignar_agenda_contacto':
            {'descripcion': _('Reasignar una Agenda a otro Agente'), 'version': '1.7.0'},
        'api_data_agenda_contacto':
            {'descripcion': _('Información de contacto de una  Agenda'), 'version': '1.7.0'},
        'api_exportar_csv_contactados':
            {'descripcion': _('Exportar reporte de contactados de una campaña a csv'),
             'version': '1.11.6'},
        'api_exportar_csv_calificados':
            {'descripcion': _('Exportar reporte de calificados de una campaña a csv'),
             'version': '1.11.6'},
        'api_exportar_csv_no_atendidos':
            {'descripcion': _('Exportar reporte de no atendidos de una campaña a csv'),
             'version': '1.11.6'},
        'api_exportar_csv_calificaciones_campana':
            {'descripcion': _('Exportar reporte de calificaciones de una campaña a csv'),
             'version': '1.11.6'},
        'api_exportar_csv_formulario_gestion_campana':
            {'descripcion': _('Exportar reporte de calificaciones de una campaña a csv'),
             'version': '1.11.6'},
        'api_exportar_csv_resultados_base_contactados':
            {'descripcion': _('API para exportar resultados de base contactados a csv'),
             'version': '1.19.0'},
        'api_contactos_campana':
            {'descripcion': _('Contactos de una campaña'), 'version': '1.7.0'},
        'api_click2call':
            {'descripcion': _('Ejecuta un click 2 call'), 'version': '1.7.0'},
        'api_agent_asterisk_login':
            {'descripcion': _('Ejecuta el login del agente en Asterisk.'), 'version': '1.7.0'},
        'api_agent_asterisk_logout':
            {'descripcion': _('Ejecuta el logout del agente en Asterisk'), 'version': '1.7.0'},
        'api_agente_logout':
            {'descripcion': _('Logout del agente en OML'), 'version': '1.7.0'},
        'api_make_pause':
            {'descripcion': _('Pone al agente en una pausa'), 'version': '1.7.0'},
        'api_make_unpause':
            {'descripcion': _('Saca al agente de una pausa'), 'version': '1.7.0'},
        'api_make_ringing':
            {'descripcion': _('Establece el estado Ringing del Agente'), 'version': '1.7.0'},
        'api_credenciales_sip_agente':
            {'descripcion': _('Devuelve credenciales SIP de un agente'), 'version': '1.7.0'},
        'api_set_estado_revision':
            {'descripcion': _('Establece el estado de revisión de una Auditoría'),
             'version': '1.8.0'},
        'api_upload_base_contactos':
            {'descripcion': _('Almacena en la base de datos los contactos subidos en archivo csv'),
             'version': '1.7.0'},
        'api_status_calificacion_llamada':
            {'descripcion': _('Detecta si una llamada esta calificada.'),
             'version': '1.8.0'},
        'reenviar_key_registro':
            {'description': _('Reenvía la llave de la instancia registrada por email')},
        'api_grabacion_archivo':
            {'descripcion': _('Retorna el archivo de grabación especificado'),
             'version': '1.11.0'},
        'api_grabacion_descarga_masiva':
            {'descripcion': _('Retorna Zip con archivos de grabación especificados'),
             'version': '1.14.0'},
        'api_contactos_asignados_campana_preview':
            {'descripcion': _('Devuelve los contactos asignados de una campaña preview'),
             'version': '1.8.0'},
        'api_evento_hold':
            {'descripcion': _('Loggea el evento hold o unhold'),
             'version': '1.13.0'},
        'api_audios_listado':
            {'descripcion': _('Lista audios de asterisk'),
             'version': '1.16.0'},
        'api_grupos':
            {'descripcion': _('Lista de grupos de agentes'),
             'version': '1.17.0'},
        'api_agentes':
            {'descripcion': _('Lista de Agentes'),
             'version': '1.17.0'},
        'api_dashboard_supervision':
            {'descripcion': _('Dashboard de supervision'),
             'version': '1.18.0'},
        'api_audit_supervisor':
            {'descripcion': _('Auditoría a supervisores'),
             'version': '1.20.0'},
        'api_database_metadata_columns_fields':
            {'descripcion': _('Listas de nombres de columnas para Base de datos de Conatactos'),
             'version': '1.20.0'}
    }
