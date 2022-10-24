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

from django.urls import re_path
from django.contrib.auth.decorators import login_required

from reportes_app import views_reportes_agentes
from reportes_app.views import (
    ReporteLlamadasFormView, ExportarReporteLlamadasFormView,
    ExportarZipReportesLlamadasFormView,
    ReporteDeResultadosView)
from reportes_app import (
    views_campanas_preview_reportes,
    views_campanas_dialer_reportes,
    views_reportes
)

urlpatterns = [
    # ==========================================================================
    # Reportes generales agentes
    # ==========================================================================
    re_path(r'^reportes/agentes_tiempos/$',
            login_required(
                views_reportes_agentes.ReportesTiemposAgente.as_view()),
            name='reportes_agentes_tiempos'),
    re_path(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
            login_required(
                views_reportes_agentes.exporta_reporte_agente_llamada_view),
            name='reportes_agentes_exporta'),
    re_path(r'^reportes/agente_por_fecha/$',
            login_required(
                views_reportes_agentes.reporte_por_fecha_modal_agente_view),
            name='reportes_agente_por_fecha'),
    re_path(r'^reportes/pausa_por_fecha/$',
            login_required(
                views_reportes_agentes.reporte_por_fecha_pausa_modal_agente_view),
            name='reportes_pausa_por_fecha'),
    re_path(r'^reportes/historico_llamadas_del_dia/$',
            login_required(views_reportes_agentes.HistoricoDeLlamadasView.as_view()),
            name='historico_de_llamadas_de_agente',
            ),
    # ==========================================================================
    # Reportes generales llamadas
    # ==========================================================================
    re_path(r'^reporte/llamadas/$',
            login_required(ReporteLlamadasFormView.as_view()),
            name='reporte_llamadas',
            ),
    re_path(r'^reporte/llamadas/exportar/$',
            login_required(ExportarReporteLlamadasFormView.as_view()),
            name='csv_reporte_llamadas',
            ),
    re_path(r'^reporte/llamadas/zip/$',
            login_required(ExportarZipReportesLlamadasFormView.as_view()),
            name='zip_reportes_llamadas',
            ),
    # ==========================================================================
    # Reportes desde las campañas
    # ==========================================================================
    re_path(r'^campana/(?P<pk_campana>\d+)/reporte_calificacion/$',
            login_required(
                views_reportes.CampanaReporteCalificacionListView.as_view()),
            name="campana_reporte_calificacion"),
    re_path(r'^campana/(?P<pk_campana>\d+)/exporta/$',
            login_required(
                views_reportes.ExportaCampanaReporteCalificacionView.as_view()),
            name='exporta_campana_reporte_calificacion',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/$',
            login_required(
                views_reportes.CampanaReporteGraficoView.as_view()),
            name='campana_reporte_grafico',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/reporte_pdf/$',
            login_required(
                views_reportes.ExportaCampanaReporteGraficoPDFView.as_view()),
            name="campana_reporte_grafico_pdf"),
    re_path(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/(?P<pk_agente>\d+)/agente/$',
            login_required(
                views_reportes.AgenteCampanaReporteGrafico.as_view()),
            name='campana_reporte_grafico_agente',
            ),
    re_path(r'^formulario/(?P<pk_campana>\d+)/exporta/$',
            login_required(
                views_reportes.ExportaReporteFormularioVentaView.as_view()),
            name='exporta_reporte_calificaciones_gestion',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/exporta_contactados/$',
            login_required(
                views_reportes.ExportaReporteLlamadosContactadosView.as_view()),
            name='exporta_reporte_llamados_contactados',
            ),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/exporta_calificados/$',
            login_required(
                views_reportes.ExportaReporteCalificadosView.as_view()),
            name='exporta_reporte_calificados',
            ),
    re_path(r'^campana/(?P<pk_campana>\d+)/exporta/no_atendidos/$',
            login_required(
                views_reportes.ExportaReporteNoAtendidosView.as_view()),
            name='exporta_reporte_no_atendidos',
            ),
    re_path(r'^campana_preview/(?P<pk>\d+)/detalle/$',
            login_required(
                views_campanas_preview_reportes.CampanaPreviewDetailView.as_view()),
            name="campana_preview_detalle"),
    re_path(r'^campana_preview/(?P<pk>\d+)/detalle_express/$',
            login_required(
                views_campanas_preview_reportes.CampanaPreviewExpressView.as_view()),
            name="campana_preview_detalle_express"),
    re_path(r'^campana_dialer/detalle_wombat/$',
            login_required(
                views_campanas_dialer_reportes.detalle_campana_dialer_view),
            name="campana_dialer_detalle_wombat"),
    re_path(r'^campana_dialer/(?P<pk_campana>\d+)/detalle/$',
            login_required(
                views_campanas_dialer_reportes.CampanaDialerDetailView.as_view()),
            name='campana_dialer_detalle',
            ),
    re_path(r'^reporte_de_resultados/(?P<pk_campana>\d+)/$',
            login_required(
                ReporteDeResultadosView.as_view()),
            name='reporte_de_resultados',
            ),
    re_path(r'^resultados_de_base_campana/(?P<pk_campana>\d+)/(?P<all_data>\d+)/$',
            login_required(
                views_reportes.ExportaReporteResultadosDeBaseView.as_view()),
            name='exporta_reporte_resultados_de_base_contactaciones',
            ),
]
