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

from __future__ import unicode_literals
from api_app.views.usuarios import ListadoAgentes, ListadoGrupos

from django.urls import include, re_path, path
from rest_framework import routers
from django.contrib.auth.decorators import login_required

from api_app.views.base import login
from api_app.views.base_de_contactos import (
    CampaingsOnDB, ContactoDeCampanaCreateView, CampaignDatabaseMetadataView, CamposDireccionView,
    BaseDatosContactoCreateView, ContactoCreateView, )
from api_app.views.administrador import (
    AgentesActivosGrupoViewSet, CrearRolView, EliminarRolView, ActualizarPermisosDeRolView,
    SubirBaseContactosView, EnviarKeyRegistro)
from api_app.views.supervisor import (
    SupervisorCampanasActivasViewSet, AgentesStatusAPIView,
    StatusCampanasSalientesView, InteraccionDeSupervisorSobreAgenteView,
    LlamadasDeCampanaView, CalificacionesDeCampanaView,
    ReasignarAgendaContactoView, DataAgendaContactoView,
    ExportarCSVContactados, ExportarCSVCalificados, ExportarCSVNoAtendidos,
    StatusCampanasEntrantesView, ContactosAsignadosCampanaPreviewView,
    ExportarCSVCalificacionesCampana, ExportarCSVFormularioGestionCampana,
    ExportarCSVResultadosBaseContactados, DashboardSupervision, AuditSupervisor)
from api_app.views.campaigns.add_agents_to_campaign import (
    AgentesCampana, ActualizaAgentesCampana, AgentesActivos)
from api_app.views.pause_set import (
    ConjuntoDePausaCreate, ConjuntoDePausaDelete, ConjuntoDePausaDetalle,
    ConjuntoDePausaList, ConjuntoDePausaUpdate, ConfiguracionDePausaCreate,
    ConfiguracionDePausaDelete, ConfiguracionDePausaUpdate, Pausas)
from api_app.views.external_site import (
    SitioExternoCreate, SitioExternoDelete, SitioExternoDesocultar,
    SitioExternoDetalle, SitioExternoList, SitioExternoOcultar,
    SitioExternoUpdate)
from api_app.views.external_site_authentication import (
    ExternalSiteAuthenticationCreate,
    ExternalSiteAuthenticationDelete,
    ExternalSiteAuthenticationDetail,
    ExternalSiteAuthenticationList,
    ExternalSiteAuthenticationUpdate)
from api_app.views.call_disposition import (
    CalificacionCreate, CalificacionDelete, CalificacionDetail,
    CalificacionList, CalificacionUpdate)
from api_app.views.external_system import (
    AgentesSistemaExternoList, SistemaExternoCreate, SistemaExternoDetail,
    SistemaExternoList, SistemaExternoUpdate)
from api_app.views.form import (
    FormCreate, FormDelete, FormDetail,
    FormHide, FormList, FormShow, FormUpdate)
from api_app.views.pause import (
    PauseCreate, PauseDelete, PauseDetail, PauseList, PauseReactivate,
    PauseUpdate)
from api_app.views.inbound_route import (
    InboundRouteCreate, InboundRouteDelete, InboundRouteDestinations,
    InboundRouteDetail, InboundRouteList, InboundRouteUpdate)
from api_app.views.outbound_route import (
    OutboundRouteCreate, OutboundRouteDelete, OutboundRouteList,
    OutboundRouteDetail, OutboundRouteOrphanTrunks, OutboundRouteReorder,
    OutboundRouteSIPTrunksList, OutboundRouteUpdate)
from api_app.views.group_of_hour import (
    GroupOfHourCreate, GroupOfHourDelete, GroupOfHourList,
    GroupOfHourDetail, GroupOfHourUpdate)
from api_app.views.ivr import (
    IVRAudioOptions, IVRCreate, IVRDelete, IVRDestinationTypes, IVRList,
    IVRDetail, IVRUpdate)
from api_app.views.register_server import (
    RegisterServerCreate,
    RegisterServerList)
