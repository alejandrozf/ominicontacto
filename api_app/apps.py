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
            {'nombre': 'api_click2call_outside_campaign',
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
            {'nombre': 'api_make_reject_call',
             'roles': ['Agente', ]},
            {'nombre': 'api_credenciales_sip_agente',
             'roles': ['Agente', ]},
            {'nombre': 'api_set_estado_revision',
             'roles': ['Agente', ]},
            {'nombre': 'api_upload_base_contactos',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_status_calificacion_llamada',
             'roles': ['Agente', ]},
            {'nombre': 'api_auditoria_archivo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_grabacion_archivo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_grabacion_descarga_masiva',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_call_record_url',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Agente']},
            {'nombre': 'api_contactos_asignados_campana_preview',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_evento_hold',
             'roles': ['Agente', ]},
            {'nombre': 'api_agent_call_transfer_options',
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
            {'nombre': 'api_restart_wombat',
             'roles': ['Administrador', ]},
            {'nombre': 'api_wombat_state',
             'roles': ['Administrador', ]},
            {'nombre': 'api_agents_campaign',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_update_agents_campaign',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_active_agents',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_pause_options',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_set_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_config_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_config_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pause_config_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_site_authentications_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_site_authentications_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_site_authentications_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_site_authentications_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_site_authentications_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_hide',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_sites_show',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_call_dispositions_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_call_dispositions_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_call_dispositions_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_call_dispositions_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_call_dispositions_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_destinations',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_destinations_types',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_systems_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_systems_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_systems_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_external_systems_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_agents_external_system_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_hide',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_forms_show',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_pauses_reactivate',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_inbound_routes_destinations_by_type',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_sip_trunks',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_orphan_trunks',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_outbound_routes_reorder',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_group_of_hours_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_group_of_hours_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_group_of_hours_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_group_of_hours_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_group_of_hours_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_audio_options_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_ivrs_destination_types_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor']},
            {'nombre': 'api_register_server_detail',
             'roles': ['Administrador']},
            {'nombre': 'api_register_server_create',
             'roles': ['Administrador']},
            {'nombre': 'api_log_survey_transfer',
             'roles': ['Agente', ]},
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
            {'descripcion': _('Ejecuta un click 2 call a una campaña'), 'version': '1.7.0'},
        'api_click2call_outside_campaign':
            {'descripcion': _('Ejecuta un click 2 call fuera de campaña'), 'version': '1.25.0'},
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
        'api_make_reject_call':
            {'descripcion': _('Establece el estado Reject del Agente'), 'version': '1.7.0'},
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
        'api_auditoria_archivo':
            {'descripcion': _('Retorna el archivo csv de auditoria'),
             'version': '1.11.0'},
        'api_grabacion_archivo':
            {'descripcion': _('Retorna el archivo de grabación especificado'),
             'version': '1.11.0'},
        'api_grabacion_descarga_masiva':
            {'descripcion': _('Retorna Zip con archivos de grabación especificados'),
             'version': '1.14.0'},
        'api_call_record_url':
            {'descripcion': _('Retorna URL del archivos de grabación asociado al callid'),
             'version': '1.25.0'},
        'api_contactos_asignados_campana_preview':
            {'descripcion': _('Devuelve los contactos asignados de una campaña preview'),
             'version': '1.8.0'},
        'api_evento_hold':
            {'descripcion': _('Loggea el evento hold o unhold'),
             'version': '1.13.0'},
        'api_agent_call_transfer_options':
            {'descripcion': _('Lista de agentes para transferir llamadas'),
             'version': '1.29.0'},
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
            {'descripcion': _('Listas de nombres de columnas para Base de datos de Contactos'),
             'version': '1.20.0'},
        'api_restart_wombat':
            {'descripcion': _('Reinicia servicio Wombat Dialer'),
             'version': '1.22.0'},
        'api_wombat_state':
            {'descripcion': _('Estado del servicio Wombat Dialer'),
             'version': '1.22.0'},
        'api_agents_campaign':
            {'descripcion': _('Lista de agentes por campaña'),
             'version': '1.19.0'},
        'api_update_agents_campaign':
            {'descripcion': _('Actualiza los agentes de una campaña'),
             'version': '1.19.0'},
        'api_active_agents':
            {'descripcion': _('Obtiene todos los agentes activos'),
             'version': '1.19.0'},
        'api_pause_set_pause_options':
            {'descripcion': _('Obtiene las pausas que no estan eliminadas'),
             'version': '1.21.0'},
        'api_pause_set_list':
            {'descripcion': _('Lista los conjuntos de pausas'),
             'version': '1.21.0'},
        'api_pause_set_detail':
            {'descripcion': _('Obtiene el detalle de un conjunto de pausas'),
             'version': '1.21.0'},
        'api_pause_set_create':
            {'descripcion': _('Crea un conjunto de pausas'),
             'version': '1.21.0'},
        'api_pause_set_update':
            {'descripcion': _('Actualiza un conjunto de pausas'),
             'version': '1.21.0'},
        'api_pause_set_delete':
            {'descripcion': _('Elimina un conjunto de pausas'),
             'version': '1.21.0'},
        'api_pause_config_create':
            {'descripcion': _('Crea una configuracion de pausa'),
             'version': '1.21.0'},
        'api_pause_config_update':
            {'descripcion': _('Actualiza una configuracion de pausa'),
             'version': '1.21.0'},
        'api_pause_config_delete':
            {'descripcion': _('Elimina una configuracion de pausa'),
             'version': '1.21.0'},
        'api_external_sites_list':
            {'descripcion': _('Lista los sitios externos'),
             'version': '1.23.0'},
        'api_external_sites_detail':
            {'descripcion': _('Obtiene el detalle de un sitio externo'),
             'version': '1.23.0'},
        'api_external_sites_create':
            {'descripcion': _('Crea un sitio externo'),
             'version': '1.23.0'},
        'api_external_sites_update':
            {'descripcion': _('Actualiza un sitio externo'),
             'version': '1.23.0'},
        'api_external_sites_delete':
            {'descripcion': _('Elimina un sitio externo'),
             'version': '1.23.0'},
        'api_external_site_authentications_list':
            {'descripcion': _('Lista las autenticaciones para sitios externos'),
             'version': '1.23.0'},
        'api_external_site_authentications_detail':
            {'descripcion': _('Obtiene el detalle de una autenticacion para sitio externo'),
             'version': '1.23.0'},
        'api_external_site_authentications_create':
            {'descripcion': _('Crea una autenticacion para sitio externo'),
             'version': '1.23.0'},
        'api_external_site_authentications_update':
            {'descripcion': _('Actualiza una autenticacion para sitio externo'),
             'version': '1.23.0'},
        'api_external_site_authentications_delete':
            {'descripcion': _('Elimina una autenticacion para sitio externo'),
             'version': '1.23.0'},
        'api_external_sites_hide':
            {'descripcion': _('Oculta un sitio externo'),
             'version': '1.23.0'},
        'api_external_sites_show':
            {'descripcion': _('Desoculta un sitio externo'),
             'version': '1.23.0'},
        'api_call_dispositions_list':
            {'descripcion': _('Lista las calificaciones'),
             'version': '1.23.0'},
        'api_call_dispositions_create':
            {'descripcion': _('Crea una calificacion'),
             'version': '1.23.0'},
        'api_call_dispositions_update':
            {'descripcion': _('Actualiza una calificacion'),
             'version': '1.23.0'},
        'api_call_dispositions_delete':
            {'descripcion': _('Elimina una calificacion'),
             'version': '1.23.0'},
        'api_call_dispositions_detail':
            {'descripcion': _('Obtiene detalle de una calificacion'),
             'version': '1.23.0'},
        'api_inbound_destinations':
            {'descripcion': _('Lista los destinos entrantes'),
             'version': '1.21.0'},
        'api_inbound_destinations_types':
            {'descripcion': _('Lista tipos de destinos entrantes'),
             'version': '1.21.0'},
        'api_external_systems_list':
            {'descripcion': _('Lista los sistemas externos'),
             'version': '1.23.0'},
        'api_external_systems_create':
            {'descripcion': _('Crea un sistema externo'),
             'version': '1.23.0'},
        'api_external_systems_update':
            {'descripcion': _('Actualiza un sistema externo'),
             'version': '1.23.0'},
        'api_external_systems_detail':
            {'descripcion': _('Obtiene detalle de un sistema externo'),
             'version': '1.23.0'},
        'api_agents_external_system_list':
            {'descripcion': _('Obtiene los agentes para asignar a un sistema externo'),
             'version': '1.23.0'},
        'api_forms_list':
            {'descripcion': _('Lista los formularios'),
             'version': '1.23.0'},
        'api_forms_create':
            {'descripcion': _('Crea un formulario'),
             'version': '1.23.0'},
        'api_forms_update':
            {'descripcion': _('Actualiza un formulario'),
             'version': '1.23.0'},
        'api_forms_detail':
            {'descripcion': _('Obtiene detalle de un formulario'),
             'version': '1.23.0'},
        'api_forms_delete':
            {'descripcion': _('Elimina un formulario'),
             'version': '1.23.0'},
        'api_forms_hide':
            {'descripcion': _('Oculta un formulario'),
             'version': '1.23.0'},
        'api_forms_show':
            {'descripcion': _('Desoculta un formulario'),
             'version': '1.23.0'},
        'api_pauses_list':
            {'descripcion': _('Lista las pausas'),
             'version': '1.23.0'},
        'api_pauses_create':
            {'descripcion': _('Crea una pausa'),
             'version': '1.23.0'},
        'api_pauses_update':
            {'descripcion': _('Actualiza una pausa'),
             'version': '1.23.0'},
        'api_pauses_detail':
            {'descripcion': _('Obtiene detalle de una pausa'),
             'version': '1.23.0'},
        'api_pauses_delete':
            {'descripcion': _('Elimina una pausa'),
             'version': '1.23.0'},
        'api_pauses_reactivate':
            {'descripcion': _('Reactiva una pausa'),
             'version': '1.23.0'},
        'api_inbound_routes_list':
            {'descripcion': _('Lista las rutas entrantes'),
             'version': '1.23.0'},
        'api_inbound_routes_create':
            {'descripcion': _('Crea una ruta entrante'),
             'version': '1.23.0'},
        'api_inbound_routes_update':
            {'descripcion': _('Actualiza una ruta entrante'),
             'version': '1.23.0'},
        'api_inbound_routes_detail':
            {'descripcion': _('Obtiene detalle de una ruta entrante'),
             'version': '1.23.0'},
        'api_inbound_routes_delete':
            {'descripcion': _('Elimina una ruta entrante'),
             'version': '1.23.0'},
        'api_inbound_routes_destinations_by_type':
            {'descripcion': _('Obtiene los destinos disponibles'),
             'version': '1.23.0'},
        'api_outbound_routes_list':
            {'descripcion': _('Lista las rutas salientes'),
             'version': '1.23.0'},
        'api_outbound_routes_create':
            {'descripcion': _('Crea una ruta saliente'),
             'version': '1.23.0'},
        'api_outbound_routes_update':
            {'descripcion': _('Actualiza una ruta saliente'),
             'version': '1.23.0'},
        'api_outbound_routes_detail':
            {'descripcion': _('Obtiene detalle de una ruta saliente'),
             'version': '1.23.0'},
        'api_outbound_routes_delete':
            {'descripcion': _('Elimina una ruta saliente'),
             'version': '1.23.0'},
        'api_outbound_routes_sip_trunks':
            {'descripcion': _('Obtiene las troncales sip para rutas salientes'),
             'version': '1.23.0'},
        'api_outbound_routes_orphan_trunks':
            {'descripcion': _('Obtiene las troncales huerfanas de una ruta saliente'),
             'version': '1.23.0'},
        'api_outbound_routes_reorder':
            {'descripcion': _('Reordena las rutas salientes'),
             'version': '1.23.0'},
        'api_group_of_hours_list':
            {'descripcion': _('Lista los grupos horarios'),
             'version': '1.23.0'},
        'api_group_of_hours_create':
            {'descripcion': _('Crea un grupo horario'),
             'version': '1.23.0'},
        'api_group_of_hours_update':
            {'descripcion': _('Actualiza un grupo horario'),
             'version': '1.23.0'},
        'api_group_of_hours_detail':
            {'descripcion': _('Obtiene detalle de un grupo horario'),
             'version': '1.23.0'},
        'api_group_of_hours_delete':
            {'descripcion': _('Elimina un grupo horario'),
             'version': '1.23.0'},
        'api_ivrs_list':
            {'descripcion': _('Lista los ivrs'),
             'version': '1.26.0'},
        'api_ivrs_create':
            {'descripcion': _('Crea un ivr'),
             'version': '1.26.0'},
        'api_ivrs_update':
            {'descripcion': _('Actualiza un ivr'),
             'version': '1.26.0'},
        'api_ivrs_detail':
            {'descripcion': _('Obtiene detalle de un ivr'),
             'version': '1.26.0'},
        'api_ivrs_delete':
            {'descripcion': _('Elimina un ivr'),
             'version': '1.26.0'},
        'api_ivrs_audio_options_list':
            {'descripcion': _('Obtiene los audios disponibles para ivr'),
             'version': '1.26.0'},
        'api_ivrs_destination_types_list':
            {'descripcion': _('Obtiene los destinos por tipo para un ivr'),
             'version': '1.26.0'},
        'api_register_server_detail':
            {'descripcion': _('Obtener el detalle del registro'),
             'version': '1.29.0'},
        'api_register_server_create':
            {'descripcion': _('Obtener el detalle del registro'),
             'version': '1.29.0'},
        'api_log_survey_transfer':
            {'descripcion': _('Loguea un intento de transferencia a Survey'),
             'version': '1.27.0'},
    }
