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

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from reportes_app import views_reportes_agentes
from reportes_app.views import (ReporteLlamadasFormView, ExportarReporteLlamadasFormView,
                                ExportarZipReportesLlamadasFormView,
                                ReporteDeResultadosView, ReporteDeResultadosCSVView)
from reportes_app import (views_campanas_preview_reportes, views_campanas_dialer_reportes,
                          views_reportes, )

urlpatterns = [
    # ==========================================================================
    # Reportes generales agentes
    # ==========================================================================
    url(r'^reportes/agentes_tiempos/$',
        login_required(
            views_reportes_agentes.ReportesTiemposAgente.as_view()),
        name='reportes_agentes_tiempos'),
    url(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
        login_required(
            views_reportes_agentes.exporta_reporte_agente_llamada_view),
        name='reportes_agentes_exporta'),
    url(r'^reportes/agente_por_fecha/$',
        login_required(
            views_reportes_agentes.reporte_por_fecha_modal_agente_view),
        name='reportes_agente_por_fecha'),
    url(r'^reportes/pausa_por_fecha/$',
        login_required(
            views_reportes_agentes.reporte_por_fecha_pausa_modal_agente_view),
        name='reportes_pausa_por_fecha'),
    url(r'^reportes/historico_llamadas_del_dia/$',
        login_required(views_reportes_agentes.HistoricoDeLlamadasView.as_view()),
        name='historico_de_llamadas_de_agente',
        ),
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
    url(r'^campana/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_reportes.ExportaCampanaReporteCalificacionView.as_view()),
        name='exporta_campana_reporte_calificacion',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/$',
        login_required(
            views_reportes.CampanaReporteGraficoView.as_view()),
        name='campana_reporte_grafico',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_pdf/$',
        login_required(
            views_reportes.ExportaCampanaReporteGraficoPDFView.as_view()),
        name="campana_reporte_grafico_pdf"),
    url(r'^campana/(?P<pk_campana>\d+)/reporte_grafico/(?P<pk_agente>\d+)/agente/$',
        login_required(
            views_reportes.AgenteCampanaReporteGrafico.as_view()),
        name='campana_reporte_grafico_agente',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_reportes.ExportaReporteFormularioVentaView.as_view()),
        name='exporta_reporte_calificaciones_gestion',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta_contactados/$',
        login_required(
            views_reportes.ExportaReporteLlamadosContactadosView.as_view()),
        name='exporta_reporte_llamados_contactados',
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
    url(r'^reporte_de_resultados/(?P<pk_campana>\d+)/$',
        login_required(
            ReporteDeResultadosView.as_view()),
        name='reporte_de_resultados',
        ),
    url(r'^reporte_de_resultados_csv/(?P<pk_campana>\d+)/$',
        login_required(
            ReporteDeResultadosCSVView.as_view()),
        name='reporte_de_resultados_csv',
        ),
]
