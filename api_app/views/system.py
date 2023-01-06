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
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from ominicontacto_app.utiles import reemplazar_no_alfanumericos_por_guion
from ominicontacto_app.models import AgenteProfile, QueueMember


class AsteriskQueuesData(APIView):
    permission_classes = (AllowAny, )
    http_method_names = ['get']
    renderer_classes = (JSONRenderer, )

    def get(self, request):

        agents_data = []
        redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)
        ids = AgenteProfile.objects.all().values_list('id', flat=True)
        for agent_id in list(ids):
            agent_data = redis_connection.hmget('OML:AGENT:' + str(agent_id),
                                                ['SIP', 'NAME', 'STATUS'])
            status = agent_data[2]
            pause = '0'
            if status and not status == 'OFFLINE':
                sip_extension = agent_data[0]
                member_name = agent_data[1]
                member_name = reemplazar_no_alfanumericos_por_guion(member_name)
                member_name = "{0}_{1}".format(agent_id, member_name)
                if status.startswith('PAUSE'):
                    pause = '1'
                queues = QueueMember.objects.obtener_queue_por_agent(agent_id)
                penalties = QueueMember.objects.obtener_penalty_por_agent(agent_id)
                interface = "PJSIP/" + str(sip_extension).strip('[]')
                agents_data.append([agent_id, member_name, interface, pause, queues, penalties])
        return Response(data=agents_data)
