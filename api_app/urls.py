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

from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from api_app.views import (SupervisorCampanasActivasViewSet, AgentesStatusAPIView,
                           AgentesActivosGrupoViewSet, StatusCampanasEntrantesView,
                           StatusCampanasSalientesView, InteraccionDeSupervisorSobreAgenteView,
                           login, API_ObtenerContactosCampanaView, OpcionesCalificacionViewSet)
from ominicontacto_app.auth.decorators import administrador_o_supervisor_requerido

router = routers.DefaultRouter()
router.register(
    r'api/v1/supervisor/campanas', SupervisorCampanasActivasViewSet,
    base_name='supervisor_campanas')
router.register(
    r'api/v1/grupo/(?P<pk_grupo>\d+)/agentes_activos', AgentesActivosGrupoViewSet,
    base_name='grupo_agentes_activos')
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions/(?P<externalSystem>\w+)',
    OpcionesCalificacionViewSet, base_name='api_campana_opciones_calificacion')
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions',
    OpcionesCalificacionViewSet, base_name='api_campana_opciones_calificacion_intern')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url('api/v1/supervision/status_campanas/entrantes/$',
        administrador_o_supervisor_requerido(StatusCampanasEntrantesView.as_view()),
        name='api_supervision_campanas_entrantes'),
    url('api/v1/supervision/status_campanas/salientes/$',
        administrador_o_supervisor_requerido(StatusCampanasSalientesView.as_view()),
        name='api_supervision_campanas_salientes'),
    url(r'api/v1/supervision/agentes',
        administrador_o_supervisor_requerido(AgentesStatusAPIView.as_view()),
        name='api_agentes_activos'),
    url(r'api/v1/supervision/accion_sobre_agente/(?P<pk>\d+)/$',
        administrador_o_supervisor_requerido(InteraccionDeSupervisorSobreAgenteView.as_view()),
        name='api_accion_sobre_agente'),
    url(r'^api/v1/campaign/(?P<pk_campana>\d+)/contacts/$',
        API_ObtenerContactosCampanaView.as_view(), name='api_contactos_campana'),
    url(r'api/v1/login', login, name='api_login'),
]
