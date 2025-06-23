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

import logging as _logging
from django.utils.translation import gettext as _
from api_app.serializers.base import CampanaSerializer, GrupoSerializer
from api_app.serializers.campaigns.add_agents_to_campaign import (
    AgenteActivoSerializer, AgenteDeCampanaSerializer)
from ominicontacto_app.models import AgenteProfile, Campana, Grupo, QueueMember
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from ominicontacto_app.services.queue_member_service import QueueMemberService
from api_app.views.permissions import TienePermisoOML

logger = _logging.getLogger(__name__)


class AgentesCampana(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk_campana):
        data = {
            'status': 'SUCCESS',
            'message': _(u'Se obtuvieron los agentes de forma exitosa'),
            'agentsCampaign': [],
            'campaign': {}}
        try:
            campana = Campana.objects.get(pk=pk_campana)
            queue_members = campana.queue_campana.queuemember.all()
            data['agentsCampaign'] = [
                AgenteDeCampanaSerializer(qm).data for qm in queue_members]
            data['campaign'] = CampanaSerializer(campana).data
            return Response(data=data, status=status.HTTP_200_OK)
        except Campana.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la campaña')
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)


class ActualizaAgentesCampana(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def _is_valid_campaign(self, campana):
        return campana.estado in [
            Campana.ESTADO_ACTIVA,
            Campana.ESTADO_INACTIVA,
            Campana.ESTADO_PAUSADA
        ]

    def _get_current_agent_ids(self, campaign):
        qms = QueueMember.objects.filter(
            queue_name=campaign.queue_campana).values_list('member')
        return [q[0] for q in qms]

    def _get_new_agent_ids(self, agents):
        return [int(a['agent_id']) for a in agents]

    def _get_agents_penalties(self, agents):
        penalties = {}
        for agent in agents:
            penalties[agent['agent_id']] = int(agent["agent_penalty"])
        return penalties

    def post(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _(u'Se agregaron los agentes de forma exitosa a la campaña')}
        campaign_id = request.data.get('campaign_id')
        agents = request.data.get('agents')
        try:
            campaign = Campana.objects.get(pk=campaign_id)
        except Campana.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la campaña, no se pueden agregar agentes')
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        try:
            # De los agentes actuales en campaña, eliminamos los que
            # ya no estan en los agentes nuevos (por agregar)
            current_agent_ids = self._get_current_agent_ids(campaign)
            new_agent_ids = self._get_new_agent_ids(agents)
            agent_ids_to_delete = set(current_agent_ids) - set(new_agent_ids)

            # Validacion de agentes
            agentes_a_eliminar = AgenteProfile.objects.filter(id__in=agent_ids_to_delete)
            if agentes_a_eliminar.count() < len(agent_ids_to_delete):
                logger.error('Falta AgenteProfile para QueueMember. Campana: ' + campaign_id)
                data['status'] = 'ERROR'
                data['message'] = _(u'No existe el agente, '
                                    'no se puede eliminar de la member queue')
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            agentes_a_agregar = AgenteProfile.objects.filter(id__in=new_agent_ids)
            if agentes_a_agregar.count() < len(new_agent_ids):
                data['status'] = 'ERROR'
                data['message'] = _(u'No existe el agente, '
                                    'no se puede crear la member queue')
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)

            # Se Delega la responsabilidad de crear/eliminar y actualizar asterisk/redis
            queue_service = QueueMemberService()
            queue_service.eliminar_agentes_de_cola(campaign, agentes_a_eliminar)
            penalties = self._get_agents_penalties(agents)
            queue_service.agregar_agentes_en_cola(campaign, agentes_a_agregar, penalties)
            queue_service.disconnect()
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'No se pudo confirmar la creación del dialplan')
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActualizarCampanasDeAgente(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        self.supervisor = request.user.get_supervisor_profile()
        error, agente, campanas, campanas_supervisor = self.validar_parametros(request)
        if error is not None:
            return self._get_error_response(error)
        error = self.actualizar_asignacion_de_campanas(agente, campanas, campanas_supervisor)
        if error is not None:
            return self._get_error_response(error)

        data = {
            'status': 'SUCCESS',
            'message': _(u'Asignación de agente a campañas actualizada')}
        return Response(data=data, status=status.HTTP_200_OK)

    def validar_parametros(self, request):
        agent_id = request.data.get('agent_id', None)
        if agent_id is None:
            return _('Parámetro "agent_id" requerido'), None, None, None
        try:
            agente = AgenteProfile.objects.get(id=agent_id)
        except (AgenteProfile.DoesNotExist, ValueError):
            return _('agente_id incorrecto'), None, None, None
        # TODO: Verificar que el supervisor tiene permiso sobre el agente

        campanas_ids = request.data.get('campaigns', None)
        if not isinstance(campanas_ids, list):
            return _('Parámetro "campaigns" de tipo "list" requerido'), None, None, None
        campanas_ids = set(campanas_ids)

        if self.supervisor.is_administrador:
            campanas_supervisor = Campana.objects.obtener_actuales()
        else:
            campanas_supervisor = self.supervisor.campanas_asignadas_actuales()
        campanas = campanas_supervisor.filter(id__in=campanas_ids)
        # Verificar que las campañas existen o que el supervisor tiene permiso sobre ellas
        if len(campanas_ids) > campanas.count():
            ids_incorrectas = campanas_ids - set(campanas.values_list('id', flat=True))
            return _('IDs de campañas inválidas: {0}').format(ids_incorrectas), None, None, None

        campanas_supervisor = set(campanas_supervisor.values_list('id', flat=True))
        return None, agente, campanas_ids, campanas_supervisor

    def actualizar_asignacion_de_campanas(self, agente, campanas, campanas_supervisor):
        # Obtener campanas previamente asignadas
        previas = set(agente.campana_member.values_list('queue_name__campana__id', flat=True))
        previas = previas.intersection(campanas_supervisor)
        # Calcular campañas no asignadas todavia y asignar
        nuevas = campanas - previas
        # Calcular campañas a desasignar y desasignar
        eliminar = previas - campanas

        try:
            queue_service = QueueMemberService()
            if eliminar:
                campanas_a_eliminar = Campana.objects.filter(id__in=eliminar)
                queue_service.eliminar_agente_de_colas(agente, campanas_a_eliminar, eliminar)
            if nuevas:
                campanas_a_agregar = Campana.objects.filter(id__in=nuevas)
                queue_service.agregar_agente_a_campanas(agente, campanas_a_agregar,
                                                        verificar_sesion_activa=True)
        except Exception:
            logger.error('Error updating agent campaigns:', exc_info=True)
            return _(u'Error asignando campañas. No se pudo confirmar la creación del dialplan')

    def _get_error_response(self, message):
        data = {'status': 'ERROR', 'message': message}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class AgentesActivos(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _(u'Se obtuvieron los agentes de forma exitosa'),
            'activeAgents': [],
            'groups': []}
        try:
            agentes = AgenteProfile.objects.obtener_activos().prefetch_related('user')
            data['activeAgents'] = [AgenteActivoSerializer(a).data for a in agentes]

            grupos = Grupo.objects.all()
            for grupo in grupos:
                agents_by_group = AgenteProfile.objects.obtener_activos()\
                    .prefetch_related('user').filter(grupo=grupo)
                data['groups'].append({
                    "group": GrupoSerializer(grupo).data,
                    "agents": [AgenteActivoSerializer(a).data for a in agents_by_group]
                })

            return Response(data=data, status=status.HTTP_200_OK)
        except Campana.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los agentes activos')
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
