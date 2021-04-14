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
from django.urls import reverse
from constance import config


class OminicontactoAppConfig(AppConfig):
    name = 'ominicontacto_app'

    def supervision_menu_items(self, request, permissions):
        items = []

        # Usuarios y grupos
        usuarios_y_grupos = []

        usuarios = []
        if 'user_list' in permissions:
            usuarios.append({
                'label': _('Usuarios'),
                'url': reverse('user_list', args=(1, ))
            })
        if 'user_nuevo' in permissions:
            usuarios.append({
                'label': _('Nuevo usuario'),
                'url': reverse('user_nuevo')
            })
        if 'user_new_agent' in permissions:
            usuarios.append({
                'label': _('Nuevo usuario Agente'),
                'url': reverse('user_new_agent')
            })
        if 'agente_list' in permissions:
            usuarios.append({
                'label': _('Agentes'),
                'url': reverse('agente_list')
            })
        if 'supervisor_list' in permissions:
            usuarios.append({
                'label': _('Supervisores'),
                'url': reverse('supervisor_list')
            })
        if config.WEBPHONE_CLIENT_ENABLED and 'cliente_webphone_list' in permissions:
            usuarios.append({
                'label': _('Clientes WebPhone'),
                'url': reverse('cliente_webphone_list')
            })
        if usuarios:
            usuarios_y_grupos.append({
                'label': _('Lista de usuarios'),
                'id': 'menuUsers',
                'children': usuarios,
            })
        if 'grupo_list' in permissions:
            usuarios_y_grupos.append({
                'label': _('Grupos de agentes'),
                'url': reverse('grupo_list')
            })
        if 'grupo_nuevo' in permissions:
            usuarios_y_grupos.append({
                'label': _('Nuevo Grupo de agentes'),
                'url': reverse('grupo_nuevo')
            })
        if 'user_role_management' in permissions:
            usuarios_y_grupos.append({
                'label': _('Roles y permisos'),
                'url': reverse('user_role_management')
            })
        if usuarios_y_grupos:
            items.append({'order': 100,
                          'label': _('Usuarios y grupos'),
                          'id': 'menuUsersGroups',
                          'icon': 'icon-user',
                          'children': usuarios_y_grupos})

        # Campañas
        campanas = []
        #  Dialers
        dialers = []
        if 'campana_dialer_list' in permissions:
            dialers.append({
                'label': _('Listado de campañas'),
                'url': reverse('campana_dialer_list')
            })
        if 'campana_dialer_create' in permissions:
            dialers.append({
                'label': _('Nueva campaña'),
                'url': reverse('campana_dialer_create')
            })
        if 'lista_campana_dialer_template' in permissions:
            dialers.append({
                'label': _('Templates'),
                'url': reverse('lista_campana_dialer_template')
            })
        if 'campana_dialer_template_create' in permissions:
            dialers.append({
                'label': _('Nuevo template'),
                'url': reverse('campana_dialer_template_create')
            })
        if dialers:
            campanas.append({
                'label': _('Campañas dialer'),
                'id': 'menuCampaignDialer',
                'children': dialers
            })
        #  Preview
        previews = []
        if 'campana_preview_list' in permissions:
            previews.append({
                'label': _('Listado de campañas'),
                'url': reverse('campana_preview_list')
            })
        if 'campana_preview_create' in permissions:
            previews.append({
                'label': _('Nueva campaña'),
                'url': reverse('campana_preview_create')
            })
        if 'campana_preview_template_list' in permissions:
            previews.append({
                'label': _('Templates'),
                'url': reverse('campana_preview_template_list')
            })
        if 'campana_preview_template_create' in permissions:
            previews.append({
                'label': _('Nuevo template'),
                'url': reverse('campana_preview_template_create')
            })
        if previews:
            campanas.append(({
                'label': _('Campañas preview'),
                'id': 'menuCampaignPreview',
                'children': previews
            }))
        #  Entrantes
        entrantes = []
        if 'campana_list' in permissions:
            entrantes.append({
                'label': _('Listado de campañas'),
                'url': reverse('campana_list')
            })
        if 'campana_nuevo' in permissions:
            entrantes.append({
                'label': _('Nueva campaña'),
                'url': reverse('campana_nuevo')
            })
        if 'campana_entrante_template_list' in permissions:
            entrantes.append({
                'label': _('Templates'),
                'url': reverse('campana_entrante_template_list')
            })
        if 'campana_entrante_template_create' in permissions:
            entrantes.append({
                'label': _('Nuevo template'),
                'url': reverse('campana_entrante_template_create')
            })
        if entrantes:
            campanas.append({
                'label': _('Campañas entrantes'),
                'id': 'menuCampaignIn',
                'children': entrantes
            })
        #  Manuales
        manuales = []
        if 'campana_manual_list' in permissions:
            manuales.append({
                'label': _('Listado de campañas'),
                'url': reverse('campana_manual_list')
            })
        if 'campana_manual_create' in permissions:
            manuales.append({
                'label': _('Nueva campaña'),
                'url': reverse('campana_manual_create')
            })
        if 'campana_manual_template_list' in permissions:
            manuales.append({
                'label': _('Templates'),
                'url': reverse('campana_manual_template_list')
            })
        if 'campana_manual_template_create' in permissions:
            manuales.append({
                'label': _('Nuevo template'),
                'url': reverse('campana_manual_template_create')
            })
        if manuales:
            campanas.append({
                'label': _('Campañas manuales'),
                'id': 'menuCampaignManual',
                'children': manuales
            })
        #  Calificaciones
        calificaciones = []
        if 'calificacion_list' in permissions:
            calificaciones.append({
                'label': _('Listado de calificaciones'),
                'url': reverse('calificacion_list')
            })
        if 'calificacion_nuevo' in permissions:
            calificaciones.append({
                'label': _('Nueva Calificación'),
                'url': reverse('calificacion_nuevo')
            })
        if calificaciones:
            campanas.append({
                'label': _('Calificaciones'),
                'id': 'menuQualifications',
                'children': calificaciones
            })
        #  Formularios
        formularios = []
        if 'formulario_nuevo' in permissions:
            formularios.append({
                'label': _('Nuevo formulario'),
                'url': reverse('formulario_nuevo')
            })
        if 'formulario_list' in permissions:
            formularios.append({
                'label': _('Listado de formularios'),
                'url': reverse('formulario_list')
            })
        if formularios:
            campanas.append({
                'label': _('Formularios'),
                'id': 'menuForms',
                'children': formularios
            })
        #  Sitios Externos
        sitios_externos = []
        if 'sitio_externo_create' in permissions:
            sitios_externos.append({
                'label': _('Nuevo sitio'),
                'url': reverse('sitio_externo_create')
            })
        if 'sitio_externo_list' in permissions:
            sitios_externos.append({
                'label': _('Listado de sitios'),
                'url': reverse('sitio_externo_list')
            })
            campanas.append({
                'label': _('Sitios Externos'),
                'id': 'menuSites',
                'children': sitios_externos
            })
        #  Sistemas EXternos
        sistemas_externos = []
        if 'sistema_externo_create' in permissions:
            sistemas_externos.append({
                'label': _('Nuevo sistema'),
                'url': reverse('sistema_externo_create')
            })
        if 'sistema_externo_list' in permissions:
            sistemas_externos.append({
                'label': _('Listado de sistemas'),
                'url': reverse('sistema_externo_list')
            })
        if sistemas_externos:
            campanas.append({
                'label': _('Sistemas Externos'),
                'id': 'menuSystems',
                'children': sistemas_externos
            })

        if campanas:
            items.append({'order': 200,
                          'label': _('Campañas'),
                          'id': 'menuCampaign',
                          'icon': 'icon-campaign',
                          'children': campanas})

        # Pausas
        pausas = []
        if 'pausa_list' in permissions:
            pausas.append({
                'label': _('Listado de pausas'),
                'url': reverse('pausa_list')
            })
        if 'pausa_nuevo' in permissions:
            pausas.append({
                'label': _('Nueva pausa'),
                'url': reverse('pausa_nuevo')
            })
        if pausas:
            items.append({'order': 200,
                          'label': _('Pausas'),
                          'icon': 'icon-pause',
                          'id': 'menuBreaks',
                          'children': pausas})
        # Contactos
        contactos = []
        if 'lista_base_datos_contacto' in permissions:
            contactos.append({
                'label': _('Base de datos de contactos'),
                'url': reverse('lista_base_datos_contacto')
            })
        if 'nueva_base_datos_contacto' in permissions:
            contactos.append({
                'label': _('Nueva base de datos de contactos'),
                'url': reverse('nueva_base_datos_contacto')
            })
        if 'listas_rapidas' in permissions:
            contactos.append({
                'label': _('Listas rápidas'),
                'url': reverse('listas_rapidas')
            })
        if 'nueva_lista_rapida' in permissions:
            contactos.append({
                'label': _('Nueva lista rápida'),
                'url': reverse('nueva_lista_rapida')
            })
        if contactos:
            contactos.append({'line': True})

        if 'black_list_list' in permissions:
            contactos.append({
                'label': _('Blacklists'),
                'url': reverse('black_list_list')
            })
        if 'black_list_create' in permissions:
            contactos.append({
                'label': _('Nueva Blacklist'),
                'url': reverse('black_list_create')
            })
        if contactos:
            items.append({'order': 400,
                          'label': _('Contactos'),
                          'icon': 'icon-contacts',
                          'id': 'menuContacts',
                          'children': contactos})

        # Grabaciones y Auditorias
        if 'grabacion_buscar' in permissions:
            items.append({'order': 500,
                          'label': _('Buscar Grabación'),
                          'icon': 'icon-search',
                          'url': reverse('grabacion_buscar', args=(1,))})
        if 'buscar_auditorias_gestion' in permissions:
            items.append({'order': 600,
                          'label': _('Buscar Auditorías'),
                          'icon': 'icon-search',
                          'url': reverse('buscar_auditorias_gestion', args=(1,))})
        return items

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'consola_de_agente',
             'roles': ['Agente', ]},
            {'nombre': 'registrar_usuario',
             'roles': ['Administrador', ]},
            {'nombre': 'addons_disponibles',
             'roles': ['Administrador', ]},
            {'nombre': 'user_nuevo',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'user_new_agent',
             'roles': ['Supervisor', ]},
            {'nombre': 'user_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'user_delete',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'user_update',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'agent_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agent_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'user_change_password',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente']},
            {'nombre': 'agente_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agenteprofile_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agente_activar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agente_desactivar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'supervisor_list',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'supervisor_update',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'cliente_webphone_list',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'cliente_webphone_toggle_activacion',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'user_role_management',
             'roles': ['Administrador', ]},
            {'nombre': 'grupo_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'grupo_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'grupo_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'grupo_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'pausa_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'pausa_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'pausa_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'pausa_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'grabacion_marcar',
             'roles': ['Agente', ]},
            {'nombre': 'grabacion_descripcion',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', 'Agente', ]},
            {'nombre': 'grabacion_buscar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'grabacion_agente_buscar',
             'roles': ['Agente', ]},
            {'nombre': 'buscar_auditorias_gestion',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'auditar_calificacion_cliente',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'service_campanas_activas',
             'roles': ['Agente', ]},
            {'nombre': 'service_agentes_de_grupo',
             'roles': ['Agente', ]},
            {'nombre': 'lista_base_datos_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'nueva_base_datos_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'update_base_datos_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'update_base_datos_contacto_de_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'define_base_datos_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agregar_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agregar_contacto_a_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'actualiza_base_datos_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'actualiza_base_datos_contacto_de_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'contacto_list_bd_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'actualizar_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_contacto',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'oculta_base_dato',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'desoculta_base_datos',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'mostrar_bases_datos_ocultas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'bloquear_campos_para_agente',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'contacto_list',
             'roles': ['Agente', ]},
            {'nombre': 'contacto_update',
             'roles': ['Agente', ]},
            {'nombre': 'seleccion_campana_adicion_contacto',
             'roles': ['Agente', ]},
            {'nombre': 'nuevo_contacto_campana',
             'roles': ['Agente', ]},
            {'nombre': 'nuevo_contacto_campana_a_llamar',
             'roles': ['Agente', ]},
            {'nombre': 'campana_busqueda_contacto',
             'roles': ['Agente', ]},
            {'nombre': 'campana_contactos_telefono_repetido',
             'roles': ['Agente', ]},
            {'nombre': 'identificar_contacto_a_llamar',
             'roles': ['Agente', ]},
            {'nombre': 'campana_entrante_template_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_entrante_template_create_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_entrante_template_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_entrante_template_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_entrante_template_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_activas_miembro',
             'roles': ['Agente', ]},
            {'nombre': 'liberar_contacto_asignado_agente',
             'roles': ['Agente', ]},
            {'nombre': 'reporte_agente_calificaciones',
             'roles': ['Agente', ]},
            {'nombre': 'exporta_reporte_calificaciones',
             'roles': ['Agente', ]},
            {'nombre': 'exporta_reporte_formularios',
             'roles': ['Agente', ]},
            {'nombre': 'agente_llamar_contacto',
             'roles': ['Agente', ]},
            {'nombre': 'agente_llamar_sin_campana',
             'roles': ['Agente', ]},
            {'nombre': 'calificacion_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'calificacion_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'calificacion_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'calificacion_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_list_mostrar_ocultos',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_field',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campo_formulario_orden',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_field_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_vista_previa',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_eliminar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_mostrar_ocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'formulario_vista',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'calificar_llamada',
             'roles': ['Agente', ]},
            {'nombre': 'calificar_llamada_con_contacto',
             'roles': ['Agente', ]},
            {'nombre': 'calificacion_formulario_update_or_create',
             'roles': ['Agente', ]},
            {'nombre': 'recalificacion_formulario_update_or_create',
             'roles': ['Agente', ]},
            {'nombre': 'calificacion_cliente_actualiza_desde_reporte',
             'roles': ['Agente', ]},
            {'nombre': 'auditar_calificacion',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'calificar_por_telefono',
             'roles': ['Agente', ]},
            {'nombre': 'formulario_detalle',
             'roles': ['Agente', ]},
            {'nombre': 'formulario_venta',
             'roles': ['Agente', ]},
            {'nombre': 'auditar_formulario_venta',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agente_cambiar_estado',
             'roles': ['Agente', ]},
            {'nombre': 'agente_dashboard',
             'roles': ['Agente', ]},
            {'nombre': 'llamadas_activas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'supervision_agentes_logueados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agenda_contacto_create',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contacto_update',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contacto_detalle',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contacto_listado',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contactos_por_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_dialer_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'start_campana_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'pausar_campana_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'activar_campana_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_ocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_desocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_update_base',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_supervisors',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'campana_dialer_mostrar_ocultas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_dialer_finaliza_activas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'disposition_incidence_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'disposition_incidence_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'disposition_incidence_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'disposition_incidence_edit',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_manual_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_ocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_desocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_supervisors',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'campana_manual_mostrar_ocultas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_preview_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_preview_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_supervisors',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'campana_preview_mostrar_ocultas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_mostrar_ocultar',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_dispatcher',
             'roles': ['Agente', ]},
            {'nombre': 'validar_contacto_asignado',
             'roles': ['Agente', ]},
            {'nombre': 'contactos_preview_asignados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'liberar_reservar_contacto_asignado',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'ordenar_entrega_contactos_preview',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'descargar_orden_contactos_actual_preview',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'campana_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_elimina',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'oculta_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'desoculta_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_supervisors',
             'roles': ['Administrador', 'Gerente', ]},
            {'nombre': 'mostrar_campanas_ocultas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', 'Referente', ]},
            {'nombre': 'black_list_create',
             'roles': ['Administrador', ]},
            {'nombre': 'black_list_list',
             'roles': ['Administrador', ]},
            {'nombre': 'sistema_externo_list',
             'roles': ['Administrador', ]},
            {'nombre': 'sistema_externo_create',
             'roles': ['Administrador', ]},
            {'nombre': 'modificar_sistema_externo',
             'roles': ['Administrador', ]},
            {'nombre': 'sitio_externo_list',
             'roles': ['Administrador', ]},
            {'nombre': 'sitio_externo_create',
             'roles': ['Administrador', ]},
            {'nombre': 'oculta_sitio_externo',
             'roles': ['Administrador', ]},
            {'nombre': 'desoculta_sitio_externo',
             'roles': ['Administrador', ]},
            {'nombre': 'mostrar_sitios_externo_ocultos',
             'roles': ['Administrador', ]},
            {'nombre': 'modificar_sitio_externo',
             'roles': ['Administrador', ]},
            {'nombre': 'sitio_externo_delete',
             'roles': ['Administrador', ]},
            {'nombre': 'queue_member_add',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'queue_member_grupo_agente',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'queue_member_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'queue_member_elimina',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_template_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_campana_dialer_template',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'crea_campana_dialer_template',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_template_detalle',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_dialer_template_elimina',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_template_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_template_create_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_template_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_template_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_manual_template_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_template_create',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_template_create_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_template_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_template_detail',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'campana_preview_template_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'lista_archivo_audio',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'create_archivo_audio',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'edita_archivo_audio',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_archivo_audio',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'configurar_agentes_en_campana',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'finalizar_campana_dialer',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'listas_rapidas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'nueva_lista_rapida',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'update_lista_rapida',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'eliminar_lista_rapida',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'define_lista_rapida',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
        ]

    informacion_de_permisos = {
        'consola_de_agente':
            {'descripcion': _('Consola de Agente'), 'version': '1.7.0'},
        'registrar_usuario':
            {'descripcion': _('Registrar la llave del usuario OML'), 'version': '1.7.0'},
        'addons_disponibles':
            {'descripcion': _('Obtener información de los addons disponibles'),
             'version': '1.11.6'},
        'user_nuevo':
            {'descripcion': _('Crear un Usuario'), 'version': '1.7.0'},
        'user_new_agent':
            {'descripcion': _('Crear un Usuario con rol Agente'), 'version': '1.11.0'},
        'user_list':
            {'descripcion': _('Ver lista de Usuarios'), 'version': '1.7.0'},
        'user_delete':
            {'descripcion': _('Borrar Usuario (no agente)'), 'version': '1.7.0'},
        'user_update':
            {'descripcion': _('Editar Usuario (no agente)'), 'version': '1.7.0'},
        'agent_delete':
            {'descripcion': _('Borrar Usuario Agente'), 'version': '1.7.0'},
        'agent_update':
            {'descripcion': _('Editar Usuario Agente'), 'version': '1.7.0'},
        'user_change_password':
            {'descripcion': _('Forzar cambio de password'), 'version': '1.9.0'},
        'agente_list':
            {'descripcion': _('Ver lista de Agentes'), 'version': '1.7.0'},
        'agenteprofile_update':
            {'descripcion': _('Editar Perfil de Agente'), 'version': '1.7.0'},
        'agente_activar':
            {'descripcion': _('Activar Agente'), 'version': '1.7.0'},
        'agente_desactivar':
            {'descripcion': _('Desactivar Agente'), 'version': '1.7.0'},
        'supervisor_list':
            {'descripcion': _('Ver lista de Supervisores'), 'version': '1.7.0'},
        'supervisor_update':
            {'descripcion': _('Editar Perfil de Supervisor'), 'version': '1.7.0'},
        'cliente_webphone_list':
            {'descripcion': _('Ver lista de Clientes WebPhone'), 'version': '1.7.0'},
        'cliente_webphone_toggle_activacion':
            {'descripcion': _('Activar/Desactivar cliente WebPhone'), 'version': '1.7.0'},
        'user_role_management':
            {'descripcion': _('Administración de roles'), 'version': '1.7.0'},
        'grupo_list':
            {'descripcion': _('Ver lista de Grupos'), 'version': '1.7.0'},
        'grupo_nuevo':
            {'descripcion': _('Crear Grupo'), 'version': '1.7.0'},
        'grupo_update':
            {'descripcion': _('Modificar Grupo'), 'version': '1.7.0'},
        'grupo_delete':
            {'descripcion': _('Borrar Grupo'), 'version': '1.7.0'},
        'pausa_list':
            {'descripcion': _('Ver lista de Pausas'), 'version': '1.7.0'},
        'pausa_nuevo':
            {'descripcion': _('Crear Pausa'), 'version': '1.7.0'},
        'pausa_update':
            {'descripcion': _('Modificar Pausa'), 'version': '1.7.0'},
        'pausa_delete':
            {'descripcion': _('Borrar Pausa'), 'version': '1.7.0'},
        'grabacion_marcar':
            {'descripcion': _('Marcar la grabación en curso.'), 'version': '1.7.0'},
        'grabacion_descripcion':
            {'descripcion': _('Ver la marca (campo descripcion) de una grabacion.'),
             'version': '1.7.0'},
        'grabacion_buscar':
            {'descripcion': _('Busqueda de grabaciones por parte de un supervisor'),
             'version': '1.7.0'},
        'grabacion_agente_buscar':
            {'descripcion': _('Busqueda de grabaciones propias para Agentes'), 'version': '1.7.0'},
        'buscar_auditorias_gestion':
            {'descripcion': _('Acceder al listado de calificaciones a auditar'),
             'version': '1.7.0'},
        'auditar_calificacion_cliente':
            {'descripcion': _('Crear/editar auditoría de calificacion'), 'version': '1.7.0'},
        'service_campanas_activas':
            {'descripcion':
             _('Lista de Campanas activas. Se usan como opciones para transferencias.'),
             'version': '1.7.0'},
        'service_agentes_de_grupo':
            {'descripcion': _('Lista de Agentes del mismo grupo que el Agente loggeado'),
             'version': '1.7.0'},
        'lista_base_datos_contacto':
            {'descripcion': _('Lista de bases de datos de contactos'), 'version': '1.7.0'},
        'nueva_base_datos_contacto':
            {'descripcion': _('Crear base de datos de contacto'), 'version': '1.7.0'},
        'update_base_datos_contacto':
            {'descripcion': _('Agregar lista de contactos a base de datos de contacto'),
             'version': '1.7.0'},
        'update_base_datos_contacto_de_campana':
            {'descripcion':
             _('Agregar lista de contactos a base de datos de contacto de una Campaña'),
             'version': '1.7.0'},
        'define_base_datos_contacto':
            {'descripcion':
             _('Define base de datos de contacto. Paso necesario al momento de la creación'),
             'version': '1.7.0'},
        'agregar_contacto':
            {'descripcion': _('Agregar un contacto a base de datos de contacto'),
             'version': '1.7.0'},
        'agregar_contacto_a_campana':
            {'descripcion': _('Agregar un contacto a base de datos de contacto de una campaña'),
             'version': '1.7.0'},
        'actualiza_base_datos_contacto':
            {'descripcion':
             _('Define base de datos de contacto. Paso necesario al momento de la creación'),
             'version': '1.7.0'},
        'actualiza_base_datos_contacto_de_campana':
            {'descripcion':
             _('Define base de datos de contacto para una campaña. Agrega contactos'),
             'version': '1.7.0'},
        'contacto_list_bd_contacto':
            {'descripcion': _('Ver lista de contactos de una Base de datos de contactos'),
             'version': '1.7.0'},
        'actualizar_contacto':
            {'descripcion': _('Actualizar un contacto'), 'version': '1.7.0'},
        'eliminar_contacto':
            {'descripcion': _('Eliminar un contacto'), 'version': '1.7.0'},
        'oculta_base_dato':
            {'descripcion': _('Ocultar una base de datos de contactos'), 'version': '1.7.0'},
        'desoculta_base_datos':
            {'descripcion': _('Desocultar una base de datos de contactos'), 'version': '1.7.0'},
        'mostrar_bases_datos_ocultas':
            {'descripcion': _('Mostrar bases de datos de contactos ocultas'), 'version': '1.7.0'},
        'bloquear_campos_para_agente':
            {'descripcion': _('Restringir campos de Contacto para Agente'), 'version': '1.7.0'},
        'contacto_list':
            {'descripcion': _('Lista de contactos para una campaña'), 'version': '1.7.0'},
        'contacto_update':
            {'descripcion': _('Actualizar un contacto'), 'version': '1.7.0'},
        'seleccion_campana_adicion_contacto':
            {'descripcion': _('Selección de campaña para agregar un contacto'), 'version': '1.7.0'},
        'nuevo_contacto_campana':
            {'descripcion': _('Crear un nuevo contacto'), 'version': '1.7.0'},
        'nuevo_contacto_campana_a_llamar':
            {'descripcion': _('Crea un nuevo contacto y luego efectua llamada'),
             'version': '1.7.0'},
        'campana_busqueda_contacto':
            {'descripcion': _('Búsqueda de contacto para agente.'), 'version': '1.7.0'},
        'campana_contactos_telefono_repetido':
            {'descripcion': _('Contactos que comparten un número de teléfono'), 'version': '1.7.0'},
        'identificar_contacto_a_llamar':
            {'descripcion': _('Identificar el contacto para la llamada'), 'version': '1.7.0'},
        'campana_entrante_template_create':
            {'descripcion': _('Crear template para campaña entrante'), 'version': '1.7.0'},
        'campana_entrante_template_create_campana':
            {'descripcion': _('Crear campaña entrante a partir de un template'),
             'version': '1.7.0'},
        'campana_entrante_template_list':
            {'descripcion': _('Ver lista de templates de campañas entrantes'), 'version': '1.7.0'},
        'campana_entrante_template_detail':
            {'descripcion': _('Ver el detalle de un template de campaña entrante'),
             'version': '1.7.0'},
        'campana_entrante_template_delete':
            {'descripcion': _('Borrar un template de campaña entrante'), 'version': '1.7.0'},
        'campana_preview_activas_miembro':
            {'descripcion': _('Pantalla para llamar contactos de campañas preview'),
             'version': '1.7.0'},
        'liberar_contacto_asignado_agente':
            {'descripcion': _('Liberar un contacto asignado en una campaña preview'),
             'version': '1.7.0'},
        'reporte_agente_calificaciones':
            {'descripcion': _('Ver calificaciones propias de Agente'), 'version': '1.7.0'},
        'exporta_reporte_calificaciones':
            {'descripcion': _('Descargar reporte de calificaciones propias de Agente'),
             'version': '1.7.0'},
        'exporta_reporte_formularios':
            {'descripcion': _('Descargar reporte de calificaciones de gestión propias de Agente'),
             'version': '1.7.0'},
        'agente_llamar_contacto':
            {'descripcion': _('Llamar a un contacto'), 'version': '1.7.0'},
        'agente_llamar_sin_campana':
            {'descripcion': _('Llamar por fuera de las campañas.'), 'version': '1.7.0'},
        'calificacion_list':
            {'descripcion': _('Ver lista de opciones de Calificación'), 'version': '1.7.0'},
        'calificacion_nuevo':
            {'descripcion': _('Crear nueva Opción de calificación'), 'version': '1.7.0'},
        'calificacion_update':
            {'descripcion': _('Modificar Opción de calificación'), 'version': '1.7.0'},
        'calificacion_delete':
            {'descripcion': _('Borrar opción de calificación'), 'version': '1.7.0'},
        'formulario_list':
            {'descripcion': _('Ver lista de Formularios de gestión'), 'version': '1.7.0'},
        'formulario_list_mostrar_ocultos':
            {'descripcion': _('Mostrar Formularios de gestión ocultos'), 'version': '1.7.0'},
        'formulario_nuevo':
            {'descripcion': _('Crear nuevo Formulario de gestión'), 'version': '1.7.0'},
        'formulario_field':
            {'descripcion': _('Crear un campo para un formulario de gestión'), 'version': '1.7.0'},
        'campo_formulario_orden':
            {'descripcion': _('Modificar el orden de los campos de un formulario de gestión'),
             'version': '1.7.0'},
        'formulario_field_delete':
            {'descripcion': _('Borrar un campo de un formulario de gestión'), 'version': '1.7.0'},
        'formulario_vista_previa':
            {'descripcion': _('Vista previa de un Formulario de gestión'), 'version': '1.7.0'},
        'formulario_eliminar':
            {'descripcion': _('Eliminar un Formulario de gestión'), 'version': '1.7.0'},
        'formulario_mostrar_ocultar':
            {'descripcion': _('Mostrar u ocultar un Formulario de gestión'), 'version': '1.7.0'},
        'formulario_vista':
            {'descripcion': _('Ver Formulario de gestión'), 'version': '1.7.0'},
        'calificar_llamada':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'calificar_llamada_con_contacto':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'calificacion_formulario_update_or_create':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'recalificacion_formulario_update_or_create':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'calificacion_cliente_actualiza_desde_reporte':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'auditar_calificacion':
            {'descripcion': _('Editar una calificacion al auditarla (Supervisor)'),
             'version': '1.7.0'},
        'calificar_por_telefono':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.7.0'},
        'formulario_detalle':
            {'descripcion': _('Ver la respuesta de un Formulario de Gestión'), 'version': '1.7.0'},
        'formulario_venta':
            {'descripcion': _('Crear/editar la respuesta de un Formulario de gestión'), 'version':
             '1.7.0'},
        'auditar_formulario_venta':
            {'descripcion': _('Editar la respuesta de un formulario de gestión al auditarla'),
             'version': '1.7.0'},
        'agente_cambiar_estado':
            {'descripcion': _('Modificar el estado de un Agente en Asterisk'), 'version': '1.7.0'},
        'agente_dashboard':
        {'descripcion': _('Vista del dashboard de un agente'), 'version': '1.11.7'},
        'llamadas_activas':
            {'descripcion': _('Llamadas activas actuales'), 'version': '1.7.0'},
        'supervision_agentes_logueados':
            {'descripcion': _('Agentes logueados'), 'version': '1.7.0'},
        'agenda_contacto_create':
            {'descripcion': _('Agenda para un contacto'), 'version': '1.7.0'},
        'agenda_contacto_update':
            {'descripcion': _('Re-agenda para un contacto'), 'version': '1.8.0'},
        'agenda_contacto_detalle':
            {'descripcion': _('Ver el detalle de la Agenda de un contacto'), 'version': '1.7.0'},
        'agenda_contacto_listado':
            {'descripcion': _('Listado de Agendas de contactos'), 'version': '1.7.0'},
        'agenda_contactos_por_campana':
            {'descripcion': _('Listado para reasignar Agendas de contactos por Campaña'),
             'version': '1.7.0'},
        'campana_dialer_list':
            {'descripcion': _('Ver listado de campañas Dialer'), 'version': '1.7.0'},
        'campana_dialer_create':
            {'descripcion': _('Crear campaña Dialer'), 'version': '1.7.0'},
        'campana_dialer_update':
            {'descripcion': _('Editar campana Dialer'), 'version': '1.7.0'},
        'start_campana_dialer':
            {'descripcion': _('Dar inicio a una campaña Dialer'), 'version': '1.7.0'},
        'pausar_campana_dialer':
            {'descripcion': _('Pausar una campaña Dialer'), 'version': '1.7.0'},
        'activar_campana_dialer':
            {'descripcion': _('Activar una campaña Dialer'), 'version': '1.7.0'},
        'campana_dialer_delete':
            {'descripcion': _('Borrar una campaña Dialer'), 'version': '1.7.0'},
        'campana_dialer_ocultar':
            {'descripcion': _('Ocultar una campaña Dialer'), 'version': '1.7.0'},
        'campana_dialer_desocultar':
            {'descripcion': _('Mostrar una campaña Dialer oculta'), 'version': '1.7.0'},
        'campana_dialer_update_base':
            {'descripcion': _('Actualizar la base de datos de una Campaña Dialer'),
             'version': '1.7.0'},
        'campana_dialer_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Dialer'), 'version': '1.7.0'},
        'campana_dialer_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Dialers ocultas'), 'version': '1.7.0'},
        'campana_dialer_finaliza_activas':
            {'descripcion': _('Finalizar campañas activas que no tengan contactos pendientes'),
             'version': '1.7.0'},
        'disposition_incidence_list':
            {'descripcion': _('Listado de Reglas de incidencia por calificación'),
             'version': '1.11.8'},
        'disposition_incidence_delete':
            {'descripcion': _('Eliminar Reglas de incidencia por calificación'),
             'version': '1.11.8'},
        'disposition_incidence_create':
            {'descripcion': _('Crear Regla de incidencia por calificación'), 'version': '1.11.8'},
        'disposition_incidence_edit':
            {'descripcion': _('Editar Regla de incidencia por calificación'), 'version': '1.11.8'},
        'campana_manual_list':
            {'descripcion': _('Ver listado de campañas Manuales'), 'version': '1.7.0'},
        'campana_manual_create':
            {'descripcion': _('Crear campaña Manual'), 'version': '1.7.0'},
        'campana_manual_update':
            {'descripcion': _('Editar campaña Manual'), 'version': '1.7.0'},
        'campana_manual_delete':
            {'descripcion': _('Borrar campaña Manual'), 'version': '1.7.0'},
        'campana_manual_ocultar':
            {'descripcion': _('Ocultar campaña Manual'), 'version': '1.7.0'},
        'campana_manual_desocultar':
            {'descripcion': _('Mostrar una campaña Manual oculta'), 'version': '1.7.0'},
        'campana_manual_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Manual'), 'version': '1.7.0'},
        'campana_manual_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Manuales ocultas'), 'version': '1.7.0'},
        'campana_preview_list':
            {'descripcion': _('Ver listado de campañas Preview'), 'version': '1.7.0'},
        'campana_preview_create':
            {'descripcion': _('Crear campaña Preview'), 'version': '1.7.0'},
        'campana_preview_update':
            {'descripcion': _('Editar campaña Preview'), 'version': '1.7.0'},
        'campana_preview_delete':
            {'descripcion': _('Borrar campaña Preview'), 'version': '1.7.0'},
        'campana_preview_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Preview'), 'version': '1.7.0'},
        'campana_preview_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Preview ocultas'), 'version': '1.7.0'},
        'campana_mostrar_ocultar':
            {'descripcion': _('Ocultar campaña Preview'), 'version': '1.7.0'},
        'campana_preview_dispatcher':
            {'descripcion': _('Obtener un contacto de una campaña Preview para llamarlo'),
             'version': '1.7.0'},
        'validar_contacto_asignado':
            {'descripcion':
             _('Validar que el agente tiene asignado un contacto de una campaña Preview'),
             'version': '1.7.0'},
        'contactos_preview_asignados':
            {'descripcion': _('Ver los contactos de una campaña Preview asignados a algun agente'),
             'version': '1.7.0'},
        'liberar_reservar_contacto_asignado':
            {'descripcion': _('Liberar o reservar un contacto de una campaña Preview asignado'
                              'a un agente'),
             'version': '1.7.0'},
        'ordenar_entrega_contactos_preview':
            {'descripcion': _('Definir orden de asignacion de contactos de una campaña Preview'),
             'version': '1.5.2'},
        'descargar_orden_contactos_actual_preview':
            {'descripcion': _('Descargar orden de asignacion de contactos de una campaña Preview'),
             'version': '1.5.2'},
        'campana_list':
            {'descripcion': _('Ver lista de campañas Entrantes'), 'version': '1.7.0'},
        'campana_nuevo':
            {'descripcion': _('Crear campaña Entrante'), 'version': '1.7.0'},
        'campana_update':
            {'descripcion': _('Modificar campaña Entrante'), 'version': '1.7.0'},
        'campana_elimina':
            {'descripcion': _('Borrar campaña Entrante'), 'version': '1.7.0'},
        'oculta_campana':
            {'descripcion': _('Ocultar campaña Entrante'), 'version': '1.7.0'},
        'desoculta_campana':
            {'descripcion': _('Mostrar campaña Entrante oculta'), 'version': '1.7.0'},
        'campana_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Entrante'), 'version': '1.7.0'},
        'mostrar_campanas_ocultas':
            {'descripcion': _('Mostrar campañas Entrantes ocultas'), 'version': '1.7.0'},
        'black_list_create':
            {'descripcion': _('Creacion de una Blacklist'), 'version': '1.7.0'},
        'black_list_list':
            {'descripcion': _('Ver lista de Blacklists'), 'version': '1.7.0'},
        'sistema_externo_list':
            {'descripcion': _('Ver lista de Sistemas Externos'), 'version': '1.7.0'},
        'sistema_externo_create':
            {'descripcion': _('Crear un Sistema Externo'), 'version': '1.7.0'},
        'modificar_sistema_externo':
            {'descripcion': _('Modificar un Sistema Externo'), 'version': '1.7.0'},
        'sitio_externo_list':
            {'descripcion': _('Ver lista de Sitios Externos'), 'version': '1.7.0'},
        'sitio_externo_create':
            {'descripcion': _('Crear un Sitio Externo'), 'version': '1.7.0'},
        'oculta_sitio_externo':
            {'descripcion': _('Ocultar un Sitio Externo'), 'version': '1.7.0'},
        'desoculta_sitio_externo':
            {'descripcion': _('Mostrar un Sitio Externo oculto'), 'version': '1.7.0'},
        'mostrar_sitios_externo_ocultos':
            {'descripcion': _('Mostrar los Sitios Externos ocultos'), 'version': '1.7.0'},
        'modificar_sitio_externo':
            {'descripcion': _('Modificar un Sitio Externo'), 'version': '1.7.0'},
        'sitio_externo_delete':
            {'descripcion': _('Borrar un Sitio Externo'), 'version': '1.7.0'},
        'queue_member_add':
            {'descripcion': _('Agregar un Agente a una Campaña'), 'version': '1.7.0'},
        'queue_member_grupo_agente':
            {'descripcion': _('Agregar un Grupo de Agentes a una Campaña'), 'version': '1.7.0'},
        'queue_member_campana':
            {'descripcion': _('Pantalla de asignacion de Agentes a Campaña'), 'version': '1.7.0'},
        'queue_member_elimina':
            {'descripcion': _('Eliminar un Agente de una Campaña'), 'version': '1.7.0'},
        'campana_dialer_template_create':
            {'descripcion': _('Crear un template de una Campaña Dialer'), 'version': '1.7.0'},
        'lista_campana_dialer_template':
            {'descripcion': _('Ver lista de templates de campaña Dialer'), 'version': '1.7.0'},
        'crea_campana_dialer_template':
            {'descripcion': _('Crear una campaña Dialer a partir de un Template'),
             'version': '1.7.0'},
        'campana_dialer_template_detalle':
            {'descripcion': _('Ver el detalle de un template de Campaña Dialer'),
             'version': '1.7.0'},
        'campana_dialer_template_elimina':
            {'descripcion': _('Eliminar un Template de Campaña Dialer'), 'version': '1.7.0'},
        'campana_manual_template_create':
            {'descripcion': _('Crear un template de una Campaña Manual'), 'version': '1.7.0'},
        'campana_manual_template_create_campana':
            {'descripcion': _('Crear una campaña Manual a partir de un Template'),
             'version': '1.7.0'},
        'campana_manual_template_list':
            {'descripcion': _('Ver lista de templates de campaña Manual'), 'version': '1.7.0'},
        'campana_manual_template_detail':
            {'descripcion': _('Ver el detalle de un template de Campaña Manual'),
             'version': '1.7.0'},
        'campana_manual_template_delete':
            {'descripcion': _('Eliminar un Template de Campaña Dialer'), 'version': '1.7.0'},
        'campana_preview_template_create':
            {'descripcion': _('Crear un template de una Campaña Preview'), 'version': '1.7.0'},
        'campana_preview_template_create_campana':
            {'descripcion': _('Crear una campaña Preview a partir de un Template'),
             'version': '1.7.0'},
        'campana_preview_template_list':
            {'descripcion': _('Ver lista de templates de campaña Preview'), 'version': '1.7.0'},
        'campana_preview_template_detail':
            {'descripcion': _('Ver el detalle de un template de Campaña Preview'),
             'version': '1.7.0'},
        'campana_preview_template_delete':
            {'descripcion': _('Eliminar un Template de Campaña Preview'), 'version': '1.7.0'},
        'lista_archivo_audio':
            {'descripcion': _('Ver la lista de Archivos de Audio'), 'version': '1.7.0'},
        'create_archivo_audio':
            {'descripcion': _('Crear un Archivo de Audio'), 'version': '1.7.0'},
        'edita_archivo_audio':
            {'descripcion': _('Editar un Archivo de Audio'), 'version': '1.7.0'},
        'eliminar_archivo_audio':
            {'descripcion': _('Eliminar un Archivo de Audio'), 'version': '1.7.0'},
        'configurar_agentes_en_campana':
            {'descripcion': _('Editar configuracion de Agentes para la campaña'),
             'version': '1.12.0'},
        'finalizar_campana_dialer':
            {'descripcion': _('Finalizar una campana dialer activa'), 'version': '1.7.0'},
        'nueva_lista_rapida':
            {'descripcion': _('Crear una nueva lista rapida de contactos'), 'version': '1.13.0'},
        'listas_rapidas':
            {'descripcion': _('Ver la lista de listas rapidas de contactos'), 'version': '1.13.0'},
        'update_lista_rapida':
            {'descripcion': _('Actualiza una lista rapida de contactos'), 'version': '1.13.0'},
        'eliminar_lista_rapida':
            {'descripcion': _('Elimina una lista rapida de contactos'), 'version': '1.13.0'},
        'define_lista_rapida':
            {'descripcion': _('Define una lista rapida de contactos'), 'version': '1.13.0'},
    }
