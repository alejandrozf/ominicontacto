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
import logging as _logging
from django.utils.translation import gettext as _
from django.db import transaction
from api_app.serializers.base import CampanaSerializer, GrupoSerializer
from api_app.serializers.campaigns.add_agents_to_campaign import (
    AgenteActivoSerializer, AgenteDeCampanaSerializer)
from ominicontacto_app.models import AgenteProfile, Campana, Grupo, QueueMember
from ominicontacto_app.services.asterisk.asterisk_ami import (
    AMIManagerConnectorError, AmiManagerClient)
from ominicontacto_app.services.creacion_queue import ActivacionQueueService
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from utiles_globales import obtener_sip_agentes_sesiones_activas

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

    def activar_cola(self):
        activacion_queue_service = ActivacionQueueService()
        activacion_queue_service.activar()

    def adicionar_agente_cola(self, agente, queue_member, campana, client):
        """Adiciona agente a la cola de su respectiva campaña"""
        queue = campana.get_queue_id_name()
        interface = "PJSIP/{0}".format(agente.sip_extension)
        penalty = queue_member.penalty
        paused = queue_member.paused
        member_name = agente.get_asterisk_caller_id()
        try:
            client.queue_add(queue, interface, penalty, paused, member_name)
        except AMIManagerConnectorError:
            logger.exception(_("QueueAdd failed - agente: {0} de la campana: {1} ".format(
                agente, campana)))

    def adicionar_agente_activo_cola(self, queue_member, campana, sip_agentes_logueados, client):
        """
        Si el agente tiene una sesión activa,
        lo adiciona a la cola de su respectiva campaña
        """
        # chequear si el agente tiene sesion activa
        agente = queue_member.member
        if agente.sip_extension in sip_agentes_logueados:
            self.adicionar_agente_cola(agente, queue_member, campana, client)

    def _is_valid_campaign(self, campana):
        return campana.estado in [
            Campana.ESTADO_ACTIVA,
            Campana.ESTADO_INACTIVA,
            Campana.ESTADO_PAUSADA
        ]

    def remover_agente_cola_asterisk(self, campana, agente, client):
        queue = campana.get_queue_id_name()
        interface = 'PJSIP/{0}'.format(agente.sip_extension)
        sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
        if agente.sip_extension in sip_agentes_logueados:
            try:
                client.queue_remove(queue, interface)
            except AMIManagerConnectorError:
                logger.exception(
                    _('QueueRemove failed - agente: {0} de la campana: {1}'.format(
                        agente, campana)))

    def _delete_queue_member(self, campaign, agent, client):
        """Elimina agente asignado en la campana"""
        try:
            QueueMember.objects.filter(
                member=agent,
                queue_name=campaign.queue_campana).delete()
        except QueueMember.DoesNotExist:
            return Response(
                data={'status': 'ERROR', 'message': _(u'No existe el agente en cola')},
                status=status.HTTP_404_NOT_FOUND)
        self.remover_agente_cola_asterisk(campaign, agent, client)

    def _get_current_agent_ids(self, campaign):
        qms = QueueMember.objects.filter(
            queue_name=campaign.queue_campana).values_list('member')
        return [q[0] for q in qms]

    def _get_new_agent_ids(self, agents):
        return [int(a['agent_id']) for a in agents]

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
            client = AmiManagerClient()
            client.connect()

            # De los agentes actuales en campaña, eliminamos los que
            # ya no estan en los agentes nuevos (por agregar)
            current_agent_ids = self._get_current_agent_ids(campaign)
            new_agent_ids = self._get_new_agent_ids(agents)
            agent_ids_to_delete = set(current_agent_ids) - set(new_agent_ids)
            for agent_id in agent_ids_to_delete:
                try:
                    agent = AgenteProfile.objects.get(pk=agent_id)
                except AgenteProfile.DoesNotExist:
                    data['status'] = 'ERROR'
                    data['message'] = _(u'No existe el agente,\
                                        no se puede eliminar de la member queue')
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                self._delete_queue_member(campaign, agent, client)
            sip_agentes_logueados = obtener_sip_agentes_sesiones_activas()
            for agent in agents:
                agent_id = int(agent["agent_id"])
                agent_penalty = int(agent["agent_penalty"])
                try:
                    agent = AgenteProfile.objects.get(pk=agent_id)
                except AgenteProfile.DoesNotExist:
                    data['status'] = 'ERROR'
                    data['message'] = _(u'No existe el agente,\
                                        no se puede crear la member queue')
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                with transaction.atomic():
                    queue_member, created = QueueMember.objects.get_or_create(
                        member=agent,
                        queue_name=campaign.queue_campana,
                        defaults=QueueMember.get_defaults(agent, campaign))
                    queue_member.penalty = agent_penalty
                    queue_member.save()
                    self.adicionar_agente_activo_cola(
                        queue_member, campaign, sip_agentes_logueados, client)
            self.activar_cola()
            client.disconnect()
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'No se pudo confirmar la creación del dialplan')
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
