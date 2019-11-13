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

from django.contrib.auth import authenticate, logout
from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect

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
                                 UserSerializer, CalificacionClienteSerializer,
                                 CalificacionClienteNuevoContactoSerializer,
                                 OpcionCalificacionSerializer)
from api_app.forms import Click2CallOMLParametersForm, Click2CallExternalSiteParametersForm

from ominicontacto_app.models import (Campana, AgenteProfile, Contacto, CalificacionCliente,
                                      SistemaExterno)
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.services.asterisk.supervisor_activity import SupervisorActivityAmiManager
from ominicontacto_app.services.click2call import Click2CallOriginator
from ominicontacto_app.forms import FormularioNuevoContacto
from reportes_app.reportes.reporte_llamadas_supervision import (
    ReporteDeLLamadasEntrantesDeSupervision, ReporteDeLLamadasSalientesDeSupervision
)


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


class EsSupervisorOAgentePermiso(BasePermission):
    """Permiso para aplicar a vistas solo para supervisores normales o agentes"""

    def has_permission(self, request, view):
        super(EsSupervisorOAgentePermiso, self).has_permission(request, view)
        return request.user.get_is_agente() or request.user.get_is_supervisor_normal()


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
    agentes_parseados = SupervisorActivityAmiManager()

    def get(self, request):
        data = list(self.agentes_parseados._obtener_agentes_activos())
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
        servicio_acciones = SupervisorActivityAmiManager()
        error = servicio_acciones.ejecutar_accion_sobre_agente(
            self.supervisor, self.agente_id, accion)
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


class AgentLoginAsterisk(View):
    """
        Vista para ejecutar el login de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077LOGIN
    """
    def post(self, request):
        agent_login_manager = AgentActivityAmiManager()
        agente_profile = self.request.user.get_agente_profile()
        queue_add_error, insert_astdb_error, queue_unpause_error = agent_login_manager.login_agent(
            agente_profile)
        if queue_add_error or insert_astdb_error or queue_unpause_error:
            return JsonResponse(data={
                'status': 'ERROR',
            })
        else:
            return JsonResponse(data={
                'status': 'OK',
            })


class AgentLogoutAsterisk(View):
    """
        Vista para ejecutar el logout de agente a asterisk, realizando las acciones
        que solia hacer la extension 066LOGOUT
    """

    def dispatch(self, request, *args, **kwargs):
        agent_login_manager = AgentActivityAmiManager()
        agente_profile = self.request.user.get_agente_profile()
        agent_login_manager.logout_agent(agente_profile)
        logout(request)
        return redirect('login')


class AgentPauseAsterisk(View):
    """
        Vista para ejecutar la pausa de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077X
    """

    def post(self, request):
        agent_login_manager = AgentActivityAmiManager()
        pause_id = request.POST.get('pause_id')
        agente_profile = self.request.user.get_agente_profile()
        queue_pause_error, insert_astdb_error = agent_login_manager.pause_agent(
            agente_profile, pause_id)
        if queue_pause_error or insert_astdb_error:
            return JsonResponse(data={
                'status': 'ERROR',
            })
        else:
            return JsonResponse(data={
                'status': 'OK',
            })


class AgentUnpauseAsterisk(View):
    """
        Vista para ejecutar la despausa de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077UNPAUSE
    """

    def post(self, request):
        agent_login_manager = AgentActivityAmiManager()
        pause_id = request.POST.get('pause_id')
        agente_profile = self.request.user.get_agente_profile()
        queue_pause_error, insert_astdb_error = agent_login_manager.unpause_agent(
            agente_profile, pause_id)
        if queue_pause_error or insert_astdb_error:
            return JsonResponse(data={
                'status': 'ERROR',
            })
        else:
            return JsonResponse(data={
                'status': 'OK',
            })


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


class ApiCalificacionClienteView(viewsets.ModelViewSet):
    """Vista que permite gestionar calificaciones """

    permission_classes = (IsAuthenticated, EsAgentePermiso)
    serializer_class = CalificacionClienteSerializer
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        agente = self.request.user.agenteprofile
        calificaciones_agente = CalificacionCliente.objects.filter(agente=agente)
        return calificaciones_agente


