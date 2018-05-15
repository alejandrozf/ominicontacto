# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from reportes_app import views_reportes_agentes

urlpatterns = [
        url(r'^reportes/agentes_tiempos/$',
            login_required(views_reportes_agentes.ReportesTiemposAgente.as_view()),
            name='reportes_agentes_tiempos'),
]
