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
from django.contrib.auth.decorators import login_required

from api_app.views.base import login, ContactoCreateView, CampaignDatabaseMetadataView
from api_app.views.administrador import AgentesActivosGrupoViewSet
from api_app.views.supervisor import (
    SupervisorCampanasActivasViewSet, AgentesStatusAPIView, StatusCampanasEntrantesView,
    StatusCampanasSalientesView, InteraccionDeSupervisorSobreAgenteView, LlamadasDeCampanaView,
    CalificacionesDeCampanaView)
from api_app.views.agente import (
    OpcionesCalificacionViewSet, ApiCalificacionClienteView, ApiCalificacionClienteCreateView,
    API_ObtenerContactosCampanaView, Click2CallView, AgentLogoutView,
    AgentLoginAsterisk, AgentLogoutAsterisk, AgentPauseAsterisk, AgentUnpauseAsterisk
)

router = routers.DefaultRouter()

#####################################################
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# ###########  ADMINISTRADOR  ############ #
router.register(
    r'api/v1/grupo/(?P<pk_grupo>\d+)/agentes_activos', AgentesActivosGrupoViewSet,
    base_name='api_agentes_activos_de_grupo')

# ###########   SUPERVISOR    ############ #
router.register(
    r'api/v1/supervisor/campanas', SupervisorCampanasActivasViewSet,
    base_name='api_campanas_de_supervisor')

# ###########     AGENTE      ############ #
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions/(?P<externalSystem>\w+)',
    OpcionesCalificacionViewSet, base_name='api_campana_opciones_calificacion')
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions',
    OpcionesCalificacionViewSet, base_name='api_campana_opciones_calificacion_intern')
router.register(r'api/v1/disposition', ApiCalificacionClienteView, base_name='api_disposition')
router.register(
    r'api/v1/new_contact/disposition', ApiCalificacionClienteCreateView,
    base_name='api_disposition_new_contact')


urlpatterns = [
    # ###########   TODOS/BASE    ############ #
    url(r'^', include(router.urls)),
    url(r'api/v1/login', login, name='api_login'),

    url(r'api/v1/new_contact/', ContactoCreateView.as_view(),
        name='api_new_contact'),
    url(r'api/v1/campaign/database_metadata/', CampaignDatabaseMetadataView.as_view(),
        name='api_campaign_database_metadata'),

    url(r'^api_supervision/llamadas_campana/(?P<pk_campana>\d+)/$',
        LlamadasDeCampanaView.as_view(),
        name='api_supervision_llamadas_campana',
        ),
    url(r'^api_supervision/calificaciones_campana/(?P<pk_campana>\d+)/$',
        CalificacionesDeCampanaView.as_view(),
        name='api_supervision_calificaciones_campana',
        ),

    # ###########   SUPERVISOR    ############ #
    url(r'api/v1/supervision/agentes',
        login_required(AgentesStatusAPIView.as_view()),
        name='api_agentes_activos'),
    url('api/v1/supervision/status_campanas/entrantes/$',
        login_required(StatusCampanasEntrantesView.as_view()),
        name='api_supervision_campanas_entrantes'),
    url('api/v1/supervision/status_campanas/salientes/$',
        login_required(StatusCampanasSalientesView.as_view()),
        name='api_supervision_campanas_salientes'),
    url(r'api/v1/supervision/accion_sobre_agente/(?P<pk>\d+)/$',
        login_required(InteraccionDeSupervisorSobreAgenteView.as_view()),
        name='api_accion_sobre_agente'),

    # ###########     AGENTE      ############ #
    url(r'^api/v1/campaign/(?P<pk_campana>\d+)/contacts/$',
        API_ObtenerContactosCampanaView.as_view(), name='api_contactos_campana'),
    url(r'api/v1/makeCall/$',
        Click2CallView.as_view(),
        name='api_click2call'),
    url(r'^api/v1/asterisk_login/$',
        AgentLoginAsterisk.as_view(), name='api_agent_asterisk_login'),
    url(r'^api/v1/asterisk_logout/$',
        AgentLogoutAsterisk.as_view(), name='api_agent_asterisk_logout'),
    url(r'^agente/logout/$', login_required(AgentLogoutView.as_view()),
        name='api_agente_logout'),
    url(r'^api/v1/asterisk_pause/$',
        AgentPauseAsterisk.as_view(), name='api_make_pause'),
    url(r'^api/v1/asterisk_unpause/$',
        AgentUnpauseAsterisk.as_view(), name='api_make_unpause'),

]
