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

import redis
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from ominicontacto_app.services.redis.connection import create_redis_connection
from ominicontacto_app.services.asterisk.redis_database import CampaignAgentsFamily, AgenteFamily
from ominicontacto_app.models import Campana
from ominicontacto_app.utiles import datetime_hora_minima_dia, datetime_hora_maxima_dia
from reportes_app.models import LlamadaLog


class AgentStatusView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campana, pk=campaign_id)
        campaign_agents = campaign.obtener_agentes().values_list('id', flat=True)
        data = dict.fromkeys(['ready', 'oncall', 'pause'], 0)
        redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME, port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        keys_agentes = redis_connection.keys('OML:AGENT:*')
        for key in keys_agentes:
            if int(key.split('OML:AGENT:')[1]) in campaign_agents:
                agente_info = redis_connection.hgetall(key)
                if agente_info['STATUS'] == 'READY':
                    data['ready'] += 1
                elif agente_info['STATUS'] == 'ONCALL':
                    data['oncall'] += 1
                elif agente_info['STATUS'].startswith('PAUSE'):
                    data['pause'] += 1
        return Response(data)


class AgentStatusListView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, campaign_id):
        # Verifico que exista en la base de datos.
        get_object_or_404(Campana, pk=campaign_id)
        redis_connection = create_redis_connection()
        key = CampaignAgentsFamily.KEY_PREFIX.format(campaign_id)
        agents_ids = redis_connection.smembers(key)
        data = []
        for agent_id in agents_ids:
            key_agent = AgenteFamily.KEY_PREFIX.format(agent_id)
            agent_data = redis_connection.hmget(key_agent, 'NAME', 'STATUS')
            name = agent_data[0]
            if name:
                data.append({'name': name,
                             'status': self._parse_status(agent_data[1])})
        return Response(data)

    def _parse_status(self, status):
        print(status)
        if status.startswith('PAUSE'):
            return 'PAUSE'
        if status == '' or status is None:
            return 'OFFLINE'
        return status


class CallStatusView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, campaign_id):
        start = request.GET.get('date_start', None)
        end = request.GET.get('date_end', None)
        call_logs = LlamadaLog.objects.filter(campana_id=campaign_id)
        if start and end:
            format_date = "%Y-%m-%d"
            start = datetime_hora_minima_dia(datetime.strptime(start, format_date))
            end = datetime_hora_maxima_dia(datetime.strptime(end, format_date))
            call_logs = call_logs.filter(time__range=(start, end))

        data = dict.fromkeys(['attended', 'abandoned', 'expired'], 0)
        attended = call_logs.filter(event__in=LlamadaLog.EVENTOS_INICIO_CONEXION_AGENTE).count()
        abandoned = call_logs.filter(event__in=LlamadaLog.EVENTOS_NO_DIALOGO).count()
        expired = call_logs.filter(event__in=LlamadaLog.EVENTOS_NO_CONTACTACION).count()
        data = {
            'attended': attended,
            'abandoned': abandoned,
            'expired': expired
        }
        return Response(data)
