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
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api_app.views.permissions import EsSupervisorPermiso
from api_app.serializers import (CampanaSerializer, )
from ominicontacto_app.models import (Campana, )
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)


class SupervisorCampanasActivasViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las campañas activas relacionadas a un supervisor
    si este no es admin y todas las campañas activas en el caso de sí lo sea
    """
    serializer_class = CampanaSerializer
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    queryset = Campana.objects.obtener_activas()
    http_method_names = ['get']

    def get_queryset(self):
        superv_profile = self.request.user.get_supervisor_profile()
        if superv_profile.is_administrador:
            return super(SupervisorCampanasActivasViewSet, self).get_queryset()
        return superv_profile.obtener_campanas_asignadas_activas()


class AgentesStatusAPIView(APIView):
    """Devuelve información de los agentes en el sistema"""
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    agentes_parseados = SupervisorActivityAmiManager()

    def get(self, request):
        online = []
        for data_agente in self.agentes_parseados._obtener_agentes_activos():
            if not data_agente.get('status', '') == 'OFFLINE':
                online.append(data_agente)
        return Response(data=online)


class StatusCampanasEntrantesView(APIView):
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(request.user)
        return Response(data={'errors': None,
                              'data': reporte.estadisticas})


class StatusCampanasSalientesView(APIView):
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        reporte = ReporteDeLLamadasSalientesDeSupervision(request.user)
        return Response(data={'errors': None,
                              'data': reporte.estadisticas})


class InteraccionDeSupervisorSobreAgenteView(APIView):
    permission_classes = (IsAuthenticated, EsSupervisorPermiso,)
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        self.supervisor = self.request.user.get_supervisor_profile()
        self.agente_id = kwargs.get('pk')
        # TODO: Verificar que el supervisor sea responsable del agente.
        return super(InteraccionDeSupervisorSobreAgenteView, self).dispatch(
            request, *args, **kwargs)

    def post(self, request, pk):
        accion = request.POST.get('accion')
        servicio_acciones = SupervisorActivityAmiManager()
        error = servicio_acciones.ejecutar_accion_sobre_agente(
            self.supervisor, self.agente_id, accion)
        if error:
            return Response(data={
                'status': 'ERROR',
                'message': error
            })
        else:
            return Response(data={
                'status': 'OK',
            })
