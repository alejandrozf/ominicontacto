# -*- coding: utf-8 -*-

from django.conf.urls import url

from ominicontacto_app.auth.decorators import user_con_permiso_administracion_requerido

from reportes_app import views_reportes_agentes
from reportes_app.views import (ReporteLlamadasFormView, ExportarReporteLlamadasFormView,
                                ExportarZipReportesLlamadasFormView)
from reportes_app import (views_campanas_preview_reportes, views_campanas_dialer_reportes,
                          views_reportes, views_api_supervision)

urlpatterns = [
    # ==========================================================================
    # Reportes generales agentes
    # ==========================================================================
    url(r'^reportes/agentes_tiempos/$',
        user_con_permiso_administracion_requerido(
            views_reportes_agentes.ReportesTiemposAgente.as_view()),
        name='reportes_agentes_tiempos'),
    url(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
        user_con_permiso_administracion_requerido(
            views_reportes_agentes.exporta_reporte_agente_llamada_view),
        name='reportes_agentes_exporta'),
    url(r'^reportes/agente_por_fecha/$',
        user_con_permiso_administracion_requerido(
            views_reportes_agentes.reporte_por_fecha_modal_agente_view),
        name='reportes_agente_por_fecha'),
    url(r'^reportes/pausa_por_fecha/$',
        user_con_permiso_administracion_requerido(
            views_reportes_agentes.reporte_por_fecha_pausa_modal_agente_view),
        name='reportes_pausa_por_fecha'),
    # ==========================================================================
    # Reportes generales llamadas
    # ==========================================================================
    url(r'^reporte/llamadas/$',
        user_con_permiso_administracion_requerido(ReporteLlamadasFormView.as_view()),
        name='reporte_llamadas',
        ),
    url(r'^reporte/llamadas/exportar/$',
        user_con_permiso_administracion_requerido(ExportarReporteLlamadasFormView.as_view()),
        name='csv_reporte_llamadas',
        ),
    url(r'^reporte/llamadas/zip/$',
        user_con_permiso_administracion_requerido(ExportarZipReportesLlamadasFormView.as_view()),
        name='zip_reportes_llamadas',
        ),
    # ==========================================================================
    # Reportes desde las campañas
    # ==========================================================================
    url(r'^campana/(?P<pk_campana>\d+)/reporte_calificacion/$',
        user_con_permiso_administracion_requerido(
            views_reportes.CampanaReporteCalificacionListView.as_view()),
        name="campana_reporte_calificacion"),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/$',
        user_con_permiso_administracion_requerido(
            views_reportes.CampanaReporteGraficoView.as_view()),
        name='campana_reporte_grafico',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_pdf/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaCampanaReportePDFView.as_view()),
        name="campana_reporte_pdf"),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/(?P<pk_agente>\d+)/agente/$',
        user_con_permiso_administracion_requerido(
            views_reportes.AgenteCampanaReporteGrafico.as_view()),
        name='campana_reporte_agente',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaReporteCampanaView.as_view()),
        name='exporta_campana_reporte',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/exporta/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_formulario_reporte',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta_contactados/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaReporteContactadosView.as_view()),
        name='exporta_reporte_contactados',
        ),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/exporta_calificados/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaReporteCalificadosView.as_view()),
        name='exporta_reporte_calificados',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/no_atendidos/$',
        user_con_permiso_administracion_requerido(
            views_reportes.ExportaReporteNoAtendidosView.as_view()),
        name='exporta_reporte_no_atendidos',
        ),
    url(r'^campana_preview/(?P<pk>\d+)/detalle/$',
        user_con_permiso_administracion_requerido(
            views_campanas_preview_reportes.CampanaPreviewDetailView.as_view()),
        name="campana_preview_detalle"),
    url(r'^campana_preview/(?P<pk>\d+)/detalle_express/$',
        user_con_permiso_administracion_requerido(
            views_campanas_preview_reportes.CampanaPreviewExpressView.as_view()),
        name="campana_preview_detalle_express"),
    url(r'^campana_dialer/detalle_wombat/$',
        user_con_permiso_administracion_requerido(
            views_campanas_dialer_reportes.detalle_campana_dialer_view),
        name="campana_dialer_detalle_wombat"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/detalle/$',
        user_con_permiso_administracion_requerido(
            views_campanas_dialer_reportes.CampanaDialerDetailView.as_view()),
        name='campana_dialer_detalle',
        ),
    # ==========================================================================
    # Api Supervision
    # ==========================================================================
    url(r'^api_supervision/llamadas_campana/(?P<pk_campana>\d+)/$',
        views_api_supervision.LlamadasDeCampanaView.as_view(),
        name='api_supervision_llamadas_campana',
        ),
    url(r'^api_supervision/calificaciones_campana/(?P<pk_campana>\d+)/$',
        views_api_supervision.CalificacionesDeCampanaView.as_view(),
        name='api_supervision_calificaciones_campana',
        ),
]
