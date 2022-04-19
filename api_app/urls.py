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
from api_app.views.usuarios import ListadoAgentes, ListadoGrupos

from django.conf.urls import url, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required

from api_app.views.base import (
    login, ContactoCreateView, CampaignDatabaseMetadataView, CamposDireccionView)
from api_app.views.administrador import (
    AgentesActivosGrupoViewSet, CrearRolView, EliminarRolView, ActualizarPermisosDeRolView,
    SubirBaseContactosView, EnviarKeyRegistro)
from api_app.views.supervisor import (
    SupervisorCampanasActivasViewSet, AgentesStatusAPIView,
    StatusCampanasSalientesView, InteraccionDeSupervisorSobreAgenteView, LlamadasDeCampanaView,
    CalificacionesDeCampanaView, ReasignarAgendaContactoView, DataAgendaContactoView,
    ExportarCSVContactados, ExportarCSVCalificados, ExportarCSVNoAtendidos,
    StatusCampanasEntrantesView, Pausas,
    ContactosAsignadosCampanaPreviewView, ExportarCSVCalificacionesCampana,
    ExportarCSVFormularioGestionCampana, ExportarCSVResultadosBaseContactados,
    DashboardSupervision, AuditSupervisor,
    AgentesCampana, ActualizaAgentesCampana, AgentesActivos,
    ConjuntoDePausaCreate, ConjuntoDePausaDelete, ConjuntoDePausaDetalle,
    ConjuntoDePausaList, ConjuntoDePausaUpdate, ConfiguracionDePausaCreate,
    ConfiguracionDePausaDelete, ConfiguracionDePausaUpdate)
from api_app.views.agente import (
    ObtenerCredencialesSIPAgenteView,
    OpcionesCalificacionViewSet, ApiCalificacionClienteView, ApiCalificacionClienteCreateView,
    API_ObtenerContactosCampanaView, Click2CallView, AgentLogoutView,
    AgentLoginAsterisk, AgentLogoutAsterisk, AgentPauseAsterisk, AgentUnpauseAsterisk,
    SetEstadoRevisionAuditoria, ApiStatusCalificacionLlamada, ApiEventoHold, AgentRingingAsterisk
)
from api_app.views.grabaciones import ObtenerArchivoGrabacionView, ObtenerArchivosGrabacionView
from api_app.views.audios import ListadoAudiosView

router = routers.DefaultRouter()

