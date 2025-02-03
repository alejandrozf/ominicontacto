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

from django.conf import settings
from django.urls import include, re_path, path
from django.views.static import serve
from django.contrib.auth.decorators import login_required

from ominicontacto_app import (
    views_base_de_datos_contacto, views_contacto, views_campana_creacion,
    views_grabacion, views_calificacion, views_formulario, views_agente,
    views_calificacion_cliente, views_campana, views_campana_reportes,
    views_agenda_contacto, views_campana_dialer_creacion, views_campana_dialer,
    views_black_list, views_sitio_externo, views_sitio_externo_autenticacion, views_queue_member,
    views_campana_dialer_template, views_campana_manual_creacion, views_campana_manual,
    views_campana_preview, views_archivo_de_audio, views_user_profiles, views_sistema_externo,
    views_auditorias, views_lista_rapida
)

from ominicontacto_app.views import base, grupos, instancia, autenticacion_externa

from ominicontacto_app.views_utils import (
    handler400, handler403, handler404, handler500
)

handler400 = handler400
handler403 = handler403
handler404 = handler404
handler500 = handler500


urlpatterns = [
    re_path(r'^admin/defender/', include('defender.urls')),  # defender admin

    # ==========================================================================
    # Base
    # ==========================================================================
    path('', base.index_view, name='index'),
    path('accounts/login/', base.login_view, name='login'),
    path('consola/',
         login_required(base.ConsolaAgenteView.as_view()),
         name='consola_de_agente'),
    path('blanco/',
         login_required(base.BlancoView.as_view()),
         name='view_blanco'),
    re_path(base.WebUI.repath,
            login_required(base.WebUI.as_view()),
            name="webui"),

    # ==========================================================================
    # Instancia
    # ==========================================================================
    path('acerca/',
         login_required(instancia.AcercaTemplateView.as_view()),
         name='acerca',
         ),
    path('addons/',
         login_required(instancia.AddonsInfoView.as_view()),
         name='addons_disponibles',
         ),
    path('registro/',
         login_required(instancia.RegistroFormView.as_view()),
         name='registrar_usuario',
         ),

    # ==========================================================================
    # Usuarios, Perfiles y Roles
    # ==========================================================================
    path('user/new/',
         login_required(views_user_profiles.CustomUserWizard.as_view()),
         name='user_nuevo',
         ),
    path('user/new/agent/',
         login_required(views_user_profiles.CustomUserWizard.as_view()),
         name='user_new_agent', kwargs={'create_agent': ''}
         ),
    path('user/clone/agent/<int:clone_pk>/',
         login_required(views_user_profiles.CustomUserWizard.as_view()),
         name='clone_agent'),
    path('user/list/<int:page>/',
         login_required(views_user_profiles.UserListView.as_view()),
         name='user_list'),
    path('user/list/download_csv/',
         login_required(views_user_profiles.ExportCsvUsuariosView.as_view()),
         name='descargar_usuarios_csv'),
    path('user/delete/<int:pk>',
         login_required(views_user_profiles.UserDeleteView.as_view()),
         name='user_delete'),
    path('user/update/<int:pk>',
         login_required(views_user_profiles.CustomerUserUpdateView.as_view()),
         name='user_update'),
    path('user/agent/delete/<int:pk>',
         login_required(views_user_profiles.UserDeleteView.as_view()),
         name='agent_delete', kwargs={'for_agent': ''}),
    path('user/agent/update/<int:pk>',
         login_required(views_user_profiles.CustomerUserUpdateView.as_view()),
         name='agent_update', kwargs={'for_agent': ''}),
    path('user/password/',
         login_required(views_user_profiles.CustomerUserUpdateView.as_view()),
         name='user_change_password', kwargs={'change_password': ''}),

    # Perfil Agente  ==========================================================
    path('agente/list/',
         login_required(views_user_profiles.AgenteListView.as_view()),
         name='agente_list',
         ),
    re_path(r'^user/agenteprofile/update/(?P<pk_agenteprofile>\d+)/$',
            login_required(views_user_profiles.AgenteProfileUpdateView.as_view()),
            name='agenteprofile_update',
            ),
    re_path(r'^agente/(?P<pk_agente>\d+)/activar/$',
            login_required(views_user_profiles.ActivarAgenteView.as_view()),
            name="agente_activar"),
    re_path(r'^agente/(?P<pk_agente>\d+)/desactivar/$',
            login_required(views_user_profiles.DesactivarAgenteView.as_view()),
            name="agente_desactivar"),
    # Perfil Supervisor  =======================================================
    re_path(r'^supervisor/list/(?P<page>[0-9]+)/$',
            login_required(views_user_profiles.SupervisorListView.as_view()),
            name='supervisor_list',
            ),
    re_path(r'^supervisor/(?P<pk>\d+)/update/$',
            login_required(views_user_profiles.SupervisorProfileUpdateView.as_view()),
            name='supervisor_update',
            ),
    # Perfil Webphone Cliente  ================================================
    re_path(r'^cliente_webphone/list/$',
            login_required(views_user_profiles.ClienteWebPhoneListView.as_view()),
            name='cliente_webphone_list',
            ),
    re_path(r'^agente/(?P<pk>\d+)/cambiar_estado_activacion/$',
            login_required(
                views_user_profiles.ToggleActivarClienteWebPhoneView.as_view()),
            name="cliente_webphone_toggle_activacion"),
    # Roles  ==================================================================
    re_path(r'^roles/manager/$',
            login_required(
                views_user_profiles.UserRoleManagementView.as_view()),
            name="user_role_management"),

    # ==========================================================================
    # Grupos
    # ==========================================================================
    path('grupo/list/',
         login_required(grupos.GrupoListView.as_view()), name='grupo_list',
         ),
    path('grupo/nuevo/',
         login_required(grupos.GrupoCreateView.as_view()), name='grupo_nuevo',
         ),
    path('grupo/update/<int:pk>/',
         login_required(grupos.GrupoUpdateView.as_view()),
         name='grupo_update',
         ),
    path('grupo/delete/<int:pk>/',
         login_required(grupos.GrupoDeleteView.as_view()),
         name='grupo_delete',
         ),
    path('grupo/<int:pk>/detalle/',
         login_required(grupos.GrupoDetalleView.as_view()),
         name="grupo_detalle"),
    # ==========================================================================
    # Pausas
    # ==========================================================================
    path('pausa/list/',
         login_required(base.PausaListView.as_view()),
         name='pausa_list',
         ),
    path('conjuntos_de_pausa/list/',
         login_required(base.ConjuntosDePausaListView.as_view()),
         name='conjuntos_de_pausas_list',
         ),
    # ==========================================================================
    # Grabaciones
    # ==========================================================================
    path('node/grabacion/marcar/',
         login_required(views_grabacion.MarcarGrabacionView.as_view()),
         name='grabacion_marcar',
         ),
    re_path(r'^grabacion/descripcion/(?P<callid>[\d .]+)/$',
            login_required(views_grabacion.GrabacionDescripcionView.as_view()),
            name='grabacion_descripcion',
            ),
    path('grabacion/buscar/<int:pagina>/',
         login_required(
             views_grabacion.BusquedaGrabacionSupervisorFormView.as_view()),
         name='grabacion_buscar',
         ),
    path('grabacion/agente/buscar/<int:pagina>/',
         login_required(views_grabacion.BusquedaGrabacionAgenteFormView.as_view()),
         name='grabacion_agente_buscar',
         ),


    # ==========================================================================
    # Auditorías (Backoffice)
    # ==========================================================================
    path('auditar_gestion/buscar/<int:pagina>/',
         login_required(
             views_auditorias.AuditarCalificacionesFormView.as_view()),
         name='buscar_auditorias_gestion',),
    path('auditar_gestion/editar/<int:pk_calificacion>/',
         login_required(views_auditorias.AuditoriaCalificacionFormView.as_view()),
         name='auditar_calificacion_cliente'),



    # ==========================================================================
    # Seguridad
    # ==========================================================================
    path('seguridad/auditoria/',
         login_required(views_auditorias.SeguridadAuditoriaView.as_view()),
         name='seguridad_auditoria'),
    path('security/external_authentication/',
         login_required(autenticacion_externa.ConfigurarAutenticacionExternaView.as_view()),
         name='security_external_authentication'),


    # ==========================================================================
    # Servicios para phoneJS
    # ==========================================================================
    re_path(r'^service/campana/activas/$',
            login_required(
                views_agente.CampanasActivasView.as_view()),
            name="service_campanas_activas"),

    # ==========================================================================
    # Base Datos Contacto
    # ==========================================================================
    re_path(r'^base_datos_contacto/(?P<page>[0-9]+)/$',
            login_required(
                views_base_de_datos_contacto.BaseDatosContactoListView.as_view()),
            name='lista_base_datos_contacto',
            ),
    path('base_datos_contacto/nueva',
         login_required(views_base_de_datos_contacto.BaseDatosContactoCreateView.as_view()),
         name='nueva_base_datos_contacto'
         ),
    path('base_datos_contacto/<int:pk>/borrar/',
         login_required(views_base_de_datos_contacto.BaseDatosContactoDeleteView.as_view()),
         name='delete_base_datos_contacto'
         ),
    path('base_datos_contacto/<int:pk_bd_contacto>/actualizar',
         login_required(views_base_de_datos_contacto.BaseDatosContactoUpdateView.as_view()),
         name='update_base_datos_contacto'
         ),
    path('campana/base_datos_contacto/<int:pk_campana>/actualizar',
         login_required(
             views_base_de_datos_contacto.BaseDatosContactoUpdateView.as_view()),
         name='update_base_datos_contacto_de_campana'
         ),
    re_path(r'^base_datos_contacto/(?P<pk>\d+)/validacion/$',
            login_required(
                views_base_de_datos_contacto.DefineBaseDatosContactoView.as_view()),
            name='define_base_datos_contacto',
            ),
    re_path(r'^base_datos_contacto/(?P<bd_contacto>\d+)/agregar_contacto/$',
            login_required(views_contacto.ContactoBDContactoCreateView.as_view()),
            name='agregar_contacto',
            ),
    re_path(r'^campana/base_datos_contacto/(?P<pk_campana>\d+)/agregar_contacto/$',
            login_required(views_contacto.ContactoBDContactoCreateView.as_view()),
            name='agregar_contacto_a_campana',
            ),
    re_path(r'^base_datos_contacto/(?P<pk>\d+)/validacion_actualizacion/$',
            login_required(
                views_base_de_datos_contacto.ActualizaBaseDatosContactoView.as_view()),
            name='actualiza_base_datos_contacto',
            ),
    path('campana/base_datos_contacto/<int:pk_campana>/validacion_actualizacion/',
         login_required(
             views_base_de_datos_contacto.ActualizaBaseDatosContactoView.as_view()),
         name='actualiza_base_datos_contacto_de_campana',
         ),

    re_path(r'^base_datos_contacto/(?P<bd_contacto>\d+)/list_contacto/$',
            login_required(views_contacto.ContactoBDContactoListView.as_view()),
            name='contacto_list_bd_contacto',
            ),
    re_path(r'^base_datos_contacto/(?P<pk_contacto>\d+)/update/$',
            login_required(views_contacto.ContactoBDContactoUpdateView.as_view()),
            name='actualizar_contacto',
            ),
    re_path(r'^base_datos_contacto/(?P<pk_contacto>\d+)/eliminar/$',
            login_required(views_contacto.ContactoBDContactoDeleteView.as_view()),
            name='eliminar_contacto',
            ),
    re_path(r'^base_datos_contacto/(?P<bd_contacto>\d+)/ocultar/$',
            login_required(
                views_base_de_datos_contacto.OcultarBaseView.as_view()),
            name='oculta_base_dato', ),
    re_path(r'^base_datos_contacto/(?P<bd_contacto>\d+)/desocultar/$',
            login_required(
                views_base_de_datos_contacto.DesOcultarBaseView.as_view()),
            name='desoculta_base_datos', ),
    re_path(r'^base_datos_contacto/bases_ocultas/$',
            login_required(views_base_de_datos_contacto.mostrar_bases_datos_borradas_ocultas_view),
            name='mostrar_bases_datos_ocultas', ),

    #  ===== Configuracion de BD Contacto de Campaña para supervisor ====
    re_path(r'^campana/(?P<pk_campana>\d+)/bloquear_campos_para_agente/$',
            login_required(
                views_contacto.BloquearCamposParaAgenteFormView.as_view()),
            name='bloquear_campos_para_agente',
            ),

    #  ===== Vistas de contacto para agente ====
    re_path(r'^contacto/list/$',
            login_required(views_contacto.ContactoListView.as_view()),
            name='contacto_list',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/contacto/(?P<pk_contacto>\d+)/update/$',
            login_required(views_contacto.ContactoUpdateView.as_view()),
            name='contacto_update',
            ),
    # ==========================================================================
    # Listas rapidas
    # ==========================================================================
    re_path(r'^listas_rapidas/$',
            login_required(views_lista_rapida.ListaRapidaListView.as_view()),
            name='listas_rapidas',
            ),
    re_path(r'^lista_rapida/nueva/$',
            login_required(views_lista_rapida.ListaRapidaCreateView.as_view()),
            name='nueva_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk>\d+)/validacion/$',
            login_required(
                views_lista_rapida.DefineListaRapidaView.as_view()),
            name='define_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/actualizar/$',
            login_required(views_lista_rapida.ListaRapidaUpdateView.as_view()),
            name='update_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/eliminar/$',
            login_required(views_lista_rapida.ListaRapidaDeleteView.as_view()),
            name='eliminar_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/contactos/$',
            login_required(views_lista_rapida.ListaRapidaContactosView.as_view()),
            name='contactos_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/contacto/(?P<pk>\d+)/editar/$',
            login_required(views_lista_rapida.ListaRapidaEditaContactoView.as_view()),
            name='editar_contacto_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/contacto/(?P<pk>\d+)/eliminar/$',
            login_required(views_lista_rapida.ListaRapidaEliminaContactoView.as_view()),
            name='eliminar_contacto_lista_rapida',
            ),
    re_path(r'^lista_rapida/(?P<pk_lista_rapida>\d+)/contacto/nuevo/$',
            login_required(views_lista_rapida.ListaRapidaNuevoContactoView.as_view()),
            name='nuevo_contacto_lista_rapida',
            ),
    # ==========================================================================
    #  Vistas de manipulación de contactos de una campaña / Para agente
    # ==========================================================================
    re_path(r'^campana/selecciona/$',
            login_required(
                views_contacto.FormularioSeleccionCampanaFormView.as_view()),
            name='seleccion_campana_adicion_contacto',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/nuevo_contacto/$',
            login_required(
                views_contacto.FormularioNuevoContactoFormView.as_view()),
            name='nuevo_contacto_campana',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/nuevo_contacto_a_llamar/(?P<telefono>\d+)/$',
            login_required(
                views_contacto.FormularioNuevoContactoFormView.as_view()),
            name='nuevo_contacto_campana_a_llamar', kwargs={'accion': 'llamar'}
            ),
    # TODO: Ver si se usa esa vista para algo
    re_path(r'^campana/(?P<pk_campana>\d+)/busqueda_contacto/$',
            login_required(
                views_contacto.CampanaBusquedaContactoFormView.as_view()),
            name="campana_busqueda_contacto"),
    re_path(r'^campana/(?P<pk_campana>\d+)/contactos_telefono_repetido/(?P<telefono>\d+)'
            r'/(?P<call_data_json>.+)$',
            login_required(
                views_contacto.ContactosTelefonosRepetidosView.as_view()),
            name="campana_contactos_telefono_repetido"),
    re_path(r'^campana/(?P<pk_campana>\d+)/identificar_contacto_a_llamar/(?P<telefono>[0-9*#]+)/$',
            login_required(views_contacto.IdentificarContactoView.as_view()),
            name="identificar_contacto_a_llamar"),


    # ==========================================================================
    #  Templates Campana Entrante
    # ==========================================================================
    re_path(r'^campana_entrante_template/crear/$',
            login_required(
                views_campana_creacion.CampanaEntranteTemplateCreateView.as_view()),
            name="campana_entrante_template_create"),
    re_path(r'^campana_entrante_template/crear_campana/(?P<pk_campana_template>\d+)$',
            login_required(
                views_campana_creacion.CampanaEntranteTemplateCreateCampanaView.as_view()),
            name="campana_entrante_template_create_campana"),
    re_path(r'^campana_entrante_template/lista/$',
            login_required(
                views_campana_creacion.CampanaEntranteTemplateListView.as_view()),
            name="campana_entrante_template_list"),
    re_path(r'^campana_entrante_template/detalle/(?P<pk>\d+)/$',
            login_required(
                views_campana_creacion.CampanaEntranteTemplateDetailView.as_view()),
            name="campana_entrante_template_detail"),
    re_path(r'^campana_entrante_template/elimina/(?P<pk>\d+)/$',
            login_required(
                views_campana_creacion.CampanaEntranteTemplateDeleteView.as_view()),
            name="campana_entrante_template_delete"),
    # ==========================================================================
    # Vistas varias para Agente: Reportes, logout
    # ==========================================================================
    re_path(r'^agente/campanas_preview/activas/$',
            login_required(
                views_agente.AgenteCampanasPreviewActivasView.as_view()),
            name="campana_preview_activas_miembro"),
    re_path(r'^agente/campanas_preview/liberar_contacto_asignado/$',
            login_required(
                views_agente.LiberarContactoAsignado.as_view()),
            name="liberar_contacto_asignado_agente"),
    re_path(r'^agente/reporte/calificaciones/$',
            login_required(
                views_agente.AgenteReporteCalificaciones.as_view()),
            name='reporte_agente_calificaciones',
            ),
    re_path(r'^agente/(?P<pk_agente>\d+)/exporta/calificaciones/$',
            login_required(
                views_agente.ExportaReporteCalificacionView.as_view()),
            name='exporta_reporte_calificaciones',
            ),
    re_path(r'^agente/(?P<pk_agente>\d+)/exporta/formularios/$',
            login_required(
                views_agente.ExportaReporteFormularioVentaView.as_view()),
            name='exporta_reporte_formularios',
            ),
    re_path(r'^agente/llamar/$',
            login_required(
                views_agente.LlamarContactoView.as_view()),
            name='agente_llamar_contacto',
            ),
    re_path(r'^agente/llamar_sin_campana/$',
            login_required(
                views_agente.LlamarFueraDeCampanaView.as_view()),
            name='agente_llamar_sin_campana',
            ),
    re_path(r'^agente/update_password/$',
            login_required(
                views_agente.UpdateAgentPasswordView.as_view()),
            name='update_agent_password',
            ),
    # ==========================================================================
    # Calificacion
    # ==========================================================================
    re_path(r'^calificacion/list/$',
            login_required(views_calificacion.CalificacionListView.as_view()),
            name='calificacion_list',
            ),

    # ==========================================================================
    # Formulario
    # ==========================================================================
    re_path(r'^formulario/list/$',
            login_required(views_formulario.FormularioListView.as_view()),
            name='formulario_list',
            ),
    re_path(r'^formulario/(?P<pk_formulario>\d+)/vista_previa/$',
            login_required(views_formulario.FormularioPreviewFormView.as_view()),
            name='formulario_vista_previa',
            ),
    # TODO: Verificar si se usa esta vista.
    # re_path(r'^formulario/(?P<pk_formulario>\d+)/create/(?P<pk_campana>\d+)/(?P<pk_contacto>\d+)'
    #     r'/(?P<id_agente>\d+)/$',
    #     login_required(views_formulario.FormularioCreateFormView.as_view()),
    #     name='formulario_create',
    #     ),
    # ==========================================================================
    # Proceso de Calificación
    # CalificacionCliente / Formulario de Calif. de Gestión
    # ==========================================================================
    re_path(r'^agente/calificar_llamada/(?P<call_data_json>.+)$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'calificacion'},
            name='calificar_llamada'
            ),
    re_path(r'^agente/calificar_llamada_con_contacto/(?P<pk_contacto>\d+)/(?P<call_data_json>.+)$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'calificacion'},
            name='calificar_llamada_con_contacto'
            ),

    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/update_calificacion/(?P<call_data_json>.+)$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'calificacion'},
            name='calificacion_formulario_update_or_create'
            ),
    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/update_calificacion/$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'calificacion'},
            name='calificacion_formulario_update_or_create'
            ),
    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/update_recalificacion/(?P<call_data_json>.+)$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'recalificacion'},
            name='recalificacion_formulario_update_or_create'
            ),
    # Duplico URL por error de parametros opcionales en Python 3.6
    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/update_recalificacion/$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'recalificacion'},
            name='recalificacion_formulario_update_or_create'
            ),
    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/update_reporte/$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'reporte'},
            name='calificacion_cliente_actualiza_desde_reporte'
            ),

    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
            '/auditar_calificacion/$',
            login_required(
                views_calificacion_cliente.AuditarCalificacionClienteFormView.as_view()),
            kwargs={'from': 'audita_supervisor'},
            name='auditar_calificacion'
            ),

    # TODO: Una vez que todas las manuales sean click to call ya no existirá esta vista
    # Mientras, quedará para ser usada únicamente en llamadas manuales
    re_path(r'^formulario/(?P<pk_campana>\d+)/calificacion_create/(?P<telefono>\d+)/$',
            login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
            kwargs={'from': 'calificacion', 'pk_contacto': None, 'manual': True},
            name="calificar_por_telefono"),

    # Respuesta de Formulario para Calificación de Gestión
    re_path(r'^formulario/venta/(?P<pk>\d+)/detalle/(?P<call_data_json>.+)$',
            login_required(
                views_calificacion_cliente.RespuestaFormularioDetailView.as_view()),
            name='formulario_detalle'
            ),
    # Duplico URL por error de parametros opcionales en Python 3.6
    re_path(r'^formulario/venta/(?P<pk>\d+)/detalle/$',
            login_required(
                views_calificacion_cliente.RespuestaFormularioDetailView.as_view()),
            name='formulario_detalle'
            ),
    re_path(r'^formulario/venta/(?P<pk_calificacion>\d+)/(?P<call_data_json>.+)$',
            login_required(
                views_calificacion_cliente.RespuestaFormularioCreateUpdateAgenteFormView.as_view()),
            name='formulario_venta'
            ),
    # Duplico URL por error de parametros opcionales en Python 3.6
    re_path(r'^formulario/venta/(?P<pk_calificacion>\d+)/$',
            login_required(
                views_calificacion_cliente.RespuestaFormularioCreateUpdateAgenteFormView.as_view()),
            name='formulario_venta'
            ),
    re_path(
        r'^formulario/auditar_venta/(?P<pk_calificacion>\d+)/$',
        login_required(
            views_calificacion_cliente.RespuestaFormularioCreateUpdateSupervisorFormView.as_view()),
        name='auditar_formulario_venta'
    ),
    # ==========================================================================
    # Agente
    # ==========================================================================
    re_path(r'^agente/dashboard/$',
            login_required(views_agente.DashboardAgenteView.as_view()),
            name='agente_dashboard',
            ),
    # ==========================================================================
    # Supervision
    # ==========================================================================
    # Vistas utilizadas en la supervision PHP.
    # TODO: Mover e implementar mejora en supervision_app o en api_app segun corresponda
    re_path(r'^llamadas/activas/$',
            login_required(views_campana_reportes.LlamadasActivasView.as_view()),
            name='llamadas_activas',
            ),
    re_path(r'^supervision/agentes/campana/(?P<campana_id>\d+)$',
            login_required(views_agente.AgentesLogueadosCampana.as_view()),
            name='supervision_agentes_logueados',
            ),
    # ==========================================================================
    # Agenda Contacto
    # ==========================================================================
    re_path(r'^agenda_contacto/(?P<pk_contacto>\d+)/create/(?P<pk_campana>\d+)/$',
            login_required(views_agenda_contacto.AgendaContactoCreateView.as_view()),
            name="agenda_contacto_create"),
    re_path(r'^agenda_contacto/update/(?P<pk>\d+)/$',
            login_required(views_agenda_contacto.AgendaContactoUpdateView.as_view()),
            name="agenda_contacto_update"),
    re_path(r'^agenda_contacto/(?P<pk>\d+)/detalle/$',
            login_required(views_agenda_contacto.AgendaContactoDetailView.as_view()),
            name="agenda_contacto_detalle"),
    re_path(r'^agenda_contacto/eventos/$',
            login_required(views_agenda_contacto.AgendaContactoListFormView.as_view()),
            name="agenda_contacto_listado"),
    re_path(r'^campana/(?P<pk_campana>\d+)/agenda_contacto/list/$',
            login_required(views_agenda_contacto.AgendaContactosPorCampanaView.as_view()),
            name="agenda_contactos_por_campana"),

    # ==========================================================================
    # Campana Dialer
    # ==========================================================================
    path('campana_dialer/list',
         login_required(views_campana_dialer.CampanaDialerListView.as_view()),
         name="campana_dialer_list"),
    path('campana_dialer/create',
         login_required(views_campana_dialer_creacion.CampanaDialerCreateView.as_view()),
         name="campana_dialer_create"),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/update/$',
            login_required(
                views_campana_dialer_creacion.CampanaDialerUpdateView.as_view()),
            name="campana_dialer_update"),
    re_path(r'^campana_dialer/start/$',
            login_required(
                views_campana_dialer.PlayCampanaDialerView.as_view()),
            name='start_campana_dialer'),
    re_path(r'^campana_dialer/pausar/$',
            login_required(
                views_campana_dialer.PausarCampanaDialerView.as_view()),
            name='pausar_campana_dialer'),
    re_path(r'^campana_dialer/activar/$',
            login_required(
                views_campana_dialer.ActivarCampanaDialerView.as_view()),
            name='activar_campana_dialer'),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/delete/$',
            login_required(
                views_campana_dialer.CampanaDialerDeleteView.as_view()),
            name="campana_dialer_delete"),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/ocultar/$',
            login_required(
                views_campana_dialer.OcultarCampanaDialerView.as_view()),
            name="campana_dialer_ocultar"),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/desocultar/$',
            login_required(
                views_campana_dialer.DesOcultarCampanaDialerView.as_view()),
            name="campana_dialer_desocultar"),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/update_base/$',
            login_required(
                views_campana_dialer.UpdateBaseDatosDialerView.as_view()),
            name="campana_dialer_update_base"),
    path('campana_dialer/<int:pk_campana>/supervisors',
         login_required(views_campana_dialer.CampanaDialerSupervisorUpdateView.as_view()),
         name="campana_dialer_supervisors"),
    path('campana_dialer/mostrar_ocultas',
         login_required(views_campana_dialer.CampanaDialerBorradasListView.as_view()),
         name="campana_dialer_mostrar_ocultas"),
    re_path(r'^campana_dialer/finaliza_actovas/$',
            login_required(
                views_campana_dialer.FinalizarCampanasActivasView.as_view()),
            name="campana_dialer_finaliza_activas"),
    re_path(r'^campana_dialer/finalizar/$',
            login_required(
                views_campana_dialer.FinalizarCampanaDialerView.as_view()),
            name="finalizar_campana_dialer"),
    re_path(r'^campana_dialer/reglas_incidencia_calificacion/(?P<pk_campana>\d+)/lista/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaDeCalificacionesListView.as_view()),
            name="disposition_incidence_list"),
    re_path(r'^campana_dialer/reglas_incidencia_calificacion/(?P<pk>\d+)/borrar/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaDeCalificacionesDeleteView.as_view()),
            name="disposition_incidence_delete"),
    re_path(r'^campana_dialer/reglas_incidencia_calificacion/(?P<pk_campana>\d+)/crear/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaDeCalificacionesCreateView.as_view()),
            name="disposition_incidence_create"),
    re_path(r'^campana_dialer/reglas_incidencia_calificacion/(?P<pk>\d+)/editar/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaDeCalificacionesUpdateView.as_view()),
            name="disposition_incidence_edit"),
    re_path(r'^campana_dialer/reglas_incidencia/(?P<pk>\d+)/borrar/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaDeleteView.as_view()),
            name="incidence_delete"),
    re_path(r'^campana_dialer/reglas_incidencia/(?P<pk_campana>\d+)/crear/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaCreateView.as_view()),
            name="incidence_create"),
    re_path(r'^campana_dialer/reglas_incidencia/(?P<pk>\d+)/editar/$',
            login_required(
                views_campana_dialer.ReglasDeIncidenciaUpdateView.as_view()),
            name="incidence_edit"),


    # ==========================================================================
    # Campana Manual
    # ==========================================================================
    path('campana_manual/lista',
         login_required(views_campana_manual.CampanaManualListView.as_view()),
         name="campana_manual_list"),
    path('campana_manual/create',
         login_required(views_campana_manual_creacion.CampanaManualCreateView.as_view()),
         name="campana_manual_create"),
    re_path(r'^campana_manual/(?P<pk_campana>\d+)/update/$',
            login_required(
                views_campana_manual_creacion.CampanaManualUpdateView.as_view()),
            name="campana_manual_update"),
    re_path(r'^campana_manual/(?P<pk_campana>\d+)/delete/$',
            login_required(
                views_campana_manual.CampanaManualDeleteView.as_view()),
            name="campana_manual_delete"),
    re_path(r'^campana_manual/(?P<pk_campana>\d+)/ocultar/$',
            login_required(
                views_campana_manual.OcultarCampanaManualView.as_view()),
            name="campana_manual_ocultar"),
    re_path(r'^campana_manual/(?P<pk_campana>\d+)/desocultar/$',
            login_required(
                views_campana_manual.DesOcultarCampanaManualView.as_view()),
            name="campana_manual_desocultar"),
    path('campana_manual/<int:pk_campana>/supervisors',
         login_required(views_campana_manual.CampanaManualSupervisorUpdateView.as_view()),
         name="campana_manual_supervisors"),
    path('campana_manual/mostrar_ocultas',
         login_required(views_campana_manual.CampanaManualBorradasListView.as_view()),
         name="campana_manual_mostrar_ocultas"),
    # ==========================================================================
    # Campana Preview
    # ==========================================================================
    path('campana_preview/lista',
         login_required(views_campana_preview.CampanaPreviewListView.as_view()),
         name="campana_preview_list"),
    path('campana_preview/create',
         login_required(views_campana_preview.CampanaPreviewCreateView.as_view()),
         name="campana_preview_create"),
    re_path(r'^campana_preview/(?P<pk_campana>\d+)/update/$',
            login_required(
                views_campana_preview.CampanaPreviewUpdateView.as_view()),
            name="campana_preview_update"),
    re_path(r'^campana_preview/(?P<pk_campana>\d+)/delete/$',
            login_required(
                views_campana_preview.CampanaPreviewDeleteView.as_view()),
            name="campana_preview_delete"),
    path('campana_preview/<int:pk_campana>/supervisors',
         login_required(views_campana_preview.CampanaPreviewSupervisorUpdateView.as_view()),
         name="campana_preview_supervisors"),
    path('campana_preview/mostrar_ocultas',
         login_required(views_campana_preview.CampanaPreviewBorradasListView.as_view()),
         name="campana_preview_mostrar_ocultas"),
    re_path(r'^campana/mostrar_ocultar/(?P<pk_campana>\d+)/$',
            login_required(
                views_campana_preview.campana_mostrar_ocultar_view),
            name="campana_mostrar_ocultar"),
    re_path(r'^campana_preview/(?P<pk_campana>\d+)/contacto/obtener/$',
            login_required(
                views_campana_preview.ObtenerContactoView.as_view()),
            name="campana_preview_dispatcher"),
    re_path(r'^campana_preview/validar_contacto_asignado/$',
            login_required(
                views_campana_preview.campana_validar_contacto_asignado_view),
            name="validar_contacto_asignado"),
    re_path(r'^campana_preview/contactos_asignados/(?P<pk_campana>\d+)/$',
            login_required(
                views_campana_preview.CampanaPreviewContactosAsignados.as_view()),
            name="contactos_preview_asignados"),
    re_path(r'^campana_preview/liberar_reservar_contacto_asignado/$',
            login_required(
                views_campana_preview.LiberarReservarContactoAsignado.as_view()),
            name="liberar_reservar_contacto_asignado"),
    re_path(r'^campana_preview/ordenar_contactos_asignados/(?P<pk_campana>\d+)/$',
            login_required(
                views_campana_preview.OrdenarAsignacionContactosView.as_view()),
            name="ordenar_entrega_contactos_preview"),
    re_path(r'^campana_preview/descargar_asignacion_contactos/(?P<pk_campana>\d+)/$',
            login_required(
                views_campana_preview.DescargarOrdenAgentesEnContactosView.as_view()),
            name="descargar_orden_contactos_actual_preview"),
    re_path(r'^campana_preview/finalizar/$',
            login_required(
                views_campana_preview.FinalizarCampanaPreviewView.as_view()),
            name="finalizar_campana_preview"),
    # ==========================================================================
    # Campana Entrante
    # ==========================================================================
    path('campana/list',
         login_required(views_campana.CampanaListView.as_view()),
         name='campana_list'),
    path('campana/nuevo',
         login_required(views_campana_creacion.CampanaEntranteCreateView.as_view()),
         name='campana_nuevo'),
    re_path(r'^campana/(?P<pk_campana>\d+)/update/$',
            login_required(
                views_campana_creacion.CampanaEntranteUpdateView.as_view()),
            name='campana_update',
            ),
    re_path(r'^campana/elimina/(?P<pk_campana>\d+)/$',
            login_required(views_campana.CampanaDeleteView.as_view()),
            name='campana_elimina',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/ocultar/$',
            login_required(views_campana.OcultarCampanaView.as_view()),
            name='oculta_campana', ),
    re_path(r'^campana/(?P<pk_campana>\d+)/desocultar/$',
            login_required(views_campana.DesOcultarCampanaView.as_view()),
            name='desoculta_campana', ),
    path('campana/<int:pk_campana>/supervisors',
         login_required(views_campana.CampanaSupervisorUpdateView.as_view()),
         name="campana_supervisors"),
    path('campana/mostrar_ocultas',
         login_required(views_campana.CampanaBorradasListView.as_view()),
         name="mostrar_campanas_ocultas"),
    # ==========================================================================
    # Blacklist
    # ==========================================================================
    re_path(r'^blacklist/nueva/$',
            login_required(views_black_list.BlacklistCreateView.as_view()),
            name="black_list_create"),
    re_path(r'^blacklist/lista/$',
            login_required(views_black_list.BlacklistView.as_view()),
            name="black_list_list"),
    re_path(r'^blacklist/(?P<pk_blacklist>\d+)/actualizar/$',
            login_required(views_black_list.BlacklistUpdateView.as_view()),
            name='update_blacklist',
            ),
    re_path(r'^blacklist/(?P<pk_blacklist>\d+)/eliminar/$',
            login_required(views_black_list.BlacklistDeleteView.as_view()),
            name='eliminar_blacklist',
            ),
    re_path(r'^blacklist/(?P<pk_blacklist>\d+)/contacto/nuevo/$',
            login_required(views_black_list.BlacklistNuevoContactoView.as_view()),
            name='nuevo_contacto_blacklist',
            ),

    # ==========================================================================
    # Sistema Externo
    # ==========================================================================
    re_path(r'^sistema_externo/list/$',
            login_required(views_sistema_externo.SistemaExternoListView.as_view()),
            name="sistema_externo_list"),
    # ==========================================================================
    # Sitio Externo
    # ==========================================================================
    re_path(r'^sitio_externo/list/$',
            login_required(views_sitio_externo.SitioExternoListView.as_view()),
            name="sitio_externo_list"),
    # ==========================================================================
    # Autenticacion Sitio Externo
    # ==========================================================================
    re_path(r'^sitio_externo_autenticacion/list/$',
            login_required(
                views_sitio_externo_autenticacion.SitioExternoAutenticacionListView.as_view()),
            name="sitio_externo_autenticacion_list"),
    # ==========================================================================
    # QueueMember
    # ==========================================================================
    path('queue_member/<int:pk_campana>/queue_member_campana/',
         login_required(views_queue_member.QueueMemberCampanaView.as_view()),
         name='queue_member_campana',
         ),

    # ==========================================================================
    # Campana Dialer Template
    # ==========================================================================
    re_path(r'^campana_dialer_template/create/$',
            login_required(
                views_campana_dialer_template.CampanaDialerTemplateCreateView.as_view()),
            name="campana_dialer_template_create"),
    re_path(r'^campana_dialer_template/lista/$',
            login_required(
                views_campana_dialer_template.TemplateListView.as_view()),
            name="lista_campana_dialer_template"),
    re_path(r'^campana_dialer_template/(?P<pk_campana_template>\d+)/crea_campana/'
            r'(?P<borrar_template>\d+)/$',
            login_required(
                views_campana_dialer_template.CampanaDialerTemplateCreateCampanaView.as_view()),
            name="crea_campana_dialer_template"),
    re_path(r'^campana_dialer_template/(?P<pk>\d+)/detalle/$',
            login_required(
                views_campana_dialer_template.TemplateDetailView.as_view()),
            name="campana_dialer_template_detalle"),
    re_path(r'^campana_dialer_template/(?P<pk_campana>\d+)/elimina/$',
            login_required(
                views_campana_dialer_template.TemplateDeleteView.as_view()),
            name="campana_dialer_template_elimina"),
    # ==========================================================================
    #  Templates Campana Manual
    # ==========================================================================
    re_path(r'^campana_manual_template/crear/$',
            login_required(
                views_campana_manual_creacion.CampanaManualTemplateCreateView.as_view()),
            name="campana_manual_template_create"),
    re_path(r'^campana_manual_template/crear_campana/(?P<pk_campana_template>\d+)$',
            login_required(
                views_campana_manual_creacion.CampanaManualTemplateCreateCampanaView.as_view()),
            name="campana_manual_template_create_campana"),
    re_path(r'^campana_manual_template/lista/$',
            login_required(
                views_campana_manual_creacion.CampanaManualTemplateListView.as_view()),
            name="campana_manual_template_list"),
    re_path(r'^campana_manual_template/detalle/(?P<pk>\d+)/$',
            login_required(
                views_campana_manual_creacion.CampanaManualTemplateDetailView.as_view()),
            name="campana_manual_template_detail"),
    re_path(r'^campana_manual_template/elimina/(?P<pk>\d+)/$',
            login_required(
                views_campana_manual_creacion.CampanaManualTemplateDeleteView.as_view()),
            name="campana_manual_template_delete"),
    # ==========================================================================
    #  Templates Campana Preview
    # ==========================================================================
    re_path(r'^campana_preview_template/crear/$',
            login_required(
                views_campana_preview.CampanaPreviewTemplateCreateView.as_view()),
            name="campana_preview_template_create"),
    re_path(r'^campana_preview_template/crear_campana/(?P<pk_campana_template>\d+)/'
            r'(?P<borrar_template>\d+)$',
            login_required(
                views_campana_preview.CampanaPreviewTemplateCreateCampanaView.as_view()),
            name="campana_preview_template_create_campana"),
    re_path(r'^campana_preview_template/lista/$',
            login_required(
                views_campana_preview.CampanaPreviewTemplateListView.as_view()),
            name="campana_preview_template_list"),
    re_path(r'^campana_preview_template/detalle/(?P<pk>\d+)/$',
            login_required(
                views_campana_preview.CampanaPreviewTemplateDetailView.as_view()),
            name="campana_preview_template_detail"),
    re_path(r'^campana_preview_template/elimina/(?P<pk>\d+)/$',
            login_required(
                views_campana_preview.CampanaPreviewTemplateDeleteView.as_view()),
            name="campana_preview_template_delete"),

    # ==========================================================================
    # Archivo de Audio
    # ==========================================================================
    path('audios/',
         login_required(
             views_archivo_de_audio.ArchivoAudioListView.as_view()),
         name='lista_archivo_audio',
         ),
    path('audios/create/',
         login_required(
             views_archivo_de_audio.ArchivoAudioCreateView.as_view()),
         name='create_archivo_audio',
         ),
    path('audios/<int:pk>/update/',
         login_required(
             views_archivo_de_audio.ArchivoAudioUpdateView.as_view()),
         name='edita_archivo_audio',
         ),
    path('audios/<int:pk>/eliminar/',
         login_required(
             views_archivo_de_audio.ArchivoAudioDeleteView.as_view()),
         name='eliminar_archivo_audio',
         ),

    # ==========================================================================
    # Configuracion de agentes en campaña
    # ==========================================================================
    re_path(r'^campana/configurar-agentes/(?P<pk_campana>\d+)/$',
            login_required(
                views_campana.ConfiguracionDeAgentesDeCampanaView.as_view()),
            name='configurar_agentes_en_campana',
            ),

]

urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), ]

if settings.DEBUG:
    #     # static files (images, css, javascript, etc.)
    #     urlpatterns += patterns('',
    #         (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    #             'document_root': settings.MEDIA_ROOT}))

    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
