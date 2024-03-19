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
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data

from ominicontacto_app.models import Campana


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='nombre')
    type = serializers.IntegerField()
    line_id = serializers.SerializerMethodField()

    def get_line_id(self, obj):
        configuracionwhatsapp = obj.configuracionwhatsapp.last()
        if configuracionwhatsapp and configuracionwhatsapp.linea:
            return configuracionwhatsapp.linea.id
        return ""


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            estados = [Campana.ESTADO_ACTIVA]
            if request.user.get_is_administrador():
                queryset = Campana.objects.filter(estado__in=estados, whatsapp_habilitado=True)
            elif request.user.get_is_agente():
                campana_members = request.user.get_agente_profile().campana_member.all()
                queue_names = campana_members.values_list('id_campana', flat=True)
                campaigns_pks = [Campana.get_id_from_queue_id_name(name) for name in queue_names]
                queryset = Campana.objects.filter(
                    pk__in=campaigns_pks, estado__in=estados, whatsapp_habilitado=True)
            else:
                queryset = request.user.get_supervisor_profile()\
                    .campanas_asignadas_actuales().filter(
                        estado__in=estados, whatsapp_habilitado=True)
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las campanas de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener campanas')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
