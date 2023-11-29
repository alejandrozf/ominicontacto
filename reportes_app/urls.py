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

from django.urls import path, re_path
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
from whatsapp_app import views as whatsapp_views

urlpatterns = [
    # ==========================================================================
    # Reportes generales agentes
    # ==========================================================================
    path('reportes/agentes_tiempos/',
         login_required(
             views_reportes_agentes.ReportesTiemposAgente.as_view()),
         name='reportes_agentes_tiempos'),
    re_path(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
            login_required(
                views_reportes_agentes.exporta_reporte_agente_llamada_view),
            name='reportes_agentes_exporta'),
    path('reportes/agente_por_fecha/',
         login_required(
             views_reportes_agentes.reporte_por_fecha_modal_agente_view),
         name='reportes_agente_por_fecha'),
    path('reportes/pausa_por_fecha/',
         login_required(
             views_reportes_agentes.reporte_por_fecha_pausa_modal_agente_view),
         name='reportes_pausa_por_fecha'),
    path('reportes/historico_llamadas_del_dia/',
         login_required(views_reportes_agentes.HistoricoDeLlamadasView.as_view()),
         name='historico_de_llamadas_de_agente',
         ),
    # ==========================================================================
    # Reportes generales llamadas
    # ==========================================================================
    path('reporte/llamadas/',
         login_required(ReporteLlamadasFormView.as_view()),
         name='reporte_llamadas',
         ),
    path('reporte/llamadas/exportar/',
         login_required(ExportarReporteLlamadasFormView.as_view()),
         name='csv_reporte_llamadas',
         ),
    path('reporte/llamadas/zip/',
         login_required(ExportarZipReportesLlamadasFormView.as_view()),
         name='zip_reportes_llamadas',
         ),
    # ==========================================================================
    # Reportes desde las campañas
    # ==========================================================================
    path('campana/<int:pk_campana>/reporte_calificacion/',
         login_required(
             views_reportes.CampanaReporteCalificacionListView.as_view()),
         name="campana_reporte_calificacion"),
    path('campana/<int:pk_campana>/exporta/',
         login_required(
             views_reportes.ExportaCampanaReporteCalificacionView.as_view()),
         name='exporta_campana_reporte_calificacion',
         ),
    path('campana/<int:pk_campana>/reporte_grafico/',
         login_required(
             views_reportes.CampanaReporteGraficoView.as_view()),
         name='campana_reporte_grafico',
         ),
    path('campana/<int:pk_campana>/reporte_pdf/',
         login_required(
             views_reportes.ExportaCampanaReporteGraficoPDFView.as_view()),
         name="campana_reporte_grafico_pdf"),
    path('campana/<int:pk_campana>/reporte_grafico/<int:pk_agente>/agente/',
         login_required(
             views_reportes.AgenteCampanaReporteGrafico.as_view()),
         name='campana_reporte_grafico_agente',
         ),
    path('formulario/<int:pk_campana>/exporta/',
         login_required(
             views_reportes.ExportaReporteFormularioVentaView.as_view()),
         name='exporta_reporte_calificaciones_gestion',
         ),
    path('campana/<int:pk_campana>/exporta_contactados/',
         login_required(
             views_reportes.ExportaReporteLlamadosContactadosView.as_view()),
         name='exporta_reporte_llamados_contactados',
         ),
    path('campana_dialer/<int:pk_campana>/exporta_calificados/',
         login_required(
             views_reportes.ExportaReporteCalificadosView.as_view()),
         name='exporta_reporte_calificados',
         ),
    path('campana/<int:pk_campana>/exporta/no_atendidos/',
         login_required(
             views_reportes.ExportaReporteNoAtendidosView.as_view()),
         name='exporta_reporte_no_atendidos',
         ),
    path('campana_preview/<int:pk>/detalle/',
         login_required(
             views_campanas_preview_reportes.CampanaPreviewDetailView.as_view()),
         name="campana_preview_detalle"),
    path('campana_preview/<int:pk>/detalle_express/',
         login_required(
             views_campanas_preview_reportes.CampanaPreviewExpressView.as_view()),
         name="campana_preview_detalle_express"),
    path('campana_dialer/detalle_wombat/',
         login_required(
             views_campanas_dialer_reportes.detalle_campana_dialer_view),
         name="campana_dialer_detalle_wombat"),
    path('campana_dialer/<int:pk_campana>/detalle/',
         login_required(
             views_campanas_dialer_reportes.CampanaDialerDetailView.as_view()),
         name='campana_dialer_detalle',
         ),
    path('reporte_de_resultados/<int:pk_campana>/',
         login_required(
             ReporteDeResultadosView.as_view()),
         name='reporte_de_resultados',
         ),
    path('campana/<int:pk_campana>/whatsapp_conversations_report/',
         login_required(
             whatsapp_views.CampaignReportConversationsListView.as_view()),
         name='campaign_whatsapp_report_conversations',
         ),
    re_path(r'^resultados_de_base_campana/(?P<pk_campana>\d+)/(?P<all_data>\d+)/$',
            login_required(
                views_reportes.ExportaReporteResultadosDeBaseView.as_view()),
            name='exporta_reporte_resultados_de_base_contactaciones',
            ),
]