#####################################################
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# ###########  ADMINISTRADOR  ############ #
router.register(
    r'api/v1/grupo/(?P<pk_grupo>\d+)/agentes_activos', AgentesActivosGrupoViewSet,
    base_name='api_agentes_activos_de_grupo')


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

    url(r'api/v1/campaign/database_metadata_columns_fields/(?P<pk>\d+)/$',
        CamposDireccionView.as_view(), name='api_database_metadata_columns_fields'),

    # ###########   ADMINISTRADOR    ############ #
    url(r'api/v1/permissions/new_role/$',
        CrearRolView.as_view(),
        name='api_new_role'),
    url(r'api/v1/permissions/delete_role/$',
        EliminarRolView.as_view(),
        name='api_delete_role'),
    url(r'api/v1/permissions/update_role_permissions/$',
        ActualizarPermisosDeRolView.as_view(),
        name='api_update_role_permissions'),
    url(r'api/v1/crear_base_contactos/$',
        SubirBaseContactosView.as_view(),
        name='api_upload_base_contactos'),
    url(r'api/v1/reenviar_key_registro/$',
        EnviarKeyRegistro.as_view(),
        name='reenviar_key_registro'),
    # ###########   SUPERVISOR    ############ #
    url(r'api/v1/supervisor/campanas',
        SupervisorCampanasActivasViewSet.as_view(),
        name='api_campanas_de_supervisor'),
    url(r'api/v1/supervision/agentes',
        login_required(AgentesStatusAPIView.as_view()),
        name='api_agentes_activos'),
    url(r'api/v1/supervision/status_campanas/entrantes/$',
        login_required(StatusCampanasEntrantesView.as_view()),
        name='api_supervision_campanas_entrantes'),
    url(r'api/v1/supervision/status_campanas/salientes/$',
        login_required(StatusCampanasSalientesView.as_view()),
        name='api_supervision_campanas_salientes'),
    url(r'api/v1/supervision/accion_sobre_agente/(?P<pk>\d+)/$',
        login_required(InteraccionDeSupervisorSobreAgenteView.as_view()),
        name='api_accion_sobre_agente'),
    url(r'^api_supervision/llamadas_campana/(?P<pk_campana>\d+)/$',
        LlamadasDeCampanaView.as_view(),
        name='api_supervision_llamadas_campana',
        ),
    url(r'^api_supervision/calificaciones_campana/(?P<pk_campana>\d+)/$',
        CalificacionesDeCampanaView.as_view(),
        name='api_supervision_calificaciones_campana',
        ),
    url(r'api/v1/supervision/reasignar_agenda_contacto/$',
        ReasignarAgendaContactoView.as_view(),
        name='api_reasignar_agenda_contacto'),
    url(r'api/v1/supervision/data_agenda_contacto/(?P<agenda_id>\d+)/$',
        DataAgendaContactoView.as_view(),
        name='api_data_agenda_contacto'),
    url(r'api/v1/exportar_csv_contactados/$',
        ExportarCSVContactados.as_view(),
        name='api_exportar_csv_contactados'),
    url(r'api/v1/exportar_csv_calificados/$',
        ExportarCSVCalificados.as_view(),
        name='api_exportar_csv_calificados'),
    url(r'api/v1/exportar_csv_no_atendidos/$',
        ExportarCSVNoAtendidos.as_view(),
        name='api_exportar_csv_no_atendidos'),
    url(r'api/vi/supervision/contactos_asignados_preview/(?P<pk_campana>\d+)/$',
        ContactosAsignadosCampanaPreviewView.as_view(),
        name='api_contactos_asignados_campana_preview'),
    url(r'api/v1/exportar_csv_calificaciones_campana/$',
        ExportarCSVCalificacionesCampana.as_view(),
        name='api_exportar_csv_calificaciones_campana'),
    url(r'api/v1/exportar_csv_formulario_gestion_campana/$',
        ExportarCSVFormularioGestionCampana.as_view(),
        name='api_exportar_csv_formulario_gestion_campana'),
    url(r'api/v1/exportar_csv_resultados_base_contactados/$',
        ExportarCSVResultadosBaseContactados.as_view(),
        name='api_exportar_csv_resultados_base_contactados'),
    url(r'api/v1/dashboard_supervision/$',
        DashboardSupervision.as_view(),
        name='api_dashboard_supervision'),
    url(r'api/v1/campaign/(?P<pk_campana>\d+)/agents/$',
        AgentesCampana.as_view(),
        name='api_agents_campaign'),
    url(r'api/v1/campaign/agents_update/$',
        ActualizaAgentesCampana.as_view(),
        name='api_update_agents_campaign'),
    url(r'api/v1/active_agents/$',
        AgentesActivos.as_view(),
        name='api_active_agents'),
    # Conjuntos de Pausas
    url(r'api/v1/pauses/$',
        Pausas.as_view(),
        name='api_pauses_list'),
    url(r'api/v1/pause_sets/$',
        ConjuntoDePausaList.as_view(),
        name='api_pause_set_list'),
    url(r'api/v1/pause_sets/(?P<pk>\d+)/$',
        ConjuntoDePausaDetalle.as_view(),
        name='api_pause_set_detail'),
    url(r'api/v1/pause_sets/create/$',
        ConjuntoDePausaCreate.as_view(),
        name='api_pause_set_create'),
    url(r'api/v1/pause_sets/(?P<pk>\d+)/update/$',
        ConjuntoDePausaUpdate.as_view(),
        name='api_pause_set_update'),
    url(r'api/v1/pause_sets/(?P<pk>\d+)/delete/$',
        ConjuntoDePausaDelete.as_view(),
        name='api_pause_set_delete'),
    url(r'api/v1/pause_config/create/$',
        ConfiguracionDePausaCreate.as_view(),
        name='api_pause_config_create'),
    url(r'api/v1/pause_config/(?P<pk>\d+)/update/$',
        ConfiguracionDePausaUpdate.as_view(),
        name='api_pause_config_update'),
    url(r'api/v1/pause_config/(?P<pk>\d+)/delete/$',
        ConfiguracionDePausaDelete.as_view(),
        name='api_pause_config_delete'),
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
    url(r'^api/v1/asterisk_ringing/$',
        AgentRingingAsterisk.as_view(), name='api_make_ringing'),
    url(r'api/v1/sip/credentials/agent/', ObtenerCredencialesSIPAgenteView.as_view(),
        name='api_credenciales_sip_agente'),
    url(r'api/v1/audit/set_revision_status/', SetEstadoRevisionAuditoria.as_view(),
        name='api_set_estado_revision'),
    url(r'api/v1/calificar_llamada/', ApiStatusCalificacionLlamada.as_view(),
        name='api_status_calificacion_llamada'),
    url(r'api/v1/evento_hold/', ApiEventoHold.as_view(),
        name='api_evento_hold'),
    # ###########     GRABACIONES      ############ #
    url(r'^api/v1/grabacion/archivo/$',
        ObtenerArchivoGrabacionView.as_view(), name='api_grabacion_archivo'),
    url(r'^api/v1/grabacion/descarga_masiva',
        ObtenerArchivosGrabacionView.as_view(), name='api_grabacion_descarga_masiva'),
    # ###########  AUDIOS ASTERISK    ############ #
    url(r'^api/v1/audio/list',
        ListadoAudiosView.as_view({'get': 'list'}), name='api_audios_listado'),
    # ###########  USUARIOS    ############ #
    url(r'^api/v1/group/list',
        ListadoGrupos.as_view({'get': 'list'}), name='api_grupos'),
    url(r'^api/v1/agent/list',
        ListadoAgentes.as_view({'get': 'list'}), name='api_agentes'),
    url(r'^api/v1/audit_supervisor',
        AuditSupervisor.as_view(), name='api_audit_supervisor'),

]
