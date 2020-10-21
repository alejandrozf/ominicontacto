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
from django.forms import ValidationError

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api_app.authentication import ExpiringTokenAuthentication
from api_app.serializers import AgenteProfileSerializer
from api_app.views.permissions import TienePermisoOML
from api_app.services.base_datos_contacto_service import BaseDatosContactoService
from ominicontacto_app.models import AgenteProfile, User
from ominicontacto_app.permisos import PermisoOML
from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, OmlError, \
    OmlParserRepeatedColumnsError
from django.utils.encoding import smart_text
from ominicontacto_app.utiles import elimina_tildes, validar_longitud_nombre_base_de_contactos
import re


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


class SubirBaseContactosView(APIView):
    """Subir y almacenar una base de contactos desde archivo csv"""
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']
    base_datos_contacto_service = BaseDatosContactoService()

    def post(self, request):
        id = None
        error = True
        LONGITUD_MAXIMA = 45
        try:
            file = request.FILES['filename']
            filename = file.name
            db_name = self._obtiene_parametro(request, 'nombre')
            validar_longitud_nombre_base_de_contactos(db_name)
            campos_telefono_str = self._obtiene_parametro(request, 'campos_telefono')
            id_externo = self._obtiene_parametro(request, 'id_externo', True)
            id = self.base_datos_contacto_service.crear_bd_contactos(file, filename, db_name)
            campos_telefono = self._procesa_campos_telefono(campos_telefono_str)
            id_externo = self._comprueba_campo_id_externo(id_externo)

            self.base_datos_contacto_service.importa_contactos_desde_api(id, campos_telefono,
                                                                         id_externo)
            error = False
        except ValidationError:
            return Response(
                data={'status': 'ERROR',
                      'message': _(
                          'La longitud del nombre no debe exceder los {0} caracteres'.format(
                              LONGITUD_MAXIMA))})
        except OmlArchivoImportacionInvalidoError:
            return Response(data={'status': 'ERROR',
                                  'message': _('la extensión del archivo no es .CSV')})
        except KeyError:
            return Response(data={'status': 'ERROR',
                                  'message': _('falta parámetro filename en request')})
        except OmlParserRepeatedColumnsError:
            return Response(data={'status': 'ERROR',
                                  'message': _("El archivo a procesar tiene nombres de columnas "
                                               "repetidos.")})
        except OmlError as e:
            return Response(data={'status': 'ERROR',
                                  'message': e.__str__()})
        except Exception:
            return Response(data={'status': 'ERROR',
                                  'message': _('no se pudo crear la base de datos de contacto')})
        finally:
            if id is not None and error:
                self.base_datos_contacto_service.remove_db(id)

        return Response(data={'status': 'OK', 'id': id})

    def _obtiene_parametro(self, request, nombre_parametro, parametro_opcional=False) -> str:
        param = request.data.get(nombre_parametro, None)
        if param is not None or parametro_opcional is True:
            return param

        message = _('falta parámetro:') + nombre_parametro
        raise OmlError(message)

    def _procesa_campos_telefono(self, campos_telefono_str) -> list:
        ct = campos_telefono_str \
            .strip() \
            .lstrip(',') \
            .rstrip(',') \
            .split(',')
        campos_telefono = [self._sanear_nombre_de_columna(x) for x in ct]

        if len(campos_telefono) == 0:
            raise OmlError(_('lista de campos teléfono vacia'))
        for campo_t in campos_telefono:
            if campo_t not in self.base_datos_contacto_service.parser.columnas:
                raise OmlError(_('campo de teléfono no coincide con nombre de columna'))

        return campos_telefono

    def _comprueba_campo_id_externo(self, id_externo):
        id_externo = self._sanear_nombre_de_columna(id_externo)
        if id_externo is not None and \
                id_externo not in self.base_datos_contacto_service.parser.columnas:
            raise OmlError(_('campo de id externo no coincide con nombre de columna'))
        return id_externo

    def _sanear_nombre_de_columna(self, nombre):
        """Realiza saneamiento básico del nombre de la columna. Con basico
        se refiere a:
        - eliminar trailing spaces
        - NO pasar a mayusculas
        - reemplazar espacios por '_'
        - eliminar tildes

        Los caracteres invalidos NO son borrados.
        """
        if nombre is not None:
            nombre = smart_text(nombre)
            nombre = nombre.strip()
            nombre = DOUBLE_SPACES.sub("_", nombre)
            nombre = elimina_tildes(nombre)
        return nombre


DOUBLE_SPACES = re.compile(r' +')
