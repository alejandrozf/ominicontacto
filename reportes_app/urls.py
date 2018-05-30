# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from reportes_app import views_reportes_agentes

urlpatterns = [
        url(r'^reportes/agentes_tiempos/$',
            login_required(views_reportes_agentes.ReportesTiemposAgente.as_view()),
            name='reportes_agentes_tiempos'),
        url(r'^reportes/agentes_export/(?P<tipo_reporte>[\w\-]+)/$',
            login_required(views_reportes_agentes.exporta_reporte_agente_llamada_view),
            name='reportes_agentes_exporta'),
        url(r'^reportes/agente_por_fecha/$',
            login_required(views_reportes_agentes.reporte_por_fecha_modal_agente_view),
            name='reportes_agente_por_fecha'),
]
