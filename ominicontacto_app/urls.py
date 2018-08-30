# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include
from django.views.static import serve
from django.contrib.auth.decorators import login_required

from ominicontacto_app import (
    views, views_base_de_datos_contacto, views_contacto, views_campana_creacion,
    views_grabacion, views_calificacion, views_formulario, views_agente,
    views_calificacion_cliente, views_campana, views_campana_reportes, views_pdf,
    views_agenda_contacto, views_campana_dialer_creacion, views_campana_dialer,
    views_back_list, views_sitio_externo, views_queue_member, views_user_api_crm, views_supervisor,
    views_campana_dialer_template, views_campana_manual_creacion, views_campana_manual,
    views_campana_preview, views_archivo_de_audio
)

from ominicontacto_app.views_utils import (
    handler400, handler403, handler404, handler500
)

from ominicontacto_app.auth.decorators import (
    administrador_requerido, administrador_o_supervisor_requerido, agente_requerido,
    permiso_administracion_requerido, supervisor_requerido)

handler400 = handler400
handler403 = handler403
handler404 = handler404
handler500 = handler500


urlpatterns = [
    url(r'^admin/defender/', include('defender.urls')),  # defender admin
    url(r'^ajax/mensaje_recibidos/',
        views.mensajes_recibidos_view,
        name='ajax_mensaje_recibidos'),
    url(r'^$', views.index_view, name='index'),

    # ==========================================================================
    # Usuarios y Perfiles
    # ==========================================================================
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^user/nuevo/$',
        administrador_o_supervisor_requerido(views.CustomerUserCreateView.as_view()),
        name='user_nuevo',
        ),
    url(r'^user/list/page(?P<page>[0-9]+)/$',
        administrador_o_supervisor_requerido(views.UserListView.as_view()),
        name='user_list'
        ),
    url(r'^user/delete/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views.UserDeleteView.as_view()),
        name='user_delete',
        ),
    url(r'^user/update/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views.CustomerUserUpdateView.as_view()),
        name='user_update',
        ),
    # Perfil Agente  ==========================================================
    url(r'^agente/list/$',
        administrador_o_supervisor_requerido(views.AgenteListView.as_view()), name='agente_list',
        ),
    url(r'^user/agenteprofile/nuevo/(?P<pk_user>\d+)/$',
        administrador_requerido(views.AgenteProfileCreateView.as_view()),
        name='agenteprofile_nuevo',
        ),
    url(r'^user/agenteprofile/update/(?P<pk_agenteprofile>\d+)/$',
        administrador_requerido(views.AgenteProfileUpdateView.as_view()),
        name='agenteprofile_update',
        ),
    # Perfil Supervisor  =======================================================
    url(r'^supervisor/list/$',
        administrador_requerido(views_supervisor.SupervisorListView.as_view()),
        name='supervisor_list',
        ),
    url(r'^supervisor/(?P<pk_user>\d+)/create/$',
        administrador_requerido(views_supervisor.SupervisorProfileCreateView.as_view()),
        name='supervisor_create',
        ),
    url(r'^supervisor/(?P<pk>\d+)/update/$',
        administrador_requerido(views_supervisor.SupervisorProfileUpdateView.as_view()),
        name='supervisor_update',
        ),
    # ==========================================================================
    # Módulos
    # ==========================================================================
    url(r'^modulo/nuevo/$',
        administrador_requerido(views.ModuloCreateView.as_view()), name='modulo_nuevo',
        ),
    url(r'^modulo/update/(?P<pk>\d+)/$',
        administrador_requerido(views.ModuloUpdateView.as_view()),
        name='modulo_update',
        ),
    url(r'^modulo/list/$',
        administrador_requerido(views.ModuloListView.as_view()), name='modulo_list',
        ),
    url(r'^modulo/delete/(?P<pk>\d+)/$',
        administrador_requerido(views.ModuloDeleteView.as_view()),
        name='modulo_delete',
        ),
    # ==========================================================================
    # Grupos
    # ==========================================================================
    url(r'^grupo/list/$',
        administrador_o_supervisor_requerido(views.GrupoListView.as_view()), name='grupo_list',
        ),
    url(r'^grupo/nuevo/$',
        administrador_requerido(views.GrupoCreateView.as_view()), name='grupo_nuevo',
        ),
    url(r'^grupo/update/(?P<pk>\d+)/$',
        administrador_requerido(views.GrupoUpdateView.as_view()),
        name='grupo_update',
        ),
    url(r'^grupo/delete/(?P<pk>\d+)/$',
        administrador_requerido(views.GrupoDeleteView.as_view()),
        name='grupo_delete',
        ),
    # ==========================================================================
    # Pausas
    # ==========================================================================
    url(r'^pausa/list/$',
        administrador_o_supervisor_requerido(views.PausaListView.as_view()),
        name='pausa_list',
        ),
    url(r'^pausa/nuevo/$',
        administrador_o_supervisor_requerido(views.PausaCreateView.as_view()),
        name='pausa_nuevo',
        ),
    url(r'^pausa/update/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views.PausaUpdateView.as_view()),
        name='pausa_update',
        ),
    url(r'^pausa/delete/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views.PausaToggleDeleteView.as_view()),
        name='pausa_delete',
        ),

    url(r'^node/$', login_required(views.node_view), name='view_node'),

    url(r'^smsThread/$',
        login_required(views.mensajes_recibidos_enviado_remitente_view),
        name='view_sms_thread'),
    url(r'^sms/getAll/$',
        login_required(views.mensajes_recibidos_view),
        name='view_sms_get_all'),
    url(r'^blanco/$',
        login_required(views.blanco_view),
        name='view_blanco'),

    # ==========================================================================
    # Grabaciones
    # ==========================================================================
    url(r'^node/grabacion/marcar/$',
        login_required(views_grabacion.MarcarGrabacionView.as_view()),
        name='grabacion_marcar',
        ),
    url(r'^grabacion/descripcion/(?P<uid>[\d .]+)/$',
        login_required(views_grabacion.GrabacionDescripcionView.as_view()),
        name='grabacion_descripcion',
        ),
    url(r'^grabacion/buscar/(?P<pagina>\d+)/$',
        permiso_administracion_requerido(views_grabacion.BusquedaGrabacionFormView.as_view()),
        name='grabacion_buscar',
        ),

    url(r'^agenda/nuevo/$',
        agente_requerido(views.nuevo_evento_agenda_view),
        name='agenda_nuevo',
        ),
    url(r'^agenda/agente_list/$',
        agente_requerido(views.AgenteEventosFormView.as_view()),
        name='agenda_agente_list',
        ),

    # TODO: Se puede Eliminar esta vista?
    # url(r'^regenerar_asterisk/$', views.regenerar_asterisk_view,
    #    name='regenerar_asterisk'),

    url(r'^duracion/llamada/$',
        login_required(views.nuevo_duracion_llamada_view),
        name='nueva_duracion_llamada',
        ),
    url(r'^chat/mensaje/$',
        login_required(views.mensaje_chat_view),
        name='nueva_mensaje_chat',
        ),
    url(r'^chat/create/$',
        login_required(views.crear_chat_view),
        name='chat_create',
        ),
    url(r'^supervision_externa/$',
        supervisor_requerido(views.supervision_url_externa),
        name='supervision_externa_url',
        ),
    url(r'^acerca/$',
        login_required(views.AcercaTemplateView.as_view()),
        name='acerca',
        ),
    # ==========================================================================
    # Servicios para phoneJS
    # ==========================================================================
    url(r'^service/campana/activas/$',
        login_required(
            views_agente.CampanasActivasView.as_view()),
        name="service_campanas_activas"),
    url(r'^service/agente/otros_agentes_de_grupo/$',
        login_required(
            views_agente.AgentesDeGrupoPropioView.as_view()),
        name="service_agentes_de_grupo"),
    # ==========================================================================
    # Base Datos Contacto
    # ==========================================================================
    url(r'^base_datos_contacto/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.BaseDatosContactoListView.as_view()),
        name='lista_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/nueva/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.BaseDatosContactoCreateView.as_view()),
        name='nueva_base_datos_contacto'
        ),
    url(r'^base_datos_contacto/(?P<pk_bd_contacto>\d+)/actualizar/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.BaseDatosContactoUpdateView.as_view()),
        name='update_base_datos_contacto'
        ),
    # TODO: Verificar que esta vista se use
    url(r'^base_datos_contacto/(?P<pk>\d+)/validacion/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.DefineBaseDatosContactoView.as_view()),
        name='define_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/agregar/$',
        administrador_o_supervisor_requerido(views_contacto.ContactoBDContactoCreateView.as_view()),
        name='agregar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk>\d+)/validacion_actualizacion/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.ActualizaBaseDatosContactoView.as_view()),
        name='actualiza_base_datos_contacto',
        ),
    # TODO: Verificar que esta vista no va mas y borrarla
    # url(r'^contacto/nuevo/$',
    #    login_required(views_contacto.ContactoCreateView.as_view()),
    #    name='contacto_nuevo',
    #    ),
    url(r'^contacto/list/$',
        agente_requerido(views_contacto.ContactoListView.as_view()),
        name='contacto_list',
        ),
    url(r'^contacto/(?P<pk_contacto>\d+)/update/$',
        agente_requerido(views_contacto.ContactoUpdateView.as_view()),
        name='contacto_update',
        ),
    url(r'^api/campana/(?P<pk_campana>\d+)/contactos/$',
        agente_requerido(views_contacto.API_ObtenerContactosCampanaView.as_view()),
        name='api_contactos_campana',
        ),

    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/list_contacto/$',
        administrador_o_supervisor_requerido(views_contacto.ContactoBDContactoListView.as_view()),
        name='contacto_list_bd_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/update/$',
        administrador_o_supervisor_requerido(views_contacto.ContactoBDContactoUpdateView.as_view()),
        name='actualizar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/eliminar/$',
        administrador_o_supervisor_requerido(views_contacto.ContactoBDContactoDeleteView.as_view()),
        name='eliminar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/ocultar/$',
        administrador_o_supervisor_requerido(views_base_de_datos_contacto.OcultarBaseView.as_view()),
        name='oculta_base_dato', ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/desocultar/$',
        administrador_o_supervisor_requerido(
            views_base_de_datos_contacto.DesOcultarBaseView.as_view()),
        name='desoculta_base_datos', ),
    url(r'^base_datos_contacto/bases_ocultas/$',
        administrador_o_supervisor_requerido(views_base_de_datos_contacto.
                                             mostrar_bases_datos_borradas_ocultas_view),
        name='mostrar_bases_datos_ocultas', ),

    # ==========================================================================
    #  Vistas de manipulación de contactos de una campaña
    # ==========================================================================
    url(r'^campana/selecciona/$',
        login_required(
            views_contacto.FormularioSeleccionCampanaFormView.as_view()),
        name='seleccion_campana_adicion_contacto',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/nuevo_contacto/$',
        login_required(
            views_contacto.FormularioNuevoContactoFormView.as_view()),
        name='nuevo_contacto_campana',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/busqueda_contacto/$',
        login_required(
            views_contacto.CampanaBusquedaContactoFormView.as_view()),
        name="campana_busqueda_contacto"),

    # ==========================================================================
    #  Templates Campana Entrante
    # ==========================================================================
    url(r'^campana_entrante_template/crear/$',
        login_required(
            views_campana_creacion.CampanaEntranteTemplateCreateView.as_view()),
        name="campana_entrante_template_create"),
    url(r'^campana_entrante_template/crear_campana/(?P<pk_campana_template>\d+)$',
        login_required(
            views_campana_creacion.CampanaEntranteTemplateCreateCampanaView.as_view()),
        name="campana_entrante_template_create_campana"),
    url(r'^campana_entrante_template/lista/$',
        login_required(
            views_campana_creacion.CampanaEntranteTemplateListView.as_view()),
        name="campana_entrante_template_list"),
    url(r'^campana_entrante_template/detalle/(?P<pk>\d+)/$',
        login_required(
            views_campana_creacion.CampanaEntranteTemplateDetailView.as_view()),
        name="campana_entrante_template_detail"),
    url(r'^campana_entrante_template/elimina/(?P<pk>\d+)/$',
        login_required(
            views_campana_creacion.CampanaEntranteTemplateDeleteView.as_view()),
        name="campana_entrante_template_delete"),
    # ==========================================================================
    # Vistas varias para Agente: Reportes, logout
    # ==========================================================================
    url(r'^agente/campanas_preview/activas/$',
        agente_requerido(
            views_agente.AgenteCampanasPreviewActivasView.as_view()),
        name="campana_preview_activas_miembro"),
    url(r'^agente/(?P<pk_agente>\d+)/reporte/$',
        agente_requerido(
            views_agente.AgenteReporteCalificaciones.as_view()),
        name='reporte_agente_calificaciones',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/exporta/calificaciones/$',
        agente_requerido(
            views_agente.ExportaReporteCalificacionView.as_view()),
        name='exporta_reporte_calificaciones',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/exporta/formularios/$',
        agente_requerido(
            views_agente.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_reporte_formularios',
        ),
    url(r'^agente/logout/$',
        login_required(views_agente.logout_view), name='agente_logout',
        ),
    url(r'^agente/llamar/$',
        agente_requerido(
            views_agente.LlamarContactoView.as_view()),
        name='agente_llamar_contacto',
        ),
    # ==========================================================================
    # Calificacion
    # ==========================================================================
    url(r'^calificacion/list/$',
        administrador_o_supervisor_requerido(views_calificacion.CalificacionListView.as_view()),
        name='calificacion_list',
        ),
    url(r'^calificacion/nuevo/$',
        administrador_o_supervisor_requerido(
            views_calificacion.CalificacionCreateView.as_view()),
        name='calificacion_nuevo',
        ),
    url(r'^calificacion/update/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views_calificacion.CalificacionUpdateView.as_view()),
        name='calificacion_update',
        ),
    url(r'^calificacion/delete/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(views_calificacion.CalificacionDeleteView.as_view()),
        name='calificacion_delete',
        ),

    # ==========================================================================
    # Formulario
    # ==========================================================================
    url(r'^formulario/list/$',
        administrador_o_supervisor_requerido(views_formulario.FormularioListView.as_view()),
        name='formulario_list',
        ),
    url(r'^formulario/nuevo/$',
        administrador_o_supervisor_requerido(views_formulario.FormularioCreateView.as_view()),
        name='formulario_nuevo',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/field/$',
        administrador_o_supervisor_requerido(views_formulario.FieldFormularioCreateView.as_view()),
        name='formulario_field',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/campo/(?P<pk>\d+)/orden/$',
        administrador_o_supervisor_requerido(views_formulario.FieldFormularioOrdenView.as_view()),
        name='campo_formulario_orden',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/campo/(?P<pk>\d+)/delete/$',
        administrador_o_supervisor_requerido(views_formulario.FieldFormularioDeleteView.as_view()),
        name='formulario_field_delete',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/vista_previa/$',
        administrador_o_supervisor_requerido(views_formulario.FormularioPreviewFormView.as_view()),
        name='formulario_vista_previa',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/create/(?P<pk_campana>\d+)/(?P<pk_contacto>\d+)'
        r'/(?P<id_agente>\d+)/$',
        administrador_o_supervisor_requerido(views_formulario.FormularioCreateFormView.as_view()),
        name='formulario_create',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/vista/$',
        administrador_o_supervisor_requerido(views_formulario.FormularioVistaFormView.as_view()),
        name='formulario_vista',
        ),
    # ==========================================================================
    # CalificacionCliente / Formulario
    # ==========================================================================
    url(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
        '/update/(?P<id_agente>\d+)/(?P<wombat_id>\d+)/calificacion/$',
        login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
        kwargs={'from': 'calificacion'},
        name='calificacion_formulario_update_or_create'
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
        '/update/(?P<id_agente>\d+)/(?P<wombat_id>\d+)/recalificacion/$',
        login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
        kwargs={'from': 'recalificacion'},
        name='calificacion_formulario_update_or_create'
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)'
        '/update/(?P<id_agente>\d+)/(?P<wombat_id>\d+)/reporte/$',
        login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
        kwargs={'from': 'reporte'},
        name='calificacion_cliente_actualiza_desde_reporte'
        ),
    url(r'^campana_manual/(?P<pk_campana>\d+)/calificacion/(?P<id_agente>\d+)/create/'
        r'(?P<telefono>\d+)/$',
        login_required(views_calificacion_cliente.CalificacionClienteFormView.as_view()),
        kwargs={'from': 'calificacion', 'pk_contacto': None, 'manual': True},
        name="calificar_por_telefono"),

    url(r'^calificacion_cliente/externa/$',
        views_calificacion_cliente.calificacion_cliente_externa_view,
        name='calificacion_cliente_externa'
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/venta/(?P<pk_contacto>\d+)/(?P<id_agente>\d+)/$',
        login_required(views_calificacion_cliente.FormularioCreateFormView.as_view()),
        name='formulario_venta'
        ),
    url(r'^formulario/(?P<pk>\d+)/detalle/$',
        login_required(
            views_calificacion_cliente.FormularioDetailView.as_view()),
        name='formulario_detalle'
        ),
    url(r'^formulario/(?P<pk_metadata>\d+)/metadata/$',
        login_required(
            views_calificacion_cliente.FormularioUpdateFormView.as_view()),
        name='formulario_venta_update'
        ),
    # ==========================================================================
    # Agente
    # ==========================================================================
    url(r'^agente/cambiar_estado/$',
        views_agente.cambiar_estado_agente_view,
        name='agente_cambiar_estado',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/activar/$',
        login_required(
            views_agente.ActivarAgenteView.as_view()),
        name="agente_activar"),
    url(r'^agente/(?P<pk_agente>\d+)/desactivar/$',
        login_required(
            views_agente.DesactivarAgenteView.as_view()),
        name="agente_desactivar"),
    # ==========================================================================
    # Supervision
    # ==========================================================================
    url(r'^llamadas/activas/$',
        login_required(views_campana_reportes.LlamadasActivasView.as_view()),
        name='llamadas_activas',
        ),
    url(r'^supervision/agentes/campana/(?P<campana_id>\d+)$',
        administrador_o_supervisor_requerido(views_agente.AgentesLogueadosCampana.as_view()),
        name='supervision_agentes_logueados',
        ),
    # ==========================================================================
    # Reportes PDF
    # ==========================================================================
    url(r'^reporte_personas_pdf/$',
        login_required(views_pdf.ReportePersonasPDF.as_view()),
        name="reporte_personas_pdf"),
    url(r'^reporte/(?P<pk_campana>\d+)/campana/$',
        login_required(views_pdf.ReporteCampanaPDF.as_view()),
        name="reporte_campana_pdf"),
    # ==========================================================================
    # Agenda Contacto
    # ==========================================================================
    url(r'^agenda_contacto/(?P<pk_contacto>\d+)/create/(?P<id_agente>\d+)/(?P<pk_campana>\d+)/$',
        login_required(views_agenda_contacto.AgendaContactoCreateView.as_view()),
        name="agenda_contacto_create"),
    url(r'^agenda_contacto/(?P<pk>\d+)/detalle/$',
        login_required(views_agenda_contacto.AgendaContactoDetailView.as_view()),
        name="agenda_contacto_detalle"),
    url(r'^agenda_contacto/eventos/$',
        login_required(views_agenda_contacto.AgendaContactoListFormView.as_view()),
        name="agenda_contacto_listado"),
    # ==========================================================================
    # Campana Dialer
    # ==========================================================================
    url(r'^campana_dialer/list/$',
        permiso_administracion_requerido(views_campana_dialer.CampanaDialerListView.as_view()),
        name="campana_dialer_list"),
    url(r'^campana_dialer/create/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer_creacion.CampanaDialerCreateView.as_view()),
        name="campana_dialer_create"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/update/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer_creacion.CampanaDialerUpdateView.as_view()),
        name="campana_dialer_update"),
    url(r'^campana_dialer/start/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.PlayCampanaDialerView.as_view()),
        name='start_campana_dialer'),
    url(r'^campana_dialer/pausar/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.PausarCampanaDialerView.as_view()),
        name='pausar_campana_dialer'),
    url(r'^campana_dialer/activar/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.ActivarCampanaDialerView.as_view()),
        name='activar_campana_dialer'),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/delete/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.CampanaDialerDeleteView.as_view()),
        name="campana_dialer_delete"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/ocultar/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.OcultarCampanaDialerView.as_view()),
        name="campana_dialer_ocultar"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/desocultar/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.DesOcultarCampanaDialerView.as_view()),
        name="campana_dialer_desocultar"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/update_base/$',
        administrador_o_supervisor_requerido(
            views_campana_dialer.UpdateBaseDatosDialerView.as_view()),
        name="campana_dialer_update_base"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/supervisors/$',
        administrador_requerido(
            views_campana_dialer.CampanaDialerSupervisorUpdateView.as_view()),
        name="campana_dialer_supervisors"),
    url(r'^campana_dialer/mostrar_ocultas/$',
        permiso_administracion_requerido(
            views_campana_dialer.CampanaDialerBorradasListView.as_view()),
        name="campana_dialer_mostrar_ocultas"),
    url(r'^campana_dialer/finaliza_actovas/$',
        permiso_administracion_requerido(
            views_campana_dialer.FinalizarCampanasActivasView.as_view()),
        name="campana_dialer_finaliza_activas"),
    # ==========================================================================
    # Campana Manual
    # ==========================================================================
    url(r'^campana_manual/lista/$',
        permiso_administracion_requerido(
            views_campana_manual.CampanaManualListView.as_view()),
        name="campana_manual_list"),
    url(r'^campana_manual/create/$',
        administrador_o_supervisor_requerido(
            views_campana_manual_creacion.CampanaManualCreateView.as_view()),
        name="campana_manual_create"),
    url(r'^campana_manual/(?P<pk_campana>\d+)/update/$',
        administrador_o_supervisor_requerido(
            views_campana_manual_creacion.CampanaManualUpdateView.as_view()),
        name="campana_manual_update"),
    url(r'^campana_manual/(?P<pk_campana>\d+)/delete/$',
        administrador_o_supervisor_requerido(
            views_campana_manual.CampanaManualDeleteView.as_view()),
        name="campana_manual_delete"),
    url(r'^campana_manual/(?P<pk_campana>\d+)/ocultar/$',
        administrador_o_supervisor_requerido(
            views_campana_manual.OcultarCampanaManualView.as_view()),
        name="campana_manual_ocultar"),
    url(r'^campana_manual/(?P<pk_campana>\d+)/desocultar/$',
        administrador_o_supervisor_requerido(
            views_campana_manual.DesOcultarCampanaManualView.as_view()),
        name="campana_manual_desocultar"),
    url(r'^campana_manual/(?P<pk_campana>\d+)/supervisors/$',
        administrador_requerido(
            views_campana_manual.CampanaManualSupervisorUpdateView.as_view()),
        name="campana_manual_supervisors"),
    url(r'^campana_manual/mostrar_ocultas/$',
        permiso_administracion_requerido(
            views_campana_manual.CampanaManualBorradasListView.as_view()),
        name="campana_manual_mostrar_ocultas"),
    # ==========================================================================
    # Campana Preview
    # ==========================================================================
    url(r'^campana_preview/lista/$',
        permiso_administracion_requerido(
            views_campana_preview.CampanaPreviewListView.as_view()),
        name="campana_preview_list"),
    url(r'^campana_preview/create/$',
        administrador_o_supervisor_requerido(
            views_campana_preview.CampanaPreviewCreateView.as_view()),
        name="campana_preview_create"),
    url(r'^campana_preview/(?P<pk_campana>\d+)/update/$',
        administrador_o_supervisor_requerido(
            views_campana_preview.CampanaPreviewUpdateView.as_view()),
        name="campana_preview_update"),
    url(r'^campana_preview/(?P<pk_campana>\d+)/delete/$',
        administrador_o_supervisor_requerido(
            views_campana_preview.CampanaPreviewDeleteView.as_view()),
        name="campana_preview_delete"),
    url(r'^campana_preview/(?P<pk_campana>\d+)/supervisors/$',
        administrador_requerido(
            views_campana_preview.CampanaPreviewSupervisorUpdateView.as_view()),
        name="campana_preview_supervisors"),
    url(r'^campana_preview/mostrar_ocultas/$',
        permiso_administracion_requerido(
            views_campana_preview.CampanaPreviewBorradasListView.as_view()),
        name="campana_preview_mostrar_ocultas"),
    url(r'^campana/mostrar_ocultar/(?P<pk_campana>\d+)/$',
        administrador_o_supervisor_requerido(
            views_campana_preview.campana_mostrar_ocultar_view),
        name="campana_mostrar_ocultar"),
    url(r'^campana_preview/(?P<pk_campana>\d+)/contacto/obtener/$',
        login_required(
            views_campana_preview.ObtenerContactoView.as_view()),
        name="campana_preview_dispatcher"),
    url(r'^campana_preview/validar_contacto_asignado/$',
        login_required(
            views_campana_preview.campana_validar_contacto_asignado_view),
        name="validar_contacto_asignado"),
    # ==========================================================================
    # Campana Entrante
    # ==========================================================================
    url(r'campana/list/$',
        permiso_administracion_requerido(views_campana.CampanaListView.as_view()),
        name='campana_list',
        ),
    url(r'^campana/nuevo/$',
        administrador_o_supervisor_requerido(
            views_campana_creacion.CampanaEntranteCreateView.as_view()),
        name='campana_nuevo',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/update/$',
        administrador_o_supervisor_requerido(
            views_campana_creacion.CampanaEntranteUpdateView.as_view()),
        name='campana_update',
        ),
    url(r'^campana/elimina/(?P<pk_campana>\d+)/$',
        administrador_o_supervisor_requerido(views_campana.CampanaDeleteView.as_view()),
        name='campana_elimina',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/ocultar/$',
        administrador_o_supervisor_requerido(views_campana.OcultarCampanaView.as_view()),
        name='oculta_campana', ),
    url(r'^campana/(?P<pk_campana>\d+)/desocultar/$',
        administrador_o_supervisor_requerido(views_campana.DesOcultarCampanaView.as_view()),
        name='desoculta_campana', ),
    url(r'^campana/llamadas_cola/$',
        login_required(
            views_campana.CampanaReporteQueueListView.as_view()),
        name='reporte_llamadas_queue',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/mostrar_json/$',
        login_required(views_campana.campana_json_view),
        ),
    url(r'^campana/(?P<pk_campana>\d+)/supervisors/$',
        administrador_requerido(
            views_campana.CampanaSupervisorUpdateView.as_view()),
        name="campana_supervisors"),
    url(r'^campana/mostrar_ocultas/$',
        permiso_administracion_requerido(
            views_campana.CampanaBorradasListView.as_view()),
        name="mostrar_campanas_ocultas"),
    # ==========================================================================
    # Blacklist
    # ==========================================================================
    url(r'^backlist/nueva/$',
        administrador_requerido(views_back_list.BacklistCreateView.as_view()),
        name="back_list_create"),
    url(r'^backlist/lista/$',
        administrador_requerido(views_back_list.BackListView.as_view()),
        name="back_list_list"),
    # ==========================================================================
    # Sitio Externo
    # ==========================================================================
    url(r'^sitio_externo/list/$',
        administrador_requerido(views_sitio_externo.SitioExternoListView.as_view()),
        name="sitio_externo_list"),
    url(r'^sitio_externo/nuevo/$',
        administrador_requerido(views_sitio_externo.SitioExternoCreateView.as_view()),
        name="sitio_externo_create"),
    url(r'^sitio_externo/(?P<pk_sitio_externo>\d+)/ocultar/$',
        administrador_requerido(views_sitio_externo.OcultarSitioExternoView.as_view()),
        name='oculta_sitio_externo', ),
    url(r'^sitio_externo/(?P<pk_sitio_externo>\d+)/desocultar/$',
        administrador_requerido(
            views_sitio_externo.DesOcultarSitioExternoView.as_view()),
        name='desoculta_sitio_externo', ),
    url(r'^sitio_externo/sitios_ocultos/$',
        administrador_requerido(views_sitio_externo.mostrar_sitio_externos_ocultos_view),
        name='mostrar_sitios_externo_ocultos', ),
    # ==========================================================================
    # QueueMember
    # ==========================================================================
    url(r'^campana/(?P<pk_campana>\d+)/queue_member/$',
        administrador_o_supervisor_requerido(views_queue_member.QueueMemberCreateView.as_view()),
        name='queue_member_add',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/grupo_agente/$',
        administrador_o_supervisor_requerido(views_queue_member.GrupoAgenteCreateView.as_view()),
        name='queue_member_grupo_agente',
        ),
    url(r'^queue_member/(?P<pk_campana>\d+)/queue_member_campana/$',
        administrador_o_supervisor_requerido(views_queue_member.QueueMemberCampanaView.as_view()),
        name='queue_member_campana',
        ),
    url(
        r'^queue_member/(?P<pk_queuemember>\d+)/elimina/(?P<pk_campana>\d+)/$',
        administrador_o_supervisor_requerido(views_queue_member.queue_member_delete_view),
        name='queue_member_elimina',
    ),
    # ==========================================================================
    # UserApiCrm
    # ==========================================================================
    url(r'^user_api_crm/create/$',
        administrador_requerido(views_user_api_crm.UserApiCrmCreateView.as_view()),
        name='user_api_crm_create',
        ),
    url(r'^user_api_crm/(?P<pk>\d+)/update/$',
        administrador_requerido(views_user_api_crm.UserApiCrmUpdateView.as_view()),
        name='user_api_crm_update',
        ),
    url(r'^user_api_crm/(?P<pk>\d+)/delete/$',
        login_required(views_user_api_crm.UserApiCrmDeleteView.as_view()),
        name='user_api_crm_delete',
        ),
    url(r'^user_api_crm/list/$',
        administrador_requerido(views_user_api_crm.UserApiCrmListView.as_view()),
        name='user_api_crm_list',
        ),

    # ==========================================================================
    # Campana Dialer Template
    # ==========================================================================
    url(r'^campana_dialer_template/create/$',
        login_required(
            views_campana_dialer_template.CampanaDialerTemplateCreateView.as_view()),
        name="campana_dialer_template_create"),
    url(r'^campana_dialer_template/lista/$',
        login_required(
            views_campana_dialer_template.TemplateListView.as_view()),
        name="lista_campana_dialer_template"),
    url(r'^campana_dialer_template/(?P<pk_campana_template>\d+)/crea_campana/'
        r'(?P<borrar_template>\d+)/$',
        login_required(
            views_campana_dialer_template.CampanaDialerTemplateCreateCampanaView.as_view()),
        name="crea_campana_dialer_template"),
    url(r'^campana_dialer_template/(?P<pk>\d+)/detalle/$',
        login_required(
            views_campana_dialer_template.TemplateDetailView.as_view()),
        name="campana_dialer_template_detalle"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/elimina/$',
        login_required(
            views_campana_dialer_template.TemplateDeleteView.as_view()),
        name="campana_dialer_template_elimina"),
    # ==========================================================================
    #  Templates Campana Manual
    # ==========================================================================
    url(r'^campana_manual_template/crear/$',
        login_required(
            views_campana_manual_creacion.CampanaManualTemplateCreateView.as_view()),
        name="campana_manual_template_create"),
    url(r'^campana_manual_template/crear_campana/(?P<pk_campana_template>\d+)$',
        login_required(
            views_campana_manual_creacion.CampanaManualTemplateCreateCampanaView.as_view()),
        name="campana_manual_template_create_campana"),
    url(r'^campana_manual_template/lista/$',
        login_required(
            views_campana_manual_creacion.CampanaManualTemplateListView.as_view()),
        name="campana_manual_template_list"),
    url(r'^campana_manual_template/detalle/(?P<pk>\d+)/$',
        login_required(
            views_campana_manual_creacion.CampanaManualTemplateDetailView.as_view()),
        name="campana_manual_template_detail"),
    url(r'^campana_manual_template/elimina/(?P<pk>\d+)/$',
        login_required(
            views_campana_manual_creacion.CampanaManualTemplateDeleteView.as_view()),
        name="campana_manual_template_delete"),
    # ==========================================================================
    #  Templates Campana Preview
    # ==========================================================================
    url(r'^campana_preview_template/crear/$',
        login_required(
            views_campana_preview.CampanaPreviewTemplateCreateView.as_view()),
        name="campana_preview_template_create"),
    url(r'^campana_preview_template/crear_campana/(?P<pk_campana_template>\d+)$',
        login_required(
            views_campana_preview.CampanaPreviewTemplateCreateCampanaView.as_view()),
        name="campana_preview_template_create_campana"),
    url(r'^campana_preview_template/lista/$',
        login_required(
            views_campana_preview.CampanaPreviewTemplateListView.as_view()),
        name="campana_preview_template_list"),
    url(r'^campana_preview_template/detalle/(?P<pk>\d+)/$',
        login_required(
            views_campana_preview.CampanaPreviewTemplateDetailView.as_view()),
        name="campana_preview_template_detail"),
    url(r'^campana_preview_template/elimina/(?P<pk>\d+)/$',
        login_required(
            views_campana_preview.CampanaPreviewTemplateDeleteView.as_view()),
        name="campana_preview_template_delete"),

    # ==========================================================================
    # API para Base de Datos de Contactos
    # ==========================================================================
    url(r'^base_de_datos/cargar_nueva/$',
        views_base_de_datos_contacto.cargar_base_datos_view,
        name="cargar_base_datos_api"),
    # ==========================================================================
    # Archivo de Audio
    # ==========================================================================
    url(r'^audios/$',
        administrador_o_supervisor_requerido(
            views_archivo_de_audio.ArchivoAudioListView.as_view()),
        name='lista_archivo_audio',
        ),
    url(r'^audios/create/$',
        administrador_o_supervisor_requerido(
            views_archivo_de_audio.ArchivoAudioCreateView.as_view()),
        name='create_archivo_audio',
        ),
    url(r'^audios/(?P<pk>\d+)/update/$',
        administrador_o_supervisor_requerido(
            views_archivo_de_audio.ArchivoAudioUpdateView.as_view()),
        name='edita_archivo_audio',
        ),
    url(r'^audios/(?P<pk>\d+)/eliminar/$',
        administrador_o_supervisor_requerido(
            views_archivo_de_audio.ArchivoAudioDeleteView.as_view()),
        name='eliminar_archivo_audio',
        ),
    url(r'^user/(?P<username>\w{0,50})/$', views.profile_page,),

]

urlpatterns += [url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), ]

if settings.DJANGO_DEBUG_TOOLBAR:
    #     # static files (images, css, javascript, etc.)
    #     urlpatterns += patterns('',
    #         (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
    #             'document_root': settings.MEDIA_ROOT}))

    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
