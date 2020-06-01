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


class OminicontactoAppConfig(AppConfig):
    name = 'ominicontacto_app'

    def configuraciones_de_permisos(self):
        return [
            {'nombre': 'consola_de_agente',
             'roles': ['Agente', ]},
            {'nombre': 'registrar_usuario',
             'roles': ['Administrador', ]},
            {'nombre': 'user_nuevo',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'user_list',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'user_delete',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'user_update',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
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
            {'nombre': 'llamadas_activas',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'supervision_agentes_logueados',
             'roles': ['Administrador', 'Gerente', 'Supervisor', ]},
            {'nombre': 'agenda_contacto_create',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contacto_detalle',
             'roles': ['Agente', ]},
            {'nombre': 'agenda_contacto_listado',
             'roles': ['Agente', ]},
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
            {'nombre': 'liberar_contacto_asignado',
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
            {'nombre': 'back_list_create',
             'roles': ['Administrador', ]},
            {'nombre': 'back_list_list',
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
            {'nombre': 'buscar_auditorias_gestion',
             'roles': ['Administrador', 'Gerente', ]},
        ]

    informacion_de_permisos = {
        'consola_de_agente':
            {'descripcion': _('Consola de Agente'), 'version': '1.6.2'},
        'registrar_usuario':
            {'descripcion': _('Registrar la llave del usuario OML'), 'version': '1.6.2'},
        'user_nuevo':
            {'descripcion': _('Crear un Usuario'), 'version': '1.6.2'},
        'user_list':
            {'descripcion': _('Ver lista de Usuarios'), 'version': '1.6.2'},
        'user_delete':
            {'descripcion': _('Borrar Usuario'), 'version': '1.6.2'},
        'user_update':
            {'descripcion': _('Editar Usuario'), 'version': '1.6.2'},
        'agente_list':
            {'descripcion': _('Ver lista de Agentes'), 'version': '1.6.2'},
        'agenteprofile_update':
            {'descripcion': _('Editar Perfil de Agente'), 'version': '1.6.2'},
        'agente_activar':
            {'descripcion': _('Activar Agente'), 'version': '1.6.2'},
        'agente_desactivar':
            {'descripcion': _('Desactivar Agente'), 'version': '1.6.2'},
        'supervisor_list':
            {'descripcion': _('Ver lista de Supervisores'), 'version': '1.6.2'},
        'supervisor_update':
            {'descripcion': _('Editar Perfil de Supervisor'), 'version': '1.6.2'},
        'cliente_webphone_list':
            {'descripcion': _('Ver lista de Clientes WebPhone'), 'version': '1.6.2'},
        'cliente_webphone_toggle_activacion':
            {'descripcion': _('Activar/Desactivar cliente WebPhone'), 'version': '1.6.2'},
        'grupo_list':
            {'descripcion': _('Ver lista de Grupos'), 'version': '1.6.2'},
        'grupo_nuevo':
            {'descripcion': _('Crear Grupo'), 'version': '1.6.2'},
        'grupo_update':
            {'descripcion': _('Modificar Grupo'), 'version': '1.6.2'},
        'grupo_delete':
            {'descripcion': _('Borrar Grupo'), 'version': '1.6.2'},
        'pausa_list':
            {'descripcion': _('Ver lista de Pausas'), 'version': '1.6.2'},
        'pausa_nuevo':
            {'descripcion': _('Crear Pausa'), 'version': '1.6.2'},
        'pausa_update':
            {'descripcion': _('Modificar Pausa'), 'version': '1.6.2'},
        'pausa_delete':
            {'descripcion': _('Borrar Pausa'), 'version': '1.6.2'},
        'grabacion_marcar':
            {'descripcion': _('Marcar la grabación en curso.'), 'version': '1.6.2'},
        'grabacion_descripcion':
            {'descripcion': _('Ver la marca (campo descripcion) de una grabacion.'),
             'version': '1.6.2'},
        'grabacion_buscar':
            {'descripcion': _('Busqueda de grabaciones por parte de un supervisor'),
             'version': '1.6.2'},
        'grabacion_agente_buscar':
            {'descripcion': _('Busqueda de grabaciones propias para Agentes'), 'version': '1.6.2'},
        'service_campanas_activas':
            {'descripcion':
             _('Lista de Campanas activas. Se usan como opciones para transferencias.'),
             'version': '1.6.2'},
        'service_agentes_de_grupo':
            {'descripcion': _('Lista de Agentes del mismo grupo que el Agente loggeado'),
             'version': '1.6.2'},
        'lista_base_datos_contacto':
            {'descripcion': _('Lista de bases de datos de contactos'), 'version': '1.6.2'},
        'nueva_base_datos_contacto':
            {'descripcion': _('Crear base de datos de contacto'), 'version': '1.6.2'},
        'update_base_datos_contacto':
            {'descripcion': _('Agregar lista de contactos a base de datos de contacto'),
             'version': '1.6.2'},
        'update_base_datos_contacto_de_campana':
            {'descripcion':
             _('Agregar lista de contactos a base de datos de contacto de una Campaña'),
             'version': '1.6.2'},
        'define_base_datos_contacto':
            {'descripcion':
             _('Define base de datos de contacto. Paso necesario al momento de la creación'),
             'version': '1.6.2'},
        'agregar_contacto':
            {'descripcion': _('Agregar un contacto a base de datos de contacto'),
             'version': '1.6.2'},
        'agregar_contacto_a_campana':
            {'descripcion': _('Agregar un contacto a base de datos de contacto de una campaña'),
             'version': '1.6.2'},
        'actualiza_base_datos_contacto':
            {'descripcion':
             _('Define base de datos de contacto. Paso necesario al momento de la creación'),
             'version': '1.6.2'},
        'actualiza_base_datos_contacto_de_campana':
            {'descripcion':
             _('Define base de datos de contacto para una campaña. Agrega contactos'),
             'version': '1.6.2'},
        'contacto_list_bd_contacto':
            {'descripcion': _('Ver lista de contactos de una Base de datos de contactos'),
             'version': '1.6.2'},
        'actualizar_contacto':
            {'descripcion': _('Actualizar un contacto'), 'version': '1.6.2'},
        'eliminar_contacto':
            {'descripcion': _('Eliminar un contacto'), 'version': '1.6.2'},
        'oculta_base_dato':
            {'descripcion': _('Ocultar una base de datos de contactos'), 'version': '1.6.2'},
        'desoculta_base_datos':
            {'descripcion': _('Desocultar una base de datos de contactos'), 'version': '1.6.2'},
        'mostrar_bases_datos_ocultas':
            {'descripcion': _('Mostrar bases de datos de contactos ocultas'), 'version': '1.6.2'},
        'bloquear_campos_para_agente':
            {'descripcion': _('Restringir campos de Contacto para Agente'), 'version': '1.6.2'},
        'contacto_list':
            {'descripcion': _('Lista de contactos para una campaña'), 'version': '1.6.2'},
        'contacto_update':
            {'descripcion': _('Actualizar un contacto'), 'version': '1.6.2'},
        'seleccion_campana_adicion_contacto':
            {'descripcion': _('Selección de campaña para agregar un contacto'), 'version': '1.6.2'},
        'nuevo_contacto_campana':
            {'descripcion': _('Crear un nuevo contacto'), 'version': '1.6.2'},
        'nuevo_contacto_campana_a_llamar':
            {'descripcion': _('Crea un nuevo contacto y luego efectua llamada'),
             'version': '1.6.2'},
        'campana_busqueda_contacto':
            {'descripcion': _('Búsqueda de contacto para agente.'), 'version': '1.6.2'},
        'campana_contactos_telefono_repetido':
            {'descripcion': _('Contactos que comparten un número de teléfono'), 'version': '1.6.2'},
        'identificar_contacto_a_llamar':
            {'descripcion': _('Identificar el contacto para la llamada'), 'version': '1.6.2'},
        'campana_entrante_template_create':
            {'descripcion': _('Crear template para campaña entrante'), 'version': '1.6.2'},
        'campana_entrante_template_create_campana':
            {'descripcion': _('Crear campaña entrante a partir de un template'),
             'version': '1.6.2'},
        'campana_entrante_template_list':
            {'descripcion': _('Ver lista de templates de campañas entrantes'), 'version': '1.6.2'},
        'campana_entrante_template_detail':
            {'descripcion': _('Ver el detalle de un template de campaña entrante'),
             'version': '1.6.2'},
        'campana_entrante_template_delete':
            {'descripcion': _('Borrar un template de campaña entrante'), 'version': '1.6.2'},
        'campana_preview_activas_miembro':
            {'descripcion': _('Pantalla para llamar contactos de campañas preview'),
             'version': '1.6.2'},
        'liberar_contacto_asignado_agente':
            {'descripcion': _('Liberar un contacto asignado en una campaña preview'),
             'version': '1.6.2'},
        'reporte_agente_calificaciones':
            {'descripcion': _('Ver calificaciones propias de Agente'), 'version': '1.6.2'},
        'exporta_reporte_calificaciones':
            {'descripcion': _('Descargar reporte de calificaciones propias de Agente'),
             'version': '1.6.2'},
        'exporta_reporte_formularios':
            {'descripcion': _('Descargar reporte de calificaciones de gestión propias de Agente'),
             'version': '1.6.2'},
        'agente_llamar_contacto':
            {'descripcion': _('Llamar a un contacto'), 'version': '1.6.2'},
        'agente_llamar_sin_campana':
            {'descripcion': _('Llamar por fuera de las campañas.'), 'version': '1.6.2'},
        'calificacion_list':
            {'descripcion': _('Ver lista de opciones de Calificación'), 'version': '1.6.2'},
        'calificacion_nuevo':
            {'descripcion': _('Crear nueva Opción de calificación'), 'version': '1.6.2'},
        'calificacion_update':
            {'descripcion': _('Modificar Opción de calificación'), 'version': '1.6.2'},
        'calificacion_delete':
            {'descripcion': _('Borrar opción de calificación'), 'version': '1.6.2'},
        'formulario_list':
            {'descripcion': _('Ver lista de Formularios de gestión'), 'version': '1.6.2'},
        'formulario_list_mostrar_ocultos':
            {'descripcion': _('Mostrar Formularios de gestión ocultos'), 'version': '1.6.2'},
        'formulario_nuevo':
            {'descripcion': _('Crear nuevo Formulario de gestión'), 'version': '1.6.2'},
        'formulario_field':
            {'descripcion': _('Crear un campo para un formulario de gestión'), 'version': '1.6.2'},
        'campo_formulario_orden':
            {'descripcion': _('Modificar el orden de los campos de un formulario de gestión'),
             'version': '1.6.2'},
        'formulario_field_delete':
            {'descripcion': _('Borrar un campo de un formulario de gestión'), 'version': '1.6.2'},
        'formulario_vista_previa':
            {'descripcion': _('Vista previa de un Formulario de gestión'), 'version': '1.6.2'},
        'formulario_eliminar':
            {'descripcion': _('Eliminar un Formulario de gestión'), 'version': '1.6.2'},
        'formulario_mostrar_ocultar':
            {'descripcion': _('Mostrar u ocultar un Formulario de gestión'), 'version': '1.6.2'},
        'formulario_vista':
            {'descripcion': _('Ver Formulario de gestión'), 'version': '1.6.2'},
        'calificar_llamada':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'calificar_llamada_con_contacto':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'calificacion_formulario_update_or_create':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'recalificacion_formulario_update_or_create':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'calificacion_cliente_actualiza_desde_reporte':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'auditar_calificacion':
            {'descripcion': _('Editar una calificacion al auditarla (Supervisor)'),
             'version': '1.6.2'},
        'calificar_por_telefono':
            {'descripcion': _('Calificar una llamada (Agente)'), 'version': '1.6.2'},
        'formulario_detalle':
            {'descripcion': _('Ver la respuesta de un Formulario de Gestión'), 'version': '1.6.2'},
        'formulario_venta':
            {'descripcion': _('Crear/editar la respuesta de un Formulario de gestión'), 'version':
             '1.6.2'},
        'auditar_formulario_venta':
            {'descripcion': _('Editar la respuesta de un formulario de gestión al auditarla'),
             'version': '1.6.2'},
        'agente_cambiar_estado':
            {'descripcion': _('Modificar el estado de un Agente en Asterisk'), 'version': '1.6.2'},
        'llamadas_activas':
            {'descripcion': _('Llamadas activas actuales'), 'version': '1.6.2'},
        'supervision_agentes_logueados':
            {'descripcion': _('Agentes logueados'), 'version': '1.6.2'},
        'agenda_contacto_create':
            {'descripcion': _('Agenda para un contacto'), 'version': '1.6.2'},
        'agenda_contacto_detalle':
            {'descripcion': _('Ver el detalle de la Agenda de un contacto'), 'version': '1.6.2'},
        'agenda_contacto_listado':
            {'descripcion': _('Listado de Agendas de contactos'), 'version': '1.6.2'},
        'campana_dialer_list':
            {'descripcion': _('Ver listado de campañas Dialer'), 'version': '1.6.2'},
        'campana_dialer_create':
            {'descripcion': _('Crear campaña Dialer'), 'version': '1.6.2'},
        'campana_dialer_update':
            {'descripcion': _('Editar campana Dialer'), 'version': '1.6.2'},
        'start_campana_dialer':
            {'descripcion': _('Dar inicio a una campaña Dialer'), 'version': '1.6.2'},
        'pausar_campana_dialer':
            {'descripcion': _('Pausar una campaña Dialer'), 'version': '1.6.2'},
        'activar_campana_dialer':
            {'descripcion': _('Activar una campaña Dialer'), 'version': '1.6.2'},
        'campana_dialer_delete':
            {'descripcion': _('Borrar una campaña Dialer'), 'version': '1.6.2'},
        'campana_dialer_ocultar':
            {'descripcion': _('Ocultar una campaña Dialer'), 'version': '1.6.2'},
        'campana_dialer_desocultar':
            {'descripcion': _('Mostrar una campaña Dialer oculta'), 'version': '1.6.2'},
        'campana_dialer_update_base':
            {'descripcion': _('Actualizar la base de datos de una Campaña Dialer'),
             'version': '1.6.2'},
        'campana_dialer_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Dialer'), 'version': '1.6.2'},
        'campana_dialer_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Dialers ocultas'), 'version': '1.6.2'},
        'campana_dialer_finaliza_activas':
            {'descripcion': _('Finalizar campañas activas que no tengan contactos pendientes'),
             'version': '1.6.2'},
        'campana_manual_list':
            {'descripcion': _('Ver listado de campañas Manuales'), 'version': '1.6.2'},
        'campana_manual_create':
            {'descripcion': _('Crear campaña Manual'), 'version': '1.6.2'},
        'campana_manual_update':
            {'descripcion': _('Editar campaña Manual'), 'version': '1.6.2'},
        'campana_manual_delete':
            {'descripcion': _('Borrar campaña Manual'), 'version': '1.6.2'},
        'campana_manual_ocultar':
            {'descripcion': _('Ocultar campaña Manual'), 'version': '1.6.2'},
        'campana_manual_desocultar':
            {'descripcion': _('Mostrar una campaña Manual oculta'), 'version': '1.6.2'},
        'campana_manual_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Manual'), 'version': '1.6.2'},
        'campana_manual_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Manuales ocultas'), 'version': '1.6.2'},
        'campana_preview_list':
            {'descripcion': _('Ver listado de campañas Preview'), 'version': '1.6.2'},
        'campana_preview_create':
            {'descripcion': _('Crear campaña Preview'), 'version': '1.6.2'},
        'campana_preview_update':
            {'descripcion': _('Editar campaña Preview'), 'version': '1.6.2'},
        'campana_preview_delete':
            {'descripcion': _('Borrar campaña Preview'), 'version': '1.6.2'},
        'campana_preview_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Preview'), 'version': '1.6.2'},
        'campana_preview_mostrar_ocultas':
            {'descripcion': _('Mostrar campañas Preview ocultas'), 'version': '1.6.2'},
        'campana_mostrar_ocultar':
            {'descripcion': _('Ocultar campaña Preview'), 'version': '1.6.2'},
        'campana_preview_dispatcher':
            {'descripcion': _('Obtener un contacto de una campaña Preview para llamarlo'),
             'version': '1.6.2'},
        'validar_contacto_asignado':
            {'descripcion':
             _('Validar que el agente tiene asignado un contacto de una campaña Preview'),
             'version': '1.6.2'},
        'contactos_preview_asignados':
            {'descripcion': _('Ver los contactos de una campaña Preview asignados a algun agente'),
             'version': '1.6.2'},
        'liberar_contacto_asignado':
            {'descripcion': _('Liberar un contacto de una campaña Preview asignado a un agente'),
             'version': '1.6.2'},
        'ordenar_entrega_contactos_preview':
            {'descripcion': _('Definir orden de asignacion de contactos de una campaña Preview'),
             'version': '1.5.2'},
        'descargar_orden_contactos_actual_preview':
            {'descripcion': _('Descargar orden de asignacion de contactos de una campaña Preview'),
             'version': '1.5.2'},
        'campana_list':
            {'descripcion': _('Ver lista de campañas Entrantes'), 'version': '1.6.2'},
        'campana_nuevo':
            {'descripcion': _('Crear campaña Entrante'), 'version': '1.6.2'},
        'campana_update':
            {'descripcion': _('Modificar campaña Entrante'), 'version': '1.6.2'},
        'campana_elimina':
            {'descripcion': _('Borrar campaña Entrante'), 'version': '1.6.2'},
        'oculta_campana':
            {'descripcion': _('Ocultar campaña Entrante'), 'version': '1.6.2'},
        'desoculta_campana':
            {'descripcion': _('Mostrar campaña Entrante oculta'), 'version': '1.6.2'},
        'campana_supervisors':
            {'descripcion': _('Asignar supervisores a una campaña Entrante'), 'version': '1.6.2'},
        'mostrar_campanas_ocultas':
            {'descripcion': _('Mostrar campañas Entrantes ocultas'), 'version': '1.6.2'},
        'back_list_create':
            {'descripcion': _('Creacion de una Blacklist'), 'version': '1.6.2'},
        'back_list_list':
            {'descripcion': _('Ver lista de Blacklists'), 'version': '1.6.2'},
        'sistema_externo_list':
            {'descripcion': _('Ver lista de Sistemas Externos'), 'version': '1.6.2'},
        'sistema_externo_create':
            {'descripcion': _('Crear un Sistema Externo'), 'version': '1.6.2'},
        'modificar_sistema_externo':
            {'descripcion': _('Modificar un Sistema Externo'), 'version': '1.6.2'},
        'sitio_externo_list':
            {'descripcion': _('Ver lista de Sitios Externos'), 'version': '1.6.2'},
        'sitio_externo_create':
            {'descripcion': _('Crear un Sitio Externo'), 'version': '1.6.2'},
        'oculta_sitio_externo':
            {'descripcion': _('Ocultar un Sitio Externo'), 'version': '1.6.2'},
        'desoculta_sitio_externo':
            {'descripcion': _('Mostrar un Sitio Externo oculto'), 'version': '1.6.2'},
        'mostrar_sitios_externo_ocultos':
            {'descripcion': _('Mostrar los Sitios Externos ocultos'), 'version': '1.6.2'},
        'modificar_sitio_externo':
            {'descripcion': _('Modificar un Sitio Externo'), 'version': '1.6.2'},
        'sitio_externo_delete':
            {'descripcion': _('Borrar un Sitio Externo'), 'version': '1.6.2'},
        'queue_member_add':
            {'descripcion': _('Agregar un Agente a una Campaña'), 'version': '1.6.2'},
        'queue_member_grupo_agente':
            {'descripcion': _('Agregar un Grupo de Agentes a una Campaña'), 'version': '1.6.2'},
        'queue_member_campana':
            {'descripcion': _('Pantalla de asignacion de Agentes a Campaña'), 'version': '1.6.2'},
        'queue_member_elimina':
            {'descripcion': _('Eliminar un Agente de una Campaña'), 'version': '1.6.2'},
        'campana_dialer_template_create':
            {'descripcion': _('Crear un template de una Campaña Dialer'), 'version': '1.6.2'},
        'lista_campana_dialer_template':
            {'descripcion': _('Ver lista de templates de campaña Dialer'), 'version': '1.6.2'},
        'crea_campana_dialer_template':
            {'descripcion': _('Crear una campaña Dialer a partir de un Template'),
             'version': '1.6.2'},
        'campana_dialer_template_detalle':
            {'descripcion': _('Ver el detalle de un template de Campaña Dialer'),
             'version': '1.6.2'},
        'campana_dialer_template_elimina':
            {'descripcion': _('Eliminar un Template de Campaña Dialer'), 'version': '1.6.2'},
        'campana_manual_template_create':
            {'descripcion': _('Crear un template de una Campaña Manual'), 'version': '1.6.2'},
        'campana_manual_template_create_campana':
            {'descripcion': _('Crear una campaña Manual a partir de un Template'),
             'version': '1.6.2'},
        'campana_manual_template_list':
            {'descripcion': _('Ver lista de templates de campaña Manual'), 'version': '1.6.2'},
        'campana_manual_template_detail':
            {'descripcion': _('Ver el detalle de un template de Campaña Manual'),
             'version': '1.6.2'},
        'campana_manual_template_delete':
            {'descripcion': _('Eliminar un Template de Campaña Dialer'), 'version': '1.6.2'},
        'campana_preview_template_create':
            {'descripcion': _('Crear un template de una Campaña Preview'), 'version': '1.6.2'},
        'campana_preview_template_create_campana':
            {'descripcion': _('Crear una campaña Preview a partir de un Template'),
             'version': '1.6.2'},
        'campana_preview_template_list':
            {'descripcion': _('Ver lista de templates de campaña Preview'), 'version': '1.6.2'},
        'campana_preview_template_detail':
            {'descripcion': _('Ver el detalle de un template de Campaña Preview'),
             'version': '1.6.2'},
        'campana_preview_template_delete':
            {'descripcion': _('Eliminar un Template de Campaña Preview'), 'version': '1.6.2'},
        'lista_archivo_audio':
            {'descripcion': _('Ver la lista de Archivos de Audio'), 'version': '1.6.2'},
        'create_archivo_audio':
            {'descripcion': _('Crear un Archivo de Audio'), 'version': '1.6.2'},
        'edita_archivo_audio':
            {'descripcion': _('Editar un Archivo de Audio'), 'version': '1.6.2'},
        'eliminar_archivo_audio':
            {'descripcion': _('Eliminar un Archivo de Audio'), 'version': '1.6.2'},
        # Auditorías
        'buscar_auditorias_gestion':
            {'descripcion': _('Acceder al listado de calificaciones a auditar'),
             'version': '1.6.2'}
    }