from api_app.views.agente import (
    ObtenerCredencialesSIPAgenteView,
    OpcionesCalificacionViewSet, ApiCalificacionClienteView, ApiCalificacionClienteCreateView,
    API_ObtenerContactosCampanaView, Click2CallView, AgentLogoutView, HangUpCallView,
    AgentLoginAsterisk, AgentLogoutAsterisk, AgentPauseAsterisk, AgentUnpauseAsterisk,
    SetEstadoRevisionAuditoria, ApiStatusCalificacionLlamada, ApiEventoHold, AgentRingingAsterisk,
    AgentRejectCallAsterisk, Click2CallOutsideCampaign, ApiAgentesParaTransferencia,
    AgentDisabledAsterisk,
)
from api_app.views.grabaciones import (
    ObtenerArchivoGrabacionView, ObtenerArchivosGrabacionView, ObtenerUrlGrabacionView
)
from api_app.views.auditoria import ObtenerArchivoAuditoriaView
from api_app.views.audios import ListadoAudiosView
from api_app.views.wombat_dialer import ReiniciarWombat, WombatState
from api_app.views.system import AsteriskQueuesData

from api_app.views.destino_entrante import DestinoEntranteView, DestinoEntranteTiposView
from api_app.views.logging import TransferenciaAEncuestaLogCreateView
from api_app.views.reports import AgentStatusView, AgentStatusListView, CallStatusView


router = routers.DefaultRouter()

#####################################################
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# ###########  ADMINISTRADOR  ############ #
router.register(
    r'api/v1/grupo/(?P<pk_grupo>\d+)/agentes_activos', AgentesActivosGrupoViewSet,
    basename='api_agentes_activos_de_grupo')


# ###########     AGENTE      ############ #
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions/(?P<externalSystem>\w+)',
    OpcionesCalificacionViewSet, basename='api_campana_opciones_calificacion')
router.register(
    r'api/v1/campaign/(?P<campaign>\w+)/dispositionOptions',
    OpcionesCalificacionViewSet, basename='api_campana_opciones_calificacion_intern')
router.register(r'api/v1/disposition', ApiCalificacionClienteView, basename='api_disposition')
router.register(
    r'api/v1/new_contact/disposition', ApiCalificacionClienteCreateView,
    basename='api_disposition_new_contact')


