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
from django.contrib.auth.models import Group

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api_app.authentication import ExpiringTokenAuthentication
from api_app.serializers import AgenteProfileSerializer
from api_app.views.permissions import TienePermisoOML
from ominicontacto_app.models import AgenteProfile, User
from ominicontacto_app.permisos import PermisoOML


class AgentesActivosGrupoViewSet(viewsets.ModelViewSet):
    """Servicio que devuelve las agentes activos de un grupo
    """
    serializer_class = AgenteProfileSerializer
    permission_classes = (TienePermisoOML, )
    http_method_names = ['get']

    def get_queryset(self):
        queryset = AgenteProfile.objects.obtener_activos()
        grupo_pk = self.kwargs.get('pk_grupo')
        queryset = queryset.filter(grupo__pk=grupo_pk)
        return queryset


class CrearRolView(APIView):
    """Crea un nuevo Rol"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        if 'name' not in request.data:
            return Response(data={'status': 'ERROR',
                                  'message': _('Se esperaba el campo "name"')})
        nombre = request.data.get('name')

        if Group.objects.filter(name=nombre).exists():
            return Response(data={'status': 'ERROR',
                                  'message': _('Ya existe un rol con ese nombre')})
        else:
            rol = Group(name=nombre)
            rol.save()
            return Response(data={
                'status': 'OK',
                'role': {
                    'id': rol.id,
                    'name': rol.name,
                    'permissions': list()
                }
            })


class ActualizarPermisosDeRolView(APIView):
    """Actualiza los permisos de un Rol"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        rol_id = request.data.get('role_id', None)
        if 'role_id' not in request.data or not isinstance(rol_id, int):
            return Response(data={'status': 'ERROR',
                                  'message': _('Se esperaba el campo "role_id" (numérico)')})
        try:
            inmutables = [User.ADMINISTRADOR, User.GERENTE, User.SUPERVISOR, User.REFERENTE,
                          User.AGENTE, User.CLIENTE_WEBPHONE]
            rol = Group.objects.exclude(name__in=inmutables).get(id=rol_id)
        except Group.DoesNotExist:
            return Response(data={'status': 'ERROR',
                                  'message': _('Id de Rol incorrecto')})
        permisos_ids = request.data.get("permissions")
        if 'permissions' not in request.data or not isinstance(permisos_ids, list):
            return Response(data={'status': 'ERROR',
                                  'message': _('Se esperaba el campo "permissions" (lista)')})

        permisos_en_base = PermisoOML.objects.filter(id__in=permisos_ids)
        if not permisos_en_base.count() == len(permisos_ids):
            return Response(data={'status': 'ERROR',
                                  'message': _('Lista de permisos incorrecta')})

        rol.permissions.set(permisos_en_base)
        return Response(data={'status': 'OK'})


class EliminarRolView(APIView):
    """Elimina un rol"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        rol_id = request.data.get('role_id', None)
        try:
            inmutables = [User.ADMINISTRADOR, User.GERENTE, User.SUPERVISOR, User.REFERENTE,
                          User.AGENTE, User.CLIENTE_WEBPHONE]
            rol = Group.objects.exclude(name__in=inmutables).get(id=rol_id)
        except Group.DoesNotExist:
            return Response(data={'status': 'ERROR',
                                  'message': _('Id de Rol incorrecto')})
        cant_usuarios = rol.user_set.count()
        # TODO: Definir si enviar en el mensaje los usernames de los usuarios.
        if cant_usuarios > 0:
            return Response(data={'status': 'ERROR',
                                  'message': _('No se puede borrar un rol asignado a usuarios.')})
        rol.delete()
        return Response(data={'status': 'OK'})
