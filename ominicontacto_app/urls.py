# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, patterns
from ominicontacto_app import (
    views, views_base_de_datos_contacto, views_contacto, views_campana_creacion,
    views_grabacion, views_calificacion, views_formulario, views_agente,
    views_calificacion_formulario, views_campana, views_campana_reportes, views_pdf,
    views_agenda_contacto, views_campana_dialer_creacion, views_campana_dialer,
    views_campana_dialer_reportes, views_back_list, views_sitio_externo,
    views_queue_member, views_user_api_crm, views_supervisor,
    views_campana_dialer_template
)
from django.contrib.auth.decorators import login_required
from ominicontacto_app.views_utils import (
    handler400, handler403, handler404, handler500
)


handler400 = handler400
handler403 = handler403
handler404 = handler404
handler500 = handler500


urlpatterns = [
    url(r'^ajax/mensaje_recibidos/',
        views.mensajes_recibidos_view,
        name='ajax_mensaje_recibidos'),
    url(r'^$', views.index_view, name='index'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^user/nuevo/$',
        login_required(views.CustomerUserCreateView.as_view()),
        name='user_nuevo',
        ),
    url(r'^user/delete/(?P<pk>\d+)/$',
        login_required(views.UserDeleteView.as_view()),
        name='user_delete',
        ),
    url(r'^user/list/page(?P<page>[0-9]+)/$',
        login_required(views.UserListView.as_view()), name='user_list',
        ),
    url(r'^user/update/(?P<pk>\d+)/$',
        login_required(views.CustomerUserUpdateView.as_view()),
        name='user_update',
        ),
    url(r'^user/agenteprofile/nuevo/(?P<pk_user>\d+)/$',
        login_required(views.AgenteProfileCreateView.as_view()),
        name='agenteprofile_nuevo',
        ),
    url(r'^modulo/nuevo/$',
        login_required(views.ModuloCreateView.as_view()), name='modulo_nuevo',
        ),
    url(r'^modulo/update/(?P<pk>\d+)/$',
        login_required(views.ModuloUpdateView.as_view()),
        name='modulo_update',
        ),
    url(r'^modulo/list/$',
        login_required(views.ModuloListView.as_view()), name='modulo_list',
        ),
    url(r'^modulo/delete/(?P<pk>\d+)/$',
        login_required(views.ModuloDeleteView.as_view()),
        name='modulo_delete',
        ),
    url(r'^agente/list/$',
        login_required(views.AgenteListView.as_view()), name='agente_list',
        ),
    url(r'^user/agenteprofile/update/(?P<pk_agenteprofile>\d+)/$',
        login_required(views.AgenteProfileUpdateView.as_view()),
        name='agenteprofile_update',
        ),
    url(r'^grupo/nuevo/$',
        login_required(views.GrupoCreateView.as_view()), name='grupo_nuevo',
        ),
    url(r'^grupo/update/(?P<pk>\d+)/$',
        login_required(views.GrupoUpdateView.as_view()),
        name='grupo_update',
        ),
    url(r'^grupo/list/$',
        login_required(views.GrupoListView.as_view()), name='grupo_list',
        ),
    url(r'^grupo/delete/(?P<pk>\d+)/$',
        login_required(views.GrupoDeleteView.as_view()),
        name='grupo_delete',
        ),
    url(r'^pausa/nuevo/$',
        login_required(views.PausaCreateView.as_view()),
        name='pausa_nuevo',
        ),
    url(r'^pausa/update/(?P<pk>\d+)/$',
        login_required(views.PausaUpdateView.as_view()),
        name='pausa_update',
        ),
    url(r'^pausa/list/$',
        login_required(views.PausaListView.as_view()),
        name='pausa_list',
        ),
    url(r'^pausa/delete/(?P<pk>\d+)/$',
        login_required(views.PausaDeleteView.as_view()),
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
    url(r'^grabacion/buscar/(?P<pagina>\d+)/$',
        login_required(views_grabacion.BusquedaGrabacionFormView.as_view()),
        name='grabacion_buscar',
        ),
    url(r'^agenda/nuevo/$',
        login_required(views.nuevo_evento_agenda_view),
        name='agenda_nuevo',
        ),
    url(r'^agenda/agente_list/$',
        login_required(views.AgenteEventosFormView.as_view()),
        name='agenda_agente_list',
        ),
    url(r'^regenerar_asterisk/$', views.regenerar_asterisk_view,
        name='regenerar_asterisk'),
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
        login_required(views.supervision_url_externa), name='supervision_externa_url',
        ),
    # ==========================================================================
    # Base Datos Contacto
    # ==========================================================================
    url(r'^base_datos_contacto/(?P<pk_bd_contacto>\d+)/actualizar/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoUpdateView.as_view()),
        name='update_base_datos_contacto'
        ),
    url(r'^base_datos_contacto/nueva/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoCreateView.as_view()),
        name='nueva_base_datos_contacto'
        ),
    url(r'^base_datos_contacto/(?P<pk>\d+)/validacion/$',
        login_required(views_base_de_datos_contacto.
                       DefineBaseDatosContactoView.as_view()),
        name='define_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoListView.as_view()),
        name='lista_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/agregar/$',
        login_required(views_contacto.ContactoBDContactoCreateView.as_view()),
        name='agregar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk>\d+)/validacion_actualizacion/$',
        login_required(views_base_de_datos_contacto.
                       ActualizaBaseDatosContactoView.as_view()),
        name='actualiza_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/exporta_dialer/$',
        login_required(views_base_de_datos_contacto.
                       ExportaDialerView.as_view()),
        name='exporta_dialer',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/genera_dialer/$',
        login_required(views_base_de_datos_contacto.
                       GeneraExportacionDialerView.as_view()),
        name='exporta_csv_dialer',
        ),
    url(r'^contacto/nuevo/$',
        login_required(views_contacto.ContactoCreateView.as_view()),
        name='contacto_nuevo',
        ),
    url(r'^contacto/list/(?P<pagina>\d+)/$',
        login_required(views_contacto.ContactoListView.as_view()),
        name='contacto_list',
        ),
    url(r'^contacto/(?P<pk_contacto>\d+)/update/$',
        login_required(views_contacto.ContactoUpdateView.as_view()),
        name='contacto_update',
        ),
    url(r'^contacto/buscar/$',
        login_required(views_contacto.BusquedaContactoFormView.as_view()),
        name='contacto_buscar',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/list_contacto/$',
        login_required(views_contacto.ContactoBDContactoListView.as_view()),
        name='contacto_list_bd_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/update/$',
        login_required(views_contacto.ContactoBDContactoUpdateView.as_view()),
        name='actualizar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/eliminar/$',
        login_required(views_contacto.ContactoBDContactoDeleteView.as_view()),
        name='eliminar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/ocultar/$',
        login_required(views_base_de_datos_contacto.OcultarBaseView.as_view()),
        name='oculta_base_dato', ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/desocultar/$',
        login_required(
            views_base_de_datos_contacto.DesOcultarBaseView.as_view()),
        name='desoculta_base_datos', ),
    url(r'^base_datos_contacto/bases_ocultas/$',
        login_required(views_base_de_datos_contacto.
                       mostrar_bases_datos_borradas_ocultas_view),
        name='mostrar_bases_datos_ocultas', ),
    # ==========================================================================
    # Campana
    # ==========================================================================
    url(r'^campana/nuevo/$',
        login_required(views_campana_creacion.CampanaCreateView.as_view()),
        name='campana_nuevo',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/update/$',
        login_required(views_campana_creacion.CampanaUpdateView.as_view()),
        name='campana_update',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/cola/$',
        login_required(views_campana_creacion.QueueCreateView.as_view()),
        name='queue_nuevo',
        ),
    url(r'^campana/update/(?P<pk_campana>\d+)/cola/$',
        login_required(views_campana_creacion.QueueUpdateView.as_view()),
        name='queue_update',
        ),
    url(r'campana/list/$',
        login_required(views_campana.CampanaListView.as_view()),
        name='campana_list',
        ),
    url(r'^campana/elimina/(?P<pk_campana>\d+)/$',
        login_required(views_campana.CampanaDeleteView.as_view()),
        name='campana_elimina',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/buscar/$',
        login_required(
            views_campana.BusquedaFormularioFormView.as_view()),
        name='formulario_buscar',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_campana.ExportaReporteCampanaView.as_view()),
        name='exporta_campana_reporte',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte/$',
        login_required(
            views_campana.CampanaReporteListView.as_view()),
        name='reporte_campana',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/$',
        login_required(
            views_campana.CampanaReporteGrafico.as_view()),
        name='reporte_campana_grafico',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/(?P<pk_agente>\d+)/agente/$',
        login_required(
            views_campana.AgenteCampanaReporteGrafico.as_view()),
        name='reporte_agente_grafico',
        ),
    url(r'^campana/selecciona/$',
        login_required(
            views_campana.FormularioSeleccionCampanaFormView.as_view()),
        name='seleccion_campana',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/nuevo_contacto/$',
        login_required(
            views_campana.FormularioNuevoContactoFormView.as_view()),
        name='nuevo_contacto_campana',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/ocultar/$',
        login_required(views_campana.OcultarCampanaView.as_view()),
        name='oculta_campana', ),
    url(r'^campana/(?P<pk_campana>\d+)/desocultar/$',
        login_required(views_campana.DesOcultarCampanaView.as_view()),
        name='desoculta_campana', ),
    url(r'^mostrar/campanas_ocultas/$',
        login_required(views_campana.mostrar_campanas_borradas_ocultas_view),
        name='mostrar_campanas_ocultas', ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta_pdf/$',
        login_required(
            views_campana.ExportaReportePDFView.as_view()),
        name='exporta_campana_reporte_pdf',
        ),
    url(r'^campana/llamadas_cola/$',
        login_required(
            views_campana.CampanaReporteQueueListView.as_view()),
        name='reporte_llamadas_queue',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/mostrar_json/$',
        login_required(views_campana.campana_json_view),
        ),
    url(r'^campana/(?P<pk_campana>\d+)/supervisors/$',
        login_required(
            views_campana.CampanaSupervisorUpdateView.as_view()),
        name="campana_supervisors"),
    # ==========================================================================
    # Formulario Weelo
    # ==========================================================================
    url(r'^formulario/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_campana.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_formulario_reporte',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/reporte/$',
        login_required(
            views_agente.AgenteReporteCalificaciones.as_view()),
        name='reporte_agente_calificaciones',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/exporta/calificaciones/$',
        login_required(
            views_agente.ExportaReporteCalificacionView.as_view()),
        name='exporta_reporte_calificaciones',
        ),
    url(r'^agente/(?P<pk_agente>\d+)/exporta/formularios/$',
        login_required(
            views_agente.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_reporte_formularios',
        ),
    url(r'^agente/tiempos/$',
        login_required(
            views_agente.AgenteReporteListView.as_view()),
        name='agente_tiempos',
        ),
    url(r'^agente/logout/$',
        login_required(views_agente.logout_view), name='agente_logout',
        ),
    url(r'^agente/llamar/$',
        login_required(
            views_agente.LlamarContactoView.as_view()),
        name='agente_llamar_contacto',
        ),
    # ==========================================================================
    # Reportes
    # ==========================================================================
    url(r'^reporte/llamadas/hoy/$',
        login_required(views_grabacion.GrabacionReporteListView.as_view()),
        name='reporte_llamadas_hoy',
        ),
    url(r'^reporte/llamadas/semana/$',
        login_required(views_grabacion.GrabacionReporteSemanaListView.as_view()),
        name='reporte_llamadas_semana',
        ),
    url(r'^reporte/llamadas/mes/$',
        login_required(
            views_grabacion.GrabacionReporteMesListView.as_view()),
        name='reporte_llamadas_mes',
        ),
    url(r'^reporte/llamadas/$',
        login_required(
            views_grabacion.GrabacionReporteFormView.as_view()),
        name='reporte_llamadas',
        ),
    # ==========================================================================
    # Calificacion
    # ==========================================================================
    url(r'^calificacion/nuevo/$',
        login_required(
            views_calificacion.CalificacionCreateView.as_view()),
        name='calificacion_nuevo',
        ),
    url(r'^calificacion/update/(?P<pk>\d+)/$',
        login_required(views_calificacion.CalificacionUpdateView.as_view()),
        name='calificacion_update',
        ),
    url(r'^calificacion/list/$',
        login_required(views_calificacion.CalificacionListView.as_view()),
        name='calificacion_list',
        ),
    url(r'^calificacion/delete/(?P<pk>\d+)/$',
        login_required(views_calificacion.CalificacionDeleteView.as_view()),
        name='calificacion_delete',
        ),
    url(r'^calificacion_campana/nuevo/$',
        login_required(
            views_calificacion.CalificacionCampanaCreateView.as_view()),
        name='calificacion_campana_nuevo',
        ),
    url(r'^calificacion_campana/update/(?P<pk>\d+)/$',
        login_required(
            views_calificacion.CalificacionCampanaUpdateView.as_view()),
        name='calificacion_campana_update',
        ),
    url(r'^calificacion_campana/lista/$',
        login_required(
            views_calificacion.CalificacionCampanaListView.as_view()),
        name='calificacion_campana_list',
        ),
    url(r'^calificacion_campana/delete/(?P<pk>\d+)/$',
        login_required(
            views_calificacion.CalificacionCampanaDeleteView.as_view()),
        name='calificacion_campana_delete',
        ),
    # ==========================================================================
    # Formulario
    # ==========================================================================
    url(r'^formulario/nuevo/$',
        login_required(views_formulario.FormularioCreateView.as_view()),
        name='formulario_nuevo',
        ),
    url(r'^formulario/list/$',
        login_required(views_formulario.FormularioListView.as_view()),
        name='formulario_list',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/field/$',
        login_required(views_formulario.FieldFormularioCreateView.as_view()),
        name='formulario_field',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/campo/(?P<pk>\d+)/orden/$',
        login_required(views_formulario.FieldFormularioOrdenView.as_view()),
        name='campo_formulario_orden',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/campo/(?P<pk>\d+)/delete/$',
        login_required(views_formulario.FieldFormularioDeleteView.as_view()),
        name='formulario_field_delete',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/vista_previa/$',
        login_required(views_formulario.FormularioPreviewFormView.as_view()),
        name='formulario_vista_previa',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/create/(?P<pk_campana>\d+)/(?P<pk_contacto>\d+)/(?P<id_agente>\d+)/$',
        login_required(views_formulario.FormularioCreateFormView.as_view()),
        name='formulario_create',
        ),
    url(r'^formulario/(?P<pk_formulario>\d+)/vista/$',
        login_required(views_formulario.FormularioVistaFormView.as_view()),
        name='formulario_vista',
        ),
    # ==========================================================================
    # Calificacion Formulario
    # ==========================================================================
    url(
        r'^formulario/(?P<pk_campana>\d+)/venta/(?P<pk_contacto>\d+)/(?P<id_agente>\d+)/$',
        login_required(views_calificacion_formulario.FormularioCreateFormView.as_view()),
        name='formulario_venta',
        ),
    url(
        r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)/create/(?P<id_agente>\d+)/(?P<wombat_id>\d+)/$',
        login_required(views_calificacion_formulario.CalificacionClienteCreateView.as_view()),
        name='calificacion_formulario_create',
        ),
    url(
        r'^formulario/(?P<pk_campana>\d+)/calificacion/(?P<pk_contacto>\d+)/update/(?P<id_agente>\d+)/(?P<wombat_id>\d+)/$',
        login_required(views_calificacion_formulario.CalificacionClienteUpdateView.as_view()),
        name='calificacion_formulario_update',
        ),
    url(r'^formulario/(?P<pk>\d+)/detalle/$',
        login_required(
            views_calificacion_formulario.FormularioDetailView.as_view()),
        name='formulario_detalle',
        ),
    url(
        r'^formulario/(?P<pk_metadata>\d+)/metadata/$',
        login_required(
            views_calificacion_formulario.FormularioUpdateFormView.as_view()),
        name='formulario_venta_update',
    ),
    url(
        r'^formulario/(?P<pk_calificacion>\d+)/calificacion/actualiza/$',
        login_required(
            views_calificacion_formulario.CalificacionUpdateView.as_view()),
        name='formulario_califiacion_actualiza',
    ),
    url(r'^califacacion_cliente/externa/$',
        views_calificacion_formulario.calificacion_cliente_externa_view,
        name='califiacion_cliente_externa'
        ),
    # ==========================================================================
    # Agente
    # ==========================================================================
    url(r'^agente/cambiar_estado/$',
        views_agente.cambiar_estado_agente_view,
        name='agente_cambiar_estado',
        ),
    # ==========================================================================
    # Supervision
    # ==========================================================================
    url(r'^llamadas/activas/$',
        login_required(views_campana_reportes.LlamadasActivasView.as_view()),
        name='llamadas_activas',
        ),
    url(r'^wombat/logs/$', views.wombat_log_view,
        name='wombat_log',
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
        login_required(views_agenda_contacto.AgenteContactoListFormView.as_view()),
        name="agenda_contacto_listado"),
    # ==========================================================================
    # Campana Dialer
    # ==========================================================================
    url(r'^campana_dialer/create/$',
        login_required(views_campana_dialer_creacion.CampanaDialerCreateView.as_view()),
        name="campana_dialer_create"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/sincronizar_lista/$',
        login_required(
            views_campana_dialer_creacion.SincronizaDialerView.as_view()),
        name="campana_dialer_sincronizar"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/update/$',
        login_required(
            views_campana_dialer_creacion.CampanaDialerUpdateView.as_view()),
        name="campana_dialer_update"),
    url(r'^campana_dialer/list/$',
        login_required(views_campana_dialer.CampanaDialerListView.as_view()),
        name="campana_dialer_list"),
    url(r'^campana_dialer/start/$',
        login_required(
            views_campana_dialer.PlayCampanaDialerView.as_view()),
        name='start_campana_dialer',
        ),
    url(r'^campana_dialer/pausar/$',
        login_required(
            views_campana_dialer.PausarCampanaDialerView.as_view()),
        name='pausar_campana_dialer',
        ),
    url(r'^campana_dialer/activar/$',
        login_required(
            views_campana_dialer.ActivarCampanaDialerView.as_view()),
        name='activar_campana_dialer',
        ),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/delete/$',
        login_required(
            views_campana_dialer.CampanaDialerDeleteView.as_view()),
        name="campana_dialer_delete"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/ocultar/$',
        login_required(
            views_campana_dialer.OcultarCampanaDialerView.as_view()),
        name="campana_dialer_ocultar"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/desocultar/$',
        login_required(
            views_campana_dialer.DesOcultarCampanaDialerView.as_view()),
        name="campana_dialer_desocultar"),
    url(r'^campana_dialer/mostrar_ocultas/$',
        login_required(
            views_campana_dialer.mostrar_campanas_dialer_borradas_ocultas_view),
        name="campana_dialer_mostrar_ocultas"),
    url(r'^campana_dialer/detalle_wombat/$',
        login_required(
            views_campana_dialer.detalle_campana_dialer_view),
        name="campana_dialer_detalle_wombat"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/update_base/$',
        login_required(
            views_campana_dialer.UpdateBaseDatosDialerView.as_view()),
        name="campana_dialer_update_base"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/busqueda_contacto/$',
        login_required(
            views_campana_dialer.CampanaDialerBusquedaContactoFormView.as_view()),
        name="campana_dialer_busqueda_contacto"),
    url(r'^campana_dialer/seleciona_campana/$',
        login_required(
            views_campana_dialer.FormularioSeleccionCampanaDialerFormView.as_view()),
        name="campana_dialer_selecciona_campana"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/nuevo_contacto/$',
        login_required(
            views_campana_dialer.FormularioNuevoContactoFormView.as_view()),
        name="nuevo_contacto_campana_dialer"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/actuacion_vigente/$',
        login_required(
            views_campana_dialer_creacion.ActuacionVigenteCampanaDialerCreateView.as_view()),
        name="nuevo_actuacion_vigente_campana_dialer"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reglas_incidencia/$',
        login_required(
            views_campana_dialer_creacion.ReglasIncidenciaCampanaDialerCreateView.as_view()),
        name="nueva_reglas_incidencia_campana_dialer"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reglas_incidencia/(?P<pk_regla>\d+)/delete/$',
        login_required(
            views_campana_dialer_creacion.regla_incidencia_delete_view),
        name="delete_regla_incidencia_campana_dialer"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/cola/$',
        login_required(
            views_campana_dialer_creacion.QueueDialerCreateView.as_view()),
        name="campana_dialer_queue_create"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/cola_update/$',
        login_required(
            views_campana_dialer_creacion.QueueDialerUpdateView.as_view()),
        name="campana_dialer_queue_update"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/supervisors/$',
        login_required(
            views_campana_dialer.CampanaDialerSupervisorUpdateView.as_view()),
        name="campana_dialer_supervisors"),
    # ==========================================================================
    # Campana Dialer Reportes
    # ==========================================================================
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reporte_calificacion/$',
        login_required(
            views_campana_dialer_reportes.CampanaDialerReporteCalificacionListView.as_view()),
        name="campana_dialer_reporte_calificacion"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reporte_grafico/$',
        login_required(
            views_campana_dialer_reportes.CampanaDialerReporteGrafico.as_view()),
        name="campana_dialer_reporte_grafico"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reporte_pdf/$',
        login_required(
            views_campana_dialer_reportes.ExportaCampanaDialerReportePDFView.as_view()),
        name="campana_dialer_reporte_pdf"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/reporte_agente/(?P<pk_agente>\d+)/$',
        login_required(
            views_campana_dialer_reportes.AgenteCampanaDialerReporteGrafico.as_view()),
        name="campana_dialer_reporte_agente"),
    # ==========================================================================
    # Backlist
    # ==========================================================================
    url(r'^backlist/nueva/$',
        login_required(views_back_list.BacklistCreateView.as_view()),
        name="back_list_create"),
    url(r'^backlist/lista/$',
        login_required(views_back_list.BackListView.as_view()),
        name="back_list_list"),
    # ==========================================================================
    # Sitio Externo
    # ==========================================================================
    url(r'^sitio_externo/nuevo/$',
        login_required(views_sitio_externo.SitioExternoCreateView.as_view()),
        name="sitio_externo_create"),
    url(r'^sitio_externo/list/$',
        login_required(views_sitio_externo.SitioExternoListView.as_view()),
        name="sitio_externo_list"),
    url(r'^sitio_externo/(?P<pk_sitio_externo>\d+)/ocultar/$',
        login_required(views_sitio_externo.OcultarSitioExternoView.as_view()),
        name='oculta_sitio_externo', ),
    url(r'^sitio_externo/(?P<pk_sitio_externo>\d+)/desocultar/$',
        login_required(
            views_sitio_externo.DesOcultarSitioExternoView.as_view()),
        name='desoculta_sitio_externo', ),
    url(r'^sitio_externo/sitios_ocultos/$',
        login_required(views_sitio_externo.mostrar_sitio_externos_ocultos_view),
        name='mostrar_sitios_externo_ocultos', ),
    # ==========================================================================
    # QueueMember
    # ==========================================================================
    url(r'^campana/(?P<pk_campana>\d+)/queue_member/$',
        login_required(views_queue_member.QueueMemberCreateView.as_view()),
        name='queue_member_add',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/grupo_agente/$',
        login_required(views_queue_member.GrupoAgenteCreateView.as_view()),
        name='queue_member_grupo_agente',
        ),
    url(r'^queue_member/(?P<pk_campana>\d+)/queue_member_campana/$',
        login_required(views_queue_member.QueueMemberCampanaView.as_view()),
        name='queue_member_campana',
        ),
    url(
        r'^queue_member/(?P<pk_queuemember>\d+)/elimina/(?P<pk_campana>\d+)/$',
        login_required(views_queue_member.queue_member_delete_view),
        name='queue_member_elimina',
    ),
    # ==========================================================================
    # UserApiCrm
    # ==========================================================================
    url(r'^user_api_crm/create/$',
        login_required(views_user_api_crm.UserApiCrmCreateView.as_view()),
        name='user_api_crm_create',
        ),
    url(r'^user_api_crm/(?P<pk>\d+)/update/$',
        login_required(views_user_api_crm.UserApiCrmUpdateView.as_view()),
        name='user_api_crm_update',
        ),
    url(r'^user_api_crm/list/$',
        login_required(views_user_api_crm.UserApiCrmListView.as_view()),
        name='user_api_crm_list',
        ),
    # ==========================================================================
    # Supervisor
    # ==========================================================================
    url(r'^supervisor/list/$',
        login_required(views_supervisor.SupervisorListView.as_view()),
        name='supervisor_list',
        ),
    url(r'^supervisor/(?P<pk_user>\d+)/create/$',
        login_required(views_supervisor.SupervisorProfileCreateView.as_view()),
        name='supervisor_create',
        ),
    url(r'^supervisor/(?P<pk>\d+)/update/$',
        login_required(views_supervisor.SupervisorProfileUpdateView.as_view()),
        name='supervisor_update',
        ),
    # ==========================================================================
    # Campana Dialer Template
    # ==========================================================================
    url(r'^campana_dialer_template/create/$',
        login_required(
            views_campana_dialer_template.CampanaDialerTemplateCreateView.as_view()),
        name="campana_dialer_template_create"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/cola/$',
        login_required(
            views_campana_dialer_template.QueueDialerTemplateCreateView.as_view()),
        name="campana_dialer_template_queue_create"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/actuacion_vigente/$',
        login_required(
            views_campana_dialer_template.ActuacionVigenteCampanaDialerTemplateCreateView.as_view()),
        name="nuevo_actuacion_vigente_campana_dialer_template"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/reglas_incidencia/$',
        login_required(
            views_campana_dialer_template.ReglasIncidenciaCampanaDialerTemplateCreateView.as_view()),
        name="nueva_reglas_incidencia_campana_dialer_template"),
    url(
        r'^campana_dialer_template/(?P<pk_campana>\d+)/reglas_incidencia/(?P<pk_regla>\d+)/delete/$',
        login_required(
            views_campana_dialer_template.regla_incidencia_delete_view),
        name="delete_regla_incidencia_campana_dialer_template"),
    url(r'^campana_dialer_template/lista/$',
        login_required(
            views_campana_dialer_template.TemplateListView.as_view()),
        name="lista_campana_dialer_template"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/confirma/$',
        login_required(
            views_campana_dialer_template.ConfirmaCampanaDialerTemplateView.as_view()),
        name="confirma_campana_dialer_template"),
    url(r'^campana_dialer_template/(?P<pk_campana>\d+)/crea_campana/$',
        login_required(
            views_campana_dialer_template.CreaCampanaTemplateView.as_view()),
        name="crea_campana_dialer_template"),
]

urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.MEDIA_ROOT}
                         )
                        )

# if settings.DEBUG:
#     # static files (images, css, javascript, etc.)
#     urlpatterns += patterns('',
#         (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#             'document_root': settings.MEDIA_ROOT}))
