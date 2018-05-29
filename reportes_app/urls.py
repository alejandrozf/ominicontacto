# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from reportes_app import views_reportes_agentes
from reportes_app.views import (ReporteLlamadasFormView, ExportarReporteLlamadasFormView,
                                ExportarZipReportesLlamadasFormView)

urlpatterns = [
    url(r'^reportes/agentes_tiempos/$',
        login_required(views_reportes_agentes.ReportesTiemposAgente.as_view()),
        name='reportes_agentes_tiempos'),
    url(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
        login_required(views_reportes_agentes.exporta_reporte_agente_llamada_view),
        name='reportes_agentes_exporta'),
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
]
