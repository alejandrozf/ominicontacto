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

# APIs para visualizar destinos
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from ominicontacto_app.models import Campana


class ListSerializer(serializers.Serializer):
    conversation = serializers.IntegerField()
    campaing = serializers.IntegerField()
    destination = serializers.IntegerField()


class AgenteListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(source='user.username')
    status = serializers.CharField(source='estado')


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    @decorators.action(detail=False, methods=["get"], url_path='(?P<campana_pk>[^/.]+)/agents')
    def agents(self, request, campana_pk):
        try:
            # filtrar por permiso de whatsapp
            queryset = Campana.objects.get(id=campana_pk).obtener_agentes()
            serializer = AgenteListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener los agentes')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(
        detail=False, methods=["post"],
        url_path='(?P<chat_id>[^/.]+)/to_agent/(?P<agent_id>[^/.]+)')
    def to_agent(self, request, chat_id, agent_id):
        try:
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al tranferir conversacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
