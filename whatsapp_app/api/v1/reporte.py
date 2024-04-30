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
import datetime
from dataclasses import dataclass
from django.utils.translation import ugettext_lazy as _
from rest_framework import response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework import serializers
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from ominicontacto_app.models import Campana, CalificacionCliente


@dataclass
class ReportParams:
    start_date: datetime.datetime
    end_date: datetime.datetime
    campaing: int


class ReporteParamsSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    campaing = serializers.IntegerField()

    def create(self, validated_data):
        return ReportParams(**validated_data)


@dataclass
class ReporteCampanaWhatsapp:
    sent_messages: int
    received_messages: int
    interactions_started: int
    attended_chats: int
    not_attended_chats: int
    inbound_chats_attended: int
    inbound_chats_not_attended: int
    inbound_chats_expired: int
    outbound_chats_attended: int
    outbound_chats_not_attended: int
    outbound_chats_expired: int
    outbound_chats_failed: int
    dispositions: dict

    def __init__(self, params: ReportParams):
        campana = Campana.objects.get(id=params.campaing)
        chats_of_campaing = campana.conversaciones
        args = (params.start_date, params.end_date)
        self.sent_messages =\
            chats_of_campaing.numero_mensajes_enviados(*args)
        self.received_messages =\
            chats_of_campaing.numero_mensajes_recibidos(*args)
        self.interactions_started =\
            chats_of_campaing.conversaciones_salientes(*args).count()
        self.attended_chats =\
            chats_of_campaing.conversaciones_entrantes_atendidas(*args).count() +\
            chats_of_campaing.conversaciones_salientes_atendidas(*args).count()
        self.not_attended_chats =\
            chats_of_campaing.conversaciones_entrantes_no_atendidas(*args).count() +\
            chats_of_campaing.conversaciones_salientes_no_atendidas(*args).count()
        self.inbound_chats_attended =\
            chats_of_campaing.conversaciones_entrantes_atendidas(*args).count()
        self.inbound_chats_not_attended =\
            chats_of_campaing.conversaciones_entrantes_no_atendidas(*args).count()
        self.inbound_chats_expired =\
            chats_of_campaing.conversaciones_entrantes_expiradas_no_atendidas(*args).count()
        self.outbound_chats_attended =\
            chats_of_campaing.conversaciones_salientes_atendidas(*args).count()
        self.outbound_chats_not_attended =\
            chats_of_campaing.conversaciones_salientes_no_atendidas(*args).count()
        self.outbound_chats_expired =\
            chats_of_campaing.conversaciones_salientes_expiradas(*args).count()
        self.outbound_chats_failed =\
            chats_of_campaing.conversaciones_salientes_con_error(*args).count()
        self.dispositions = {
            'done': [{item['opcion_calificacion__nombre']: item['total']}
                     for item in CalificacionCliente.objects.calificaciones_whatsapp_campanas(
                         campana, *args)],
            'not_done': chats_of_campaing.conversaciones_no_calificadas(*args).count()}


class ReporteCampanaWhatsappSerializer(serializers.Serializer):
    sent_messages = serializers.IntegerField()
    received_messages = serializers.IntegerField()
    interactions_started = serializers.IntegerField()
    attended_chats = serializers.IntegerField()
    not_attended_chats = serializers.IntegerField()
    inbound_chats_attended = serializers.IntegerField()
    inbound_chats_not_attended = serializers.IntegerField()
    inbound_chats_expired = serializers.IntegerField()
    outbound_chats_attended = serializers.IntegerField()
    outbound_chats_not_attended = serializers.IntegerField()
    outbound_chats_expired = serializers.IntegerField()
    outbound_chats_failed = serializers.IntegerField()
    dispositions = serializers.JSONField()


class ReportAPIView(APIView):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def post(self, request):
        try:
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            campaing = request.data.get('campaign')
            params_serializer =\
                ReporteParamsSerializer(data={
                    'start_date': start_date,
                    'end_date': end_date,
                    'campaing': campaing
                }, context={"request": request})
            params_serializer.is_valid(raise_exception=True)
            params = params_serializer.save()
            data = ReporteCampanaWhatsapp(params)
            serializer = ReporteCampanaWhatsappSerializer(instance=data)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener el reporte')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                message=_('Reporte obtenido exitosamente'),
                data=serializer.data),
            status=status.HTTP_200_OK)
