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
from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.views import APIView

from api_app.authentication import token_expire_handler, expires_in, ExpiringTokenAuthentication
from api_app.serializers import UserSigninSerializer, UserSerializer
from api_app.views.permissions import EsSupervisorOAgentePermiso
from ominicontacto_app.forms import FormularioNuevoContacto
from ominicontacto_app.models import SistemaExterno, Campana


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
            if sistema_externo is None:
                id_campana = int(id_campana)
        except (KeyError, ValueError, TypeError):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('Debe indicar un idCampaign válido.')]}
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
                'errors': {'idCampaign': [_('Campaña inexistente.')]}
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
            if self.request.user.get_is_supervisor_normal():
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


class CampaignDatabaseMetadataView(APIView):
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
                id_external_system = request.data.get('idExternalSystem')
                sistema_externo = SistemaExterno.objects.get(id=id_external_system)
            except SistemaExterno.DoesNotExist:
                return Response(data={
                    'status': 'ERROR',
                    'message': msg_error_datos,
                    'errors': {'idExternalSystem': [_('Sistema externo inexistente.')]}
                }, status=HTTP_400_BAD_REQUEST)

        # Obtengo la campaña a la cual corresponde la base de datos
        try:
            id_campana = request.data.get('idCampaign')
            if sistema_externo is None:
                id_campana = int(id_campana)
        except (KeyError, ValueError, TypeError):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('Debe indicar un idCampaign válido.')]}
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
                'errors': {'idCampaign': [_('Campaña inexistente.')]}
            }, status=HTTP_400_BAD_REQUEST)

        if not self._user_tiene_permiso_en_campana(campana):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('No tiene permiso para editar la campaña.')]}
            }, status=HTTP_400_BAD_REQUEST)

        metadata = campana.bd_contacto.get_metadata()

        return Response(data={
            'status': 'OK',
            'main_phone': metadata.nombre_campo_telefono,
            'external_id': metadata.nombre_campo_id_externo,
            'fields': metadata.nombres_de_columnas,
        })

    def _user_tiene_permiso_en_campana(self, campana):
        user = self.request.user
        if user.get_is_agente():
            return user.get_agente_profile() in campana.obtener_agentes()
        else:
            return user in campana.supervisors.all()
