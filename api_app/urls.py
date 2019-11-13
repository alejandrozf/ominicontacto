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
                           login, API_ObtenerContactosCampanaView, ApiCalificacionClienteView,
                           ApiCalificacionClienteCreateView, OpcionesCalificacionViewSet,
                           Click2CallView, AgentLoginAsterisk, AgentLogoutAsterisk,
                           AgentPauseAsterisk, AgentUnpauseAsterisk, ContactoCreateView)
from ominicontacto_app.auth.decorators import supervisor_requerido, agente_requerido

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
router.register(r'api/v1/disposition', ApiCalificacionClienteView, base_name='disposition')
router.register(
    r'api/v1/new_contact/disposition', ApiCalificacionClienteCreateView,
    base_name='disposition_new_contact')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url('api/v1/supervision/status_campanas/entrantes/$',
        supervisor_requerido(StatusCampanasEntrantesView.as_view()),
        name='api_supervision_campanas_entrantes'),
    url('api/v1/supervision/status_campanas/salientes/$',
        supervisor_requerido(StatusCampanasSalientesView.as_view()),
        name='api_supervision_campanas_salientes'),
    url(r'api/v1/supervision/agentes',
        supervisor_requerido(AgentesStatusAPIView.as_view()),
        name='api_agentes_activos'),
    url(r'api/v1/supervision/accion_sobre_agente/(?P<pk>\d+)/$',
        supervisor_requerido(InteraccionDeSupervisorSobreAgenteView.as_view()),
        name='api_accion_sobre_agente'),
    url(r'^api/v1/campaign/(?P<pk_campana>\d+)/contacts/$',
        API_ObtenerContactosCampanaView.as_view(), name='api_contactos_campana'),
    url(r'api/v1/login', login, name='api_login'),
    url(r'^api/v1/asterisk_login/$',
        agente_requerido(AgentLoginAsterisk.as_view()), name='agent_asterisk_login'),
    url(r'^api/v1/asterisk_pause/$',
        agente_requerido(AgentPauseAsterisk.as_view()), name='make_pause'),
    url(r'^api/v1/asterisk_unpause/$',
        agente_requerido(AgentUnpauseAsterisk.as_view()), name='make_unpause'),
    url(r'api/v1/makeCall/$',
        Click2CallView.as_view(),
        name='api_click2call'),
    url(r'^agente/logout/$', agente_requerido(AgentLogoutAsterisk.as_view()),
        name='agente_logout'),
    url(r'api/v1/new_contact/', ContactoCreateView.as_view(),
        name='api_new_contact')
]