class ApiCalificacionClienteCreateView(viewsets.ModelViewSet):
    """Vista que permite crear una calificación"""
    permission_classes = (IsAuthenticated, EsAgentePermiso)
    serializer_class = CalificacionClienteNuevoContactoSerializer
    http_method_names = ['post']


class ContactoCreateView(APIView):
    permission_classes = (IsAuthenticated, EsSupervisorOAgentePermiso)
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication)
    http_method_names = ['post']
    renderer_classes = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        msg_error_datos = _('Hubo errores en los datos recibidos')
        # Veo si los ids corresponden a un sistema externo
        sistema_externo = None
        if 'idExternalSystem' in request.data:
            try:
                id_external_system = request.data.pop('idExternalSystem')
                sistema_externo = SistemaExterno.objects.get(id=id_external_system)
            except SistemaExterno.DoesNotExist:
                return Response(data={
                    'status': 'ERROR',
                    'message': msg_error_datos,
                    'errors': {'idExternalSystem': [_('Sistema externo inexistente.')]}
                }, status=HTTP_400_BAD_REQUEST)

        # Obtengo la campaña a la cual corresponde la base de datos
        try:
            id_campana = request.data.pop('idCampaign')
        except KeyError:
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('Debe indicar un idCampaign.')]}
            }, status=HTTP_400_BAD_REQUEST)

        try:
            if sistema_externo:
                campana = Campana.objects.obtener_activas().get(id_externo=id_campana)
            else:
                campana = Campana.objects.obtener_activas().get(id=id_campana)
        except Campana.DoesNotExist:
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('Campana inexistente.')]}
            }, status=HTTP_400_BAD_REQUEST)

        if not self._user_tiene_permiso_en_campana(campana):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('No tiene permiso para editar la campaña.')]}
            }, status=HTTP_400_BAD_REQUEST)

        # Valido los campos enviados
        metadata = campana.bd_contacto.get_metadata()
        extras = set(request.data.keys()) - set(metadata.nombres_de_columnas)
        if len(extras) > 0:
            return Response(data={
                'status': 'ERROR',
                'message': _('Se recibieron campos incorrectos'),
                'errors': extras,
            }, status=HTTP_400_BAD_REQUEST)

        # Valido los campos enviados
        if metadata.nombre_campo_telefono not in request.data:
            return Response(data={
                'status': 'ERROR',
                'message': _('El campo es obligatorio'),
                'errors': metadata.nombre_campo_telefono,
            }, status=HTTP_400_BAD_REQUEST)

        # Reemplazo campo 'telefono'
        request.data['telefono'] = request.data.pop(metadata.nombre_campo_telefono)

        # Reemplazo campo 'id_externo'
        if metadata.nombre_campo_id_externo and metadata.nombre_campo_id_externo in request.data:
            request.data['id_externo'] = request.data.pop(metadata.nombre_campo_id_externo)

        form = FormularioNuevoContacto(base_datos=campana.bd_contacto, data=request.data)
        if form.is_valid():
            # TODO: Decidir si esto lo tiene que hacer el form o la vista
            contacto = form.save(commit=False)
            if self.user.get_is_supervisor_normal():
                campana.bd_contacto.cantidad_contactos += 1
                campana.bd_contacto.save()
            contacto.datos = form.get_datos_json()
            contacto.save()

            # TODO: OML-1016
            return Response(data={
                'status': 'OK',
                'message': _('Contacto agregado'),
                'id': contacto.id,
                'contacto': contacto.obtener_datos()
            })
        else:
            errors = form.errors
            if 'telefono' in errors:
                errors[metadata.nombre_campo_telefono] = errors.pop('telefono')
            if 'id_externo' in errors:
                errors[metadata.nombre_campo_id_externo] = errors.pop('id_externo')

            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': form.errors
            }, status=HTTP_400_BAD_REQUEST)

    def _user_tiene_permiso_en_campana(self, campana):
        user = self.request.user
        if user.get_is_agente():
            return user.get_agente_profile() in campana.obtener_agentes()
        else:
            return user in campana.supervisors.all()
