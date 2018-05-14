# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from reportes_app import views_reportes_agentes
from reportes_app.views import (ReporteLlamadasFormView, ExportarReporteLlamadasFormView,
                                ExportarZipReportesLlamadasFormView)
from reportes_app import (views_campanas_preview_reportes, views_campanas_dialer_reportes,
                          views_reportes)

urlpatterns = [
    # ==========================================================================
    # Reportes generales agentes
    # ==========================================================================
    url(r'^reportes/agentes_tiempos/$',
        login_required(views_reportes_agentes.ReportesTiemposAgente.as_view()),
        name='reportes_agentes_tiempos'),
    url(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
        login_required(views_reportes_agentes.exporta_reporte_agente_llamada_view),
        name='reportes_agentes_exporta'),
    # ==========================================================================
    # Reportes generales llamadas
    # ==========================================================================
    url(r'^reporte/llamadas/$',
        login_required(ReporteLlamadasFormView.as_view()),
        name='reporte_llamadas',
        ),
    url(r'^reporte/llamadas/exportar/$',
        login_required(ExportarReporteLlamadasFormView.as_view()),
        name='csv_reporte_llamadas',
        ),
    url(r'^reporte/llamadas/zip/$',
        login_required(ExportarZipReportesLlamadasFormView.as_view()),
        name='zip_reportes_llamadas',
        ),
    # ==========================================================================
    # Reportes desde las campañas
    # ==========================================================================
    url(r'^campana/(?P<pk_campana>\d+)/reporte_calificacion/$',
        login_required(
            views_reportes.CampanaReporteCalificacionListView.as_view()),
        name="campana_reporte_calificacion"),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/$',
        login_required(
            views_reportes.CampanaReporteGraficoView.as_view()),
        name='campana_reporte_grafico',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_pdf/$',
        login_required(
            views_reportes.ExportaCampanaReportePDFView.as_view()),
        name="campana_reporte_pdf"),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/(?P<pk_agente>\d+)/agente/$',
        login_required(
            views_reportes.AgenteCampanaReporteGrafico.as_view()),
        name='campana_reporte_agente',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_reportes.ExportaReporteCampanaView.as_view()),
        name='exporta_campana_reporte',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_reportes.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_formulario_reporte',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta_contactados/$',
        login_required(
            views_reportes.ExportaReporteContactadosView.as_view()),
        name='exporta_reporte_contactados',
        ),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/exporta_calificados/$',
        login_required(
            views_reportes.ExportaReporteCalificadosView.as_view()),
        name='exporta_reporte_calificados',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/no_atendidos/$',
        login_required(
            views_reportes.ExportaReporteNoAtendidosView.as_view()),
        name='exporta_reporte_no_atendidos',
        ),
        url(r'^campana_preview/(?P<pk>\d+)/detalle/$',
        login_required(
            views_campanas_preview_reportes.CampanaPreviewDetailView.as_view()),
        name="campana_preview_detalle"),
    url(r'^campana_preview/(?P<pk>\d+)/detalle_express/$',
        login_required(
            views_campanas_preview_reportes.CampanaPreviewExpressView.as_view()),
        name="campana_preview_detalle_express"),
    url(r'^campana_dialer/detalle_wombat/$',
        login_required(
            views_campanas_dialer_reportes.detalle_campana_dialer_view),
        name="campana_dialer_detalle_wombat"),
    url(r'^campana_dialer/(?P<pk_campana>\d+)/detalle/$',
        login_required(
            views_campanas_dialer_reportes.CampanaDialerDetailView.as_view()),
        name='campana_dialer_detalle',
        ),
]
