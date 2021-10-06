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

from django.utils.translation import ugettext as _
from django.contrib.auth import logout
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api_app.authentication import ExpiringTokenAuthentication
from api_app.forms import Click2CallOMLParametersForm, Click2CallExternalSiteParametersForm
from api_app.serializers import (OpcionCalificacionSerializer, CalificacionClienteSerializer,
                                 CalificacionClienteNuevoContactoSerializer)
from api_app.views.permissions import TienePermisoOML

from ominicontacto_app.models import (
    Campana, SistemaExterno, CalificacionCliente, Contacto, AuditoriaCalificacion)
from reportes_app.models import LlamadaLog
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.services.click2call import Click2CallOriginator

from ominicontacto_app.services.kamailio_service import KamailioService
from api_app.services.calificacion_llamada import CalificacionLLamada


class ObtenerCredencialesSIPAgenteView(APIView):
    permission_classes = (TienePermisoOML, )
    # authentication_classes = (BasicAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get', ]

    def get(self, request):
        usuario_agente = request.user
        agente_profile = usuario_agente.get_agente_profile()
        kamailio_service = KamailioService()
        sip_user = kamailio_service.generar_sip_user(agente_profile.sip_extension)
        sip_password = kamailio_service.generar_sip_password(sip_user)

        if sip_password is None:
            return Response(data={
                'status': 'ERROR',
                'message': _('Error al generar sip password'),
            })
        return Response(data={
            'status': 'OK',
            'sip_user': sip_user,
            'sip_password': sip_password,
        })


class OpcionesCalificacionViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las opciones de calificación de una campaña
    """
    serializer_class = OpcionCalificacionSerializer
    permission_classes = (TienePermisoOML, )
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


class ApiCalificacionClienteView(viewsets.ModelViewSet):
    """Vista que permite gestionar calificaciones """

    permission_classes = (TienePermisoOML, )
    serializer_class = CalificacionClienteSerializer
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        agente = self.request.user.agenteprofile
        calificaciones_agente = CalificacionCliente.objects.filter(agente=agente)
        return calificaciones_agente


class ApiCalificacionClienteCreateView(viewsets.ModelViewSet):
    """Vista que permite crear una calificación"""
    permission_classes = (TienePermisoOML, )
    serializer_class = CalificacionClienteNuevoContactoSerializer
    http_method_names = ['post']


class API_ObtenerContactosCampanaView(APIView):

    permission_classes = (TienePermisoOML, )
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
    permission_classes = (TienePermisoOML, )
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
            # TODO: Verificar que el agente que dispara la llamada es el mismo de la autenticación
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


class AgentLoginAsterisk(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    """
        Vista para ejecutar el login de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077LOGIN
    """
    def post(self, request):
        agente_profile = self.request.user.get_agente_profile()
        agent_login_manager = AgentActivityAmiManager()
        error = agent_login_manager.login_agent(agente_profile, manage_connection=True)
        if error:
            return Response(data={
                'status': 'ERROR',
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class AgentLogoutAsterisk(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']
    """
        Vista para ejecutar el logout de agente a asterisk, realizando las acciones
        que solia hacer la extension 066LOGOUT
    """

    def post(self, request, *args, **kwargs):
        agente_profile = self.request.user.get_agente_profile()
        agent_login_manager = AgentActivityAmiManager()
        queue_remove_error, insert_redis_error = agent_login_manager.logout_agent(
            agente_profile, manage_connection=True)
        if insert_redis_error or queue_remove_error:
            return Response(data={
                'status': 'ERROR',
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class AgentLogoutView(View):
    """
        Vista para ejecutar el logout de agente a asterisk, realizando las acciones
        que solia hacer la extension 066LOGOUT
    """

    def dispatch(self, request, *args, **kwargs):
        agente_profile = self.request.user.get_agente_profile()
        agent_login_manager = AgentActivityAmiManager()
        agent_login_manager.logout_agent(agente_profile, manage_connection=True)
        logout(request)
        return redirect('login')


class AgentPauseAsterisk(APIView):
    """
        Vista para ejecutar la pausa de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077X
    """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        agent_login_manager = AgentActivityAmiManager()
        pause_id = request.data.get('pause_id')
        agente_profile = self.request.user.get_agente_profile()
        queue_pause_error, insert_redis_error = agent_login_manager.pause_agent(
            agente_profile, pause_id, manage_connection=True)
        if queue_pause_error or insert_redis_error:
            return Response(data={
                'status': 'ERROR',
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class AgentUnpauseAsterisk(APIView):
    """
        Vista para ejecutar la despausa de agente a asterisk, realizando las acciones
        que solia hacer la extension 0077UNPAUSE
    """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        agent_login_manager = AgentActivityAmiManager()
        pause_id = request.data.get('pause_id')
        agente_profile = self.request.user.get_agente_profile()
        queue_pause_error, insert_redis_error = agent_login_manager.unpause_agent(
            agente_profile, pause_id, manage_connection=True)
        if queue_pause_error or insert_redis_error:
            return Response(data={
                'status': 'ERROR',
            })
        else:
            return Response(data={
                'status': 'OK',
            })


class SetEstadoRevisionAuditoria(APIView):
    """ Vista para marcar si una auditoria fue revisada """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        auditoria_id = request.data.get('audit_id')
        status = request.data.get('revised') == 'true'
        agente_profile = self.request.user.get_agente_profile()
        try:
            auditoria = AuditoriaCalificacion.objects.get(id=auditoria_id)
        except AuditoriaCalificacion.DoesNotExist:
            return Response(data={
                'status': 'ERROR',
                'message': _('Auditoría inexistente'),
            })
        if not auditoria.calificacion.agente == agente_profile:
            return Response(data={
                'status': 'ERROR',
                'message': _('No tiene permiso para modificar la auditoría'),
            })

        auditoria.revisada = status
        auditoria.save()

        return Response(data={
            'status': 'OK',
            'audit_status': status
        })


class ApiStatusCalificacionLlamada(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        redis_data = CalificacionLLamada()
        agente = self.request.user.get_agente_profile()
        datos_llamada = redis_data.get_family(agente)
        call_data = datos_llamada.get('CALLDATA')
        id_calificacion = datos_llamada.get('IDCALIFICACION')
        if not datos_llamada:
            return Response(data={
                'calificada': 'True',
            })
        if datos_llamada['CALIFICADA'] == 'TRUE':
            return Response(data={
                'calificada': 'True',
            })
        elif datos_llamada['GESTION'] == 'TRUE':
            return Response(data={
                'calldata': call_data,
                'gestion': 'True',
                'id_calificacion': id_calificacion,
            })
        elif not call_data:
            return Response(data={
                'calificada': 'True',
            })
        else:
            return Response(data={
                'calificada': 'False',
                'calldata': call_data,
            })


class ApiEventoHold(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        agente = self.request.user.get_agente_profile()
        llamadalog = LlamadaLog.objects.filter(agente_id=agente.id).last()
        callid = llamadalog.callid
        campana_id = llamadalog.campana_id
        tipo_campana = llamadalog.tipo_campana
        tipo_llamada = llamadalog.tipo_llamada
        if llamadalog.event == 'HOLD':
            event = 'UNHOLD'
        else:
            event = 'HOLD'

        evento_hold = LlamadaLog.objects.create(duracion_llamada=-1, agente_id=agente.id,
                                                callid=callid, campana_id=campana_id,
                                                tipo_campana=tipo_campana,
                                                tipo_llamada=tipo_llamada,
                                                event=event, time=timezone.now())
        evento_hold.save()
        if evento_hold:
            return Response(data={'status': 'OK'})
        else:
            return Response(data={'status': 'ERROR'})
