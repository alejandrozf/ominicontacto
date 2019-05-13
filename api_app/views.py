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

from django.contrib.auth import authenticate
from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
                                   HTTP_200_OK)
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from api_app.authentication import token_expire_handler, expires_in, ExpiringTokenAuthentication
from api_app.serializers import (CampanaSerializer, AgenteProfileSerializer, UserSigninSerializer,
                                 UserSerializer, OpcionCalificacionSerializer)
from api_app.utiles import EstadoAgentesService
from api_app.forms import Click2CallOMLParametersForm, Click2CallExternalSiteParametersForm

from ominicontacto_app.models import Campana, AgenteProfile, Contacto, SistemaExterno
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)
from ominicontacto_app.services.asterisk.interaccion_supervisor_agente import (
    AccionesDeSupervisorSobreAgente
)
from ominicontacto_app.services.click2call import Click2CallOriginator

logger = _logging.getLogger(__name__)


class EsSupervisorPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores"""

    def has_permission(self, request, view):
        super(EsSupervisorPermiso, self).has_permission(request, view)
        superv_profile = request.user.get_supervisor_profile()
        return superv_profile is not None


class EsAdminPermiso(BasePermission):
    """Permiso para aplicar a vistas solo para administradores"""

    def has_permission(self, request, view):
        super(EsAdminPermiso, self).has_permission(request, view)
        return request.user.get_is_administrador()


class EsAgentePermiso(BasePermission):
    """Permiso para aplicar a vistas solo para agentes"""

    def has_permission(self, request, view):
        super(EsAgentePermiso, self).has_permission(request, view)
        return request.user.get_is_agente()


@api_view(["POST"])
@permission_classes((AllowAny,))  # here we specify permission by default we set IsAuthenticated
def login(request):
    signin_serializer = UserSigninSerializer(data=request.data)
    if not signin_serializer.is_valid():
        return Response(signin_serializer.errors, status=HTTP_400_BAD_REQUEST)
    user = authenticate(
        username=signin_serializer.data['username'],
        password=signin_serializer.data['password'])
    if not user:
        return Response(
            {'detail': 'Invalid Credentials or activate account'}, status=HTTP_404_NOT_FOUND)

    # TOKEN STUFF
    token, __ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)
    user_serialized = UserSerializer(user)

    return Response({
        'user': user_serialized.data,
        'expires_in': expires_in(token),
        'token': token.key
    }, status=HTTP_200_OK)


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
        return superv_profile.obtener_campanas_activas_asignadas()


class AgentesActivosGrupoViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las agentes activos de un grupo
    """
    serializer_class = AgenteProfileSerializer
    permission_classes = (IsAuthenticated, EsAdminPermiso,)
    http_method_names = ['get']

    def get_queryset(self):
        queryset = AgenteProfile.objects.obtener_activos()
        grupo_pk = self.kwargs.get('pk_grupo')
        queryset = queryset.filter(grupo__pk=grupo_pk)
        return queryset


class OpcionesCalificacionViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las opciones de calificación de una campaña
    """
    serializer_class = OpcionCalificacionSerializer
    permission_classes = (IsAuthenticated, EsAgentePermiso)
    http_method_names = ['get']

    def _validar_parametros(self, pk_campana, pk_sistema_externo):
        # Validamos que los ids de campaña y sistema externo tengan consistencia
        # esto es, si se pasa el parámetro 'pk_sistema_externo' entonces el
        # parámetro 'pk_campana' podría ser cualquier cadena pero 'pk_sistema_externo'
        # debe ser entero. En caso de que no se pase parámetro de sistema externo
        # entonces 'pk_campana' debe ser un entero que corresponde a un id de campaña
        # de OML
        if pk_sistema_externo is not None:
            try:
                int(pk_sistema_externo)
            except ValueError:
                raise Http404
        else:
            try:
                int(pk_campana)
            except ValueError:
                raise Http404

    def get_queryset(self):
        pk_campana = self.kwargs.get('campaign')
        pk_sistema_externo = self.kwargs.get('externalSystem')
        self._validar_parametros(pk_campana, pk_sistema_externo)
        if pk_sistema_externo:
            sistema_externo = get_object_or_404(SistemaExterno, pk=pk_sistema_externo)
            campana = sistema_externo.campanas.filter(id_externo=pk_campana).first()
        else:
            campana = get_object_or_404(Campana, pk=pk_campana)
        if campana is not None:
            queryset = campana.opciones_calificacion.all()
            return queryset
        else:
            raise Http404


class StatusCampanasEntrantesView(View):
    def get(self, request):
        reporte = ReporteDeLLamadasEntrantesDeSupervision(request.user)
        return JsonResponse({'errors': None,
                             'data': reporte.estadisticas})


class StatusCampanasSalientesView(View):
    def get(self, request):
        reporte = ReporteDeLLamadasSalientesDeSupervision(request.user)
        return JsonResponse({'errors': None,
                             'data': reporte.estadisticas})


class AgentesStatusAPIView(View):
    """Devuelve información de los agentes en el sistema"""

    def get(self, request):
        agentes_activos_service = EstadoAgentesService()
        data = list(agentes_activos_service._obtener_agentes_activos_ami())
        return JsonResponse(data=data, safe=False)


class InteraccionDeSupervisorSobreAgenteView(View):

    def dispatch(self, request, *args, **kwargs):
        self.supervisor = self.request.user.get_supervisor_profile()
        self.agente_id = kwargs.get('pk')
        # TODO: Verificar que el supervisor sea responsable del agente.
        return super(InteraccionDeSupervisorSobreAgenteView, self).dispatch(
            request, *args, **kwargs)

    def post(self, request, pk):
        accion = request.POST.get('accion')
        servicio_acciones = AccionesDeSupervisorSobreAgente()
        error = servicio_acciones.ejecutar_accion(self.supervisor, self.agente_id, accion)
        if error:
            return JsonResponse(data={
                'status': 'ERROR',
                'message': error
            })
        else:
            return JsonResponse(data={
                'status': 'OK',
            })


class API_ObtenerContactosCampanaView(APIView):

    permission_classes = (IsAuthenticated, EsAgentePermiso)
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication)

    def _procesar_api(self, request, campana):
        search = request.GET['search[value]']
        contactos_calificados_ids = list(campana.obtener_calificaciones().values_list(
            'contacto__pk', flat=True))
        if search != '':
            contactos = Contacto.objects.contactos_by_filtro_bd_contacto(
                campana.bd_contacto, filtro=search)
            contactos = contactos.exclude(pk__in=contactos_calificados_ids)
        else:
            contactos = campana.bd_contacto.contactos.exclude(pk__in=contactos_calificados_ids)

        return contactos

    def _procesar_contactos_salida(self, request, campana, contactos_filtrados):
        total_contactos = campana.bd_contacto.contactos.count()
        total_contactos_filtrados = contactos_filtrados.count()
        start = int(request.GET['start'])
        length = int(request.GET['length'])
        draw = int(request.GET['draw'])
        data = [[pk, telefono, ''] for pk, telefono
                in contactos_filtrados.values_list('pk', 'telefono')]
        result_dict = {
            'draw': draw,
            'recordsTotal': total_contactos,
            'recordsFiltered': total_contactos_filtrados,
            'data': data[start:start + length],
        }
        return result_dict

    def get(self, request, *args, **kwargs):
        pk_campana = kwargs.get('pk_campana')
        campana = Campana.objects.get(pk=pk_campana)
        contactos = self._procesar_api(request, campana)
        result_dict = self._procesar_contactos_salida(request, campana, contactos)
        return Response(result_dict)


class Click2CallView(APIView):
    """
        Vista para ejecutar un click2call desde un sistema externo
        Params:
        - idExternalSystem (opcional)
        - idCampaign, idAgent, idContact, phone
    """
    permission_classes = (IsAuthenticated, EsAgentePermiso, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )

    def post(self, request):
        self.sistema_externo = None
        if 'idExternalSystem' in request.data:
            try:
                id_external_system = request.data['idExternalSystem']
                self.sistema_externo = SistemaExterno.objects.get(id=id_external_system)
            except SistemaExterno.DoesNotExist:
                return Response(data={
                    'status': 'ERROR',
                    'message': _('Hubo errores en los datos recibidos'),
                    'errors': {'idExternalSystem': [_('Sistema externo inexistente.')]}
                })
            form = Click2CallExternalSiteParametersForm(sistema_externo=self.sistema_externo,
                                                        data=request.data)
        else:
            form = Click2CallOMLParametersForm(request.data)

        if form.is_valid():
            agente = form.get_agente()
            campana = form.get_campana()
            contacto_id = form.get_contacto_id()
            telefono = form.cleaned_data.get('phone')
            click2call_type = 'contactos'       # TODO: Consultar con Fabian

            originator = Click2CallOriginator()
            error = originator.call_originate(
                agente, campana.id, str(campana.type), contacto_id, telefono, click2call_type)
            if error is None:
                return Response(data={
                    'status': 'OK',
                })
            else:
                return Response(data={
                    'status': 'ERROR',
                    'message': _('Error al ejecutar la llamada'),
                    'errors': [error]
                })
            return Response(data={
                'status': 'OK',
            })
        else:
            return Response(data={
                'status': 'ERROR',
                'message': _('Hubo errores en los datos recibidos'),
                'errors': form.errors
            })
