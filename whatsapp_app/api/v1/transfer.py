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


class ListSerializer(serializers.Serializer):
    id_conversation = serializers.IntegerField()
    id_camapana = serializers.IntegerField()
    destination = serializers.IntegerField()


class AgenteListSerializer(serializers.Serializer):
    id_agente = serializers.IntegerField()
    nombre_agente = serializers.CharField()
    status = serializers.CharField()


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = [
                {
                    "id_conversation": "1",
                    "id_camapana": "1",
                    "destination": "1"
                },
                {
                    "id_conversation": "2",
                    "id_camapana": "2",
                    "destination": "2"
                },
                {
                    "id_conversation": "3",
                    "id_camapana": "3",
                    "destination": "3"
                },
            ]
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las transferecia')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def agents(self, request):
        try:
            queryset = [
                {
                    "id_agente": "1",
                    "nombre_agente": "agente1",
                    "status": "ready"
                },
                {
                    "id_agente": "2",
                    "nombre_agente": "agente2",
                    "status": "ready"
                },
                {
                    "id_agente": "3",
                    "nombre_agente": "agente3",
                    "status": "ready"
                },
            ]
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