urlpatterns = [

    # ###########   TODOS/BASE    ############ #
    re_path(r'^', include(router.urls)),
    path('api/v1/login', login, name='api_login'),
    # ###########   ADMINISTRADOR    ############ #
    re_path(r'api/v1/permissions/new_role/$',
            CrearRolView.as_view(),
            name='api_new_role'),
    re_path(r'api/v1/permissions/delete_role/$',
            EliminarRolView.as_view(),
            name='api_delete_role'),
    re_path(r'api/v1/permissions/update_role_permissions/$',
            ActualizarPermisosDeRolView.as_view(),
            name='api_update_role_permissions'),
    re_path(r'api/v1/crear_base_contactos/$',
            SubirBaseContactosView.as_view(),
            name='api_upload_base_contactos'),
    re_path(r'api/v1/reenviar_key_registro/$',
            EnviarKeyRegistro.as_view(),
            name='reenviar_key_registro'),
    # ###########   SUPERVISOR    ############ #
    re_path(r'api/v1/supervisor/campanas',
            SupervisorCampanasActivasViewSet.as_view(),
            name='api_campanas_de_supervisor'),
    re_path(r'api/v1/supervision/agentes',
            login_required(AgentesStatusAPIView.as_view()),
            name='api_agentes_activos'),
    re_path(r'api/v1/supervision/status_campanas/entrantes/$',
            login_required(StatusCampanasEntrantesView.as_view()),
            name='api_supervision_campanas_entrantes'),
    re_path(r'api/v1/supervision/status_campanas/salientes/$',
            login_required(StatusCampanasSalientesView.as_view()),
            name='api_supervision_campanas_salientes'),
    re_path(r'api/v1/supervision/accion_sobre_agente/(?P<pk>\d+)/$',
            login_required(InteraccionDeSupervisorSobreAgenteView.as_view()),
            name='api_accion_sobre_agente'),
    re_path(r'^api_supervision/llamadas_campana/(?P<pk_campana>\d+)/$',
            LlamadasDeCampanaView.as_view(),
            name='api_supervision_llamadas_campana',
            ),
    re_path(r'^api_supervision/calificaciones_campana/(?P<pk_campana>\d+)/$',
            CalificacionesDeCampanaView.as_view(),
            name='api_supervision_calificaciones_campana',
            ),
    re_path(r'api/v1/supervision/reasignar_agenda_contacto/$',
            ReasignarAgendaContactoView.as_view(),
            name='api_reasignar_agenda_contacto'),
    re_path(r'api/v1/supervision/data_agenda_contacto/(?P<agenda_id>\d+)/$',
            DataAgendaContactoView.as_view(),
            name='api_data_agenda_contacto'),
    re_path(r'api/v1/exportar_csv_contactados/$',
            ExportarCSVContactados.as_view(),
            name='api_exportar_csv_contactados'),
    re_path(r'api/v1/exportar_csv_calificados/$',
            ExportarCSVCalificados.as_view(),
            name='api_exportar_csv_calificados'),
    re_path(r'api/v1/exportar_csv_no_atendidos/$',
            ExportarCSVNoAtendidos.as_view(),
            name='api_exportar_csv_no_atendidos'),
    re_path(r'api/v1/supervision/contactos_asignados_preview/(?P<pk_campana>\d+)/$',
            ContactosAsignadosCampanaPreviewView.as_view(),
            name='api_contactos_asignados_campana_preview'),
    re_path(r'api/v1/exportar_csv_calificaciones_campana/$',
            ExportarCSVCalificacionesCampana.as_view(),
            name='api_exportar_csv_calificaciones_campana'),
    re_path(r'api/v1/exportar_csv_formulario_gestion_campana/$',
            ExportarCSVFormularioGestionCampana.as_view(),
            name='api_exportar_csv_formulario_gestion_campana'),
    re_path(r'api/v1/exportar_csv_resultados_base_contactados/$',
            ExportarCSVResultadosBaseContactados.as_view(),
            name='api_exportar_csv_resultados_base_contactados'),
    re_path(r'api/v1/dashboard_supervision/$',
            DashboardSupervision.as_view(),
            name='api_dashboard_supervision'),
    re_path(r'api/v1/campaign/(?P<pk_campana>\d+)/agents/$',
            AgentesCampana.as_view(),
            name='api_agents_campaign'),
    re_path(r'api/v1/campaign/agents_update/$',
            ActualizaAgentesCampana.as_view(),
            name='api_update_agents_campaign'),
    re_path(r'api/v1/active_agents/$',
            AgentesActivos.as_view(),
            name='api_active_agents'),
    # =========================
    # Conjuntos de Pausas
    # =========================
    re_path(r'api/v1/pause_sets/pause_options/$',
            Pausas.as_view(),
            name='api_pause_set_pause_options'),
    re_path(r'api/v1/pause_sets/$',
            ConjuntoDePausaList.as_view(),
            name='api_pause_set_list'),
    re_path(r'api/v1/pause_sets/(?P<pk>\d+)/$',
            ConjuntoDePausaDetalle.as_view(),
            name='api_pause_set_detail'),
    re_path(r'api/v1/pause_sets/create/$',
            ConjuntoDePausaCreate.as_view(),
            name='api_pause_set_create'),
    re_path(r'api/v1/pause_sets/(?P<pk>\d+)/update/$',
            ConjuntoDePausaUpdate.as_view(),
            name='api_pause_set_update'),
    re_path(r'api/v1/pause_sets/(?P<pk>\d+)/delete/$',
            ConjuntoDePausaDelete.as_view(),
            name='api_pause_set_delete'),
    re_path(r'api/v1/pause_config/create/$',
            ConfiguracionDePausaCreate.as_view(),
            name='api_pause_config_create'),
    re_path(r'api/v1/pause_config/(?P<pk>\d+)/update/$',
            ConfiguracionDePausaUpdate.as_view(),
            name='api_pause_config_update'),
    re_path(r'api/v1/pause_config/(?P<pk>\d+)/delete/$',
            ConfiguracionDePausaDelete.as_view(),
            name='api_pause_config_delete'),
    # =========================
    # Sitios Externos
    # =========================
    re_path(r'api/v1/external_sites/$',
            SitioExternoList.as_view(),
            name='api_external_sites_list'),
    re_path(r'api/v1/external_sites/(?P<pk>\d+)/$',
            SitioExternoDetalle.as_view(),
            name='api_external_sites_detail'),
    re_path(r'api/v1/external_sites/create/$',
            SitioExternoCreate.as_view(),
            name='api_external_sites_create'),
    re_path(r'api/v1/external_sites/(?P<pk>\d+)/update/$',
            SitioExternoUpdate.as_view(),
            name='api_external_sites_update'),
    re_path(r'api/v1/external_sites/(?P<pk>\d+)/delete/$',
            SitioExternoDelete.as_view(),
            name='api_external_sites_delete'),
    re_path(r'api/v1/external_sites/(?P<pk>\d+)/hide/$',
            SitioExternoOcultar.as_view(),
            name='api_external_sites_hide'),
    re_path(r'api/v1/external_sites/(?P<pk>\d+)/show/$',
            SitioExternoDesocultar.as_view(),
            name='api_external_sites_show'),
    # ===================================
    # Autenticacion de Sitios Externos
    # ===================================
    re_path(r'api/v1/external_site_authentications/$',
            ExternalSiteAuthenticationList.as_view(),
            name='api_external_site_authentications_list'),
    re_path(r'api/v1/external_site_authentications/(?P<pk>\d+)/$',
            ExternalSiteAuthenticationDetail.as_view(),
            name='api_external_site_authentications_detail'),
    re_path(r'api/v1/external_site_authentications/create/$',
            ExternalSiteAuthenticationCreate.as_view(),
            name='api_external_site_authentications_create'),
    re_path(r'api/v1/external_site_authentications/(?P<pk>\d+)/update/$',
            ExternalSiteAuthenticationUpdate.as_view(),
            name='api_external_site_authentications_update'),
    re_path(r'api/v1/external_site_authentications/(?P<pk>\d+)/delete/$',
            ExternalSiteAuthenticationDelete.as_view(),
            name='api_external_site_authentications_delete'),
    # =========================
    # Calificaciones
    # =========================
    re_path(r'api/v1/call_dispositions/$',
            CalificacionList.as_view(),
            name='api_call_dispositions_list'),
    re_path(r'api/v1/call_dispositions/create/$',
            CalificacionCreate.as_view(),
            name='api_call_dispositions_create'),
    re_path(r'api/v1/call_dispositions/(?P<pk>\d+)/update/$',
            CalificacionUpdate.as_view(),
            name='api_call_dispositions_update'),
    re_path(r'api/v1/call_dispositions/(?P<pk>\d+)/$',
            CalificacionDetail.as_view(),
            name='api_call_dispositions_detail'),
    re_path(r'api/v1/call_dispositions/(?P<pk>\d+)/delete/$',
            CalificacionDelete.as_view(),
            name='api_call_dispositions_delete'),
    # =========================
    # Sistemas Externos
    # =========================
    re_path(r'api/v1/external_systems/$',
            SistemaExternoList.as_view(),
            name='api_external_systems_list'),
    re_path(r'api/v1/external_systems/create/$',
            SistemaExternoCreate.as_view(),
            name='api_external_systems_create'),
    re_path(r'api/v1/external_systems/(?P<pk>\d+)/update/$',
            SistemaExternoUpdate.as_view(),
            name='api_external_systems_update'),
    re_path(r'api/v1/external_systems/(?P<pk>\d+)/$',
            SistemaExternoDetail.as_view(),
            name='api_external_systems_detail'),
    re_path(r'api/v1/agents_external_system/$',
            AgentesSistemaExternoList.as_view(),
            name='api_agents_external_system_list'),
    # =========================
    # Formularios
    # =========================
    re_path(r'api/v1/forms/$',
            FormList.as_view(),
            name='api_forms_list'),
    re_path(r'api/v1/forms/create/$',
            FormCreate.as_view(),
            name='api_forms_create'),
    re_path(r'api/v1/forms/(?P<pk>\d+)/update/$',
            FormUpdate.as_view(),
            name='api_forms_update'),
    re_path(r'api/v1/forms/(?P<pk>\d+)/hide/$',
            FormHide.as_view(),
            name='api_forms_hide'),
    re_path(r'api/v1/forms/(?P<pk>\d+)/show/$',
            FormShow.as_view(),
            name='api_forms_show'),
    re_path(r'api/v1/forms/(?P<pk>\d+)/$',
            FormDetail.as_view(),
            name='api_forms_detail'),
    re_path(r'api/v1/forms/(?P<pk>\d+)/delete/$',
            FormDelete.as_view(),
            name='api_forms_delete'),
    # =========================
    # Pausas
    # =========================
    re_path(r'api/v1/pauses/$',
            PauseList.as_view(),
            name='api_pauses_list'),
    re_path(r'api/v1/pauses/create/$',
            PauseCreate.as_view(),
            name='api_pauses_create'),
    re_path(r'api/v1/pauses/(?P<pk>\d+)/update/$',
            PauseUpdate.as_view(),
            name='api_pauses_update'),
    re_path(r'api/v1/pauses/(?P<pk>\d+)/$',
            PauseDetail.as_view(),
            name='api_pauses_detail'),
    re_path(r'api/v1/pauses/(?P<pk>\d+)/reactivate/$',
            PauseReactivate.as_view(),
            name='api_pauses_reactivate'),
    re_path(r'api/v1/pauses/(?P<pk>\d+)/delete/$',
            PauseDelete.as_view(),
            name='api_pauses_delete'),
    # =========================
    # Rutas Entrantes
    # =========================
    re_path(r'api/v1/inbound_routes/$',
            InboundRouteList.as_view(),
            name='api_inbound_routes_list'),
    re_path(r'api/v1/inbound_routes/create/$',
            InboundRouteCreate.as_view(),
            name='api_inbound_routes_create'),
    re_path(r'api/v1/inbound_routes/(?P<pk>\d+)/update/$',
            InboundRouteUpdate.as_view(),
            name='api_inbound_routes_update'),
    re_path(r'api/v1/inbound_routes/(?P<pk>\d+)/$',
            InboundRouteDetail.as_view(),
            name='api_inbound_routes_detail'),
    re_path(r'api/v1/inbound_routes/(?P<pk>\d+)/delete/$',
            InboundRouteDelete.as_view(),
            name='api_inbound_routes_delete'),
    re_path(r'api/v1/inbound_routes/destinations_by_type/$',
            InboundRouteDestinations.as_view(),
            name='api_inbound_routes_destinations_by_type'),
    # =========================
    # Rutas Salientes
    # =========================
    re_path(r'api/v1/outbound_routes/$',
            OutboundRouteList.as_view(),
            name='api_outbound_routes_list'),
    re_path(r'api/v1/outbound_routes/create/$',
            OutboundRouteCreate.as_view(),
            name='api_outbound_routes_create'),
    re_path(r'api/v1/outbound_routes/(?P<pk>\d+)/update/$',
            OutboundRouteUpdate.as_view(),
            name='api_outbound_routes_update'),
    re_path(r'api/v1/outbound_routes/(?P<pk>\d+)/$',
            OutboundRouteDetail.as_view(),
            name='api_outbound_routes_detail'),
    re_path(r'api/v1/outbound_routes/(?P<pk>\d+)/delete/$',
            OutboundRouteDelete.as_view(),
            name='api_outbound_routes_delete'),
    re_path(r'api/v1/outbound_routes/sip_trunks/$',
            OutboundRouteSIPTrunksList.as_view(),
            name='api_outbound_routes_sip_trunks'),
    re_path(r'api/v1/outbound_routes/(?P<pk>\d+)/orphan_trunks$',
            OutboundRouteOrphanTrunks.as_view(),
            name='api_outbound_routes_orphan_trunks'),
    re_path(r'api/v1/outbound_routes/reorder/$',
            OutboundRouteReorder.as_view(),
            name='api_outbound_routes_reorder'),
    # =========================
    # Grupos Horarios
    # =========================
    re_path(r'api/v1/group_of_hours/$',
            GroupOfHourList.as_view(),
            name='api_group_of_hours_list'),
    re_path(r'api/v1/group_of_hours/create/$',
            GroupOfHourCreate.as_view(),
            name='api_group_of_hours_create'),
    re_path(r'api/v1/group_of_hours/(?P<pk>\d+)/update/$',
            GroupOfHourUpdate.as_view(),
            name='api_group_of_hours_update'),
    re_path(r'api/v1/group_of_hours/(?P<pk>\d+)/$',
            GroupOfHourDetail.as_view(),
            name='api_group_of_hours_detail'),
    re_path(r'api/v1/group_of_hours/(?P<pk>\d+)/delete/$',
            GroupOfHourDelete.as_view(),
            name='api_group_of_hours_delete'),
    # =========================
    # IVRs
    # =========================
    path('api/v1/ivrs/',
         IVRList.as_view(),
         name='api_ivrs_list'),
    path('api/v1/ivrs/create/',
         IVRCreate.as_view(),
         name='api_ivrs_create'),
    path('api/v1/ivrs/<int:pk>/update/',
         IVRUpdate.as_view(),
         name='api_ivrs_update'),
    path('api/v1/ivrs/<int:pk>/',
         IVRDetail.as_view(),
         name='api_ivrs_detail'),
    path('api/v1/ivrs/<int:pk>/delete/',
         IVRDelete.as_view(),
         name='api_ivrs_delete'),
    path('api/v1/ivrs/audio_options/',
         IVRAudioOptions.as_view(),
         name='api_ivrs_audio_options_list'),
    path('api/v1/ivrs/destination_types/',
         IVRDestinationTypes.as_view(),
         name='api_ivrs_destination_types_list'),
    # =========================
    # Register Server
    # =========================
    path('api/v1/register_server/',
         RegisterServerList.as_view(),
         name='api_register_server_detail'),
    path('api/v1/register_server/create/',
         RegisterServerCreate.as_view(),
         name='api_register_server_create'),
    # =========================
    # Base de contactos
    # =========================
    path('api/v1/contact_database/create/',
         BaseDatosContactoCreateView.as_view(), name='api_database_create_view'),
    path('api/v1/contact_database/<int:db_pk>/contact/',
         ContactoCreateView.as_view(), name='api_database_create_contact_view'),
    path('api/v1/contact_database/<int:pk>/campaings/',
         CampaingsOnDB.as_view(),
         name='api_contact_database_campaings'),
    path('api/v1/new_contact/', ContactoDeCampanaCreateView.as_view(),
         name='api_new_contact'),
    path('api/v1/campaign/database_metadata/', CampaignDatabaseMetadataView.as_view(),
         name='api_campaign_database_metadata'),
    path('api/v1/campaign/database_metadata_columns_fields/<int:pk>/',
         CamposDireccionView.as_view(), name='api_database_metadata_columns_fields'),
    # ###########     AGENTE      ############ #
    path('api/v1/campaign/<int:pk_campana>/contacts/',
         API_ObtenerContactosCampanaView.as_view(), name='api_contactos_campana'),
    path('api/v1/makeCall/',
         Click2CallView.as_view(),
         name='api_click2call'),
    path('api/v1/make_call_outside_campaign/',
         Click2CallOutsideCampaign.as_view(),
         name='api_click2call_outside_campaign'),
    path('api/v1/hangupCall/',
         HangUpCallView.as_view(),
         name='api_hangup_call'),
    path('api/v1/asterisk_login/',
         AgentLoginAsterisk.as_view(), name='api_agent_asterisk_login'),
    path('api/v1/asterisk_logout/',
         AgentLogoutAsterisk.as_view(), name='api_agent_asterisk_logout'),
    path('agente/logout/', login_required(AgentLogoutView.as_view()),
         name='api_agente_logout'),
    path('api/v1/asterisk_pause/',
         AgentPauseAsterisk.as_view(), name='api_make_pause'),
    path('api/v1/asterisk_unpause/',
         AgentUnpauseAsterisk.as_view(), name='api_make_unpause'),
    path('api/v1/asterisk_ringing/',
         AgentRingingAsterisk.as_view(), name='api_make_ringing'),
    path('api/v1/asterisk_reject_call/',
         AgentRejectCallAsterisk.as_view(), name='api_make_reject_call'),
    path('api/v1/asterisk_disabled/',
         AgentDisabledAsterisk.as_view(), name='api_make_disabled'),
    path('api/v1/sip/credentials/agent/', ObtenerCredencialesSIPAgenteView.as_view(),
         name='api_credenciales_sip_agente'),
    path('api/v1/audit/set_revision_status/', SetEstadoRevisionAuditoria.as_view(),
         name='api_set_estado_revision'),
    path('api/v1/calificar_llamada/', ApiStatusCalificacionLlamada.as_view(),
         name='api_status_calificacion_llamada'),
    path('api/v1/evento_hold/', ApiEventoHold.as_view(),
         name='api_evento_hold'),
    path('api/v1/agent/transfer_options', ApiAgentesParaTransferencia.as_view({'get': 'list'}),
         name='api_agent_call_transfer_options'),
    # ###########     AUDITORIAS       ############ #
    path('api/v1/auditoria/archivo',
         ObtenerArchivoAuditoriaView.as_view(), name='api_auditoria_archivo'),
    # ###########     GRABACIONES      ############ #
    re_path(r'^api/v1/grabacion/archivo/$',
            ObtenerArchivoGrabacionView.as_view(), name='api_grabacion_archivo'),
    re_path(r'^api/v1/grabacion/descarga_masiva',
            ObtenerArchivosGrabacionView.as_view(), name='api_grabacion_descarga_masiva'),
    path('api/v1/call_record/<str:callid>/',
         ObtenerUrlGrabacionView.as_view(), name='api_call_record_url'),
    # ###########  AUDIOS ASTERISK    ############ #
    path('api/v1/audio/list/',
         ListadoAudiosView.as_view({'get': 'list'}), name='api_audios_listado'),
    # ###########  USUARIOS    ############ #
    path('api/v1/group/list/',
         ListadoGrupos.as_view({'get': 'list'}), name='api_grupos'),
    path('api/v1/agent/list/',
         ListadoAgentes.as_view({'get': 'list'}), name='api_agentes'),
    path('api/v1/audit_supervisor/',
         AuditSupervisor.as_view(), name='api_audit_supervisor'),
    # ###########  WOMBAT DIALER    ############ #
    path('api/v1/wombat_dialer/restart/',
         ReiniciarWombat.as_view(), name='api_restart_wombat'),
    path('api/v1/wombat_dialer/status/',
         WombatState.as_view(), name='api_wombat_state'),

    # ###########  ASTERISK    ############ #
    path('api/v1/asterisk/queues_data/',
         AsteriskQueuesData.as_view(), name='api_asterisk_queues_data'),

    # ###########  Inbound Destinations    ############ #
    re_path(r'^api/v1/inbound_destinations/(?P<type>\d+)/list/',
            DestinoEntranteView.as_view(), name='api_inbound_destinations'),
    path('api/v1/inbound_destinations_types/list/',
         DestinoEntranteTiposView.as_view(), name='api_inbound_destinations_types'),

    # ###########  Inbound Destinations    ############ #
    path('api/v1/reportes/survey_transfer/',
         TransferenciaAEncuestaLogCreateView.as_view(), name='api_log_survey_transfer'),

    # ######  For Bots Internos    ############ #
    path('api/v1/agent_status/campaign/<int:campaign_id>',
         AgentStatusView.as_view(), name='api_agent_status'),
    path('api/v1/agent_status_list/campaign/<int:campaign_id>',
         AgentStatusListView.as_view(), name='api_agent_status_list'),
    path('api/v1/call_status/campaign/<int:campaign_id>',
         CallStatusView.as_view(), name='api_call_status'),
]
