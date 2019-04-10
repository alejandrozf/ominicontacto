# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers
from api_app.views import (
    SupervisorCampanasActivasViewSet, AgentesActivosGrupoViewSet, StatusCampanasView
)

from ominicontacto_app.auth.decorators import supervisor_requerido

router = routers.DefaultRouter()
router.register(
    r'api/v1/supervisor/campanas', SupervisorCampanasActivasViewSet,
    base_name='supervisor_campanas')
router.register(
    r'api/v1/grupo/(?P<pk_grupo>\d+)/agentes_activos', AgentesActivosGrupoViewSet,
    base_name='grupo_agentes_activos')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url('api/v1/supervision/status_campanas/entrantes/$',
        supervisor_requerido(StatusCampanasView.as_view()),
        name='api_supervision_campanas_entrantes'),
]
