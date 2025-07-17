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

import re
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str
from django.core.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework import serializers
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.base_de_contactos import (CampaingsOnDBSerializer)
from ominicontacto_app.forms.base import FormularioNuevoContacto
from ominicontacto_app.models import SistemaExterno, Campana, BaseDatosContacto, Contacto
from ominicontacto_app.models import TelephoneValidator
from ominicontacto_app.utiles import (
    validar_solo_alfanumericos_o_guiones, validar_longitud_nombre_base_de_contactos, elimina_tildes)

import json

DOUBLE_SPACES = re.compile(r' +')


class CampaingsOnDB(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron las campanas asociadas a la base de '
                         'contactos de forma exitosa'),
            'data': None}
        try:
            db = BaseDatosContacto.objects.get(pk=pk)
            data['data'] = CampaingsOnDBSerializer(db).data
            return Response(data=data, status=status.HTTP_200_OK)
        except BaseDatosContacto.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = 'No existe la base de datos de contactos'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener las campañas asociadas a la '
                                'base de datos de contactos')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactoDeCampanaCreateView(APIView):
    permission_classes = (TienePermisoOML, )
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
                }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        if not self._user_tiene_permiso_en_campana(campana):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('No tiene permiso para editar la campaña.')]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Valido los campos enviados
        metadata = campana.bd_contacto.get_metadata()
        extras = set(request.data.keys()) - set(metadata.nombres_de_columnas)
        if len(extras) > 0 and extras != {'confirmar_duplicado'}:
            return Response(data={
                'status': 'ERROR',
                'message': _('Se recibieron campos incorrectos'),
                'errors': extras,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Valido los campos enviados
        if metadata.nombre_campo_telefono not in request.data:
            return Response(data={
                'status': 'ERROR',
                'message': _('El campo es obligatorio'),
                'errors': metadata.nombre_campo_telefono,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Reemplazo campo 'telefono'
        request.data['telefono'] = request.data.pop(metadata.nombre_campo_telefono)

        # Reemplazo campo 'id_externo'
        if metadata.nombre_campo_id_externo and metadata.nombre_campo_id_externo in request.data:
            request.data['id_externo'] = request.data.pop(metadata.nombre_campo_id_externo)
        control_de_duplicados = campana.control_de_duplicados if campana else None
        # Permito duplicar sin enviar confirmación por API
        if control_de_duplicados == Campana.PERMITIR_DUPLICADOS:
            request.data['confirmar_duplicado'] = True
        form = FormularioNuevoContacto(base_datos=campana.bd_contacto, data=request.data,
                                       control_de_duplicados=control_de_duplicados)
        if form.is_valid():
            # TODO: Decidir si esto lo tiene que hacer el form o la vista
            contacto = form.save(commit=False)
            if self.request.user.get_is_supervisor_normal():
                campana.bd_contacto.cantidad_contactos += 1
                campana.bd_contacto.save()
            contacto.datos = form.get_datos_json()
            contacto.save()

            # TODO: OML-1016 - Agregar en Wombat si quien lo crea es supervisor.

            # Agrego la relación de AgenteEnContacto
            if campana.type == Campana.TYPE_PREVIEW:
                es_originario = True
                agente_id = -1
                es_agente = self.request.user.get_is_agente()
                if es_agente:
                    agente_id = self.request.user.get_agente_profile().id
                    es_originario = False

                campana.adicionar_agente_en_contacto(
                    contacto, agente_id=agente_id, es_originario=es_originario)

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
            }, status=status.HTTP_400_BAD_REQUEST)

    def _user_tiene_permiso_en_campana(self, campana):
        user = self.request.user
        if user.get_is_agente():
            return user.get_agente_profile() in campana.obtener_agentes()
        else:
            return user in campana.supervisors.all()


class CampaignDatabaseMetadataView(APIView):
    permission_classes = (TienePermisoOML, )
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
                }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_400_BAD_REQUEST)

        if not self._user_tiene_permiso_en_campana(campana):
            return Response(data={
                'status': 'ERROR',
                'message': msg_error_datos,
                'errors': {'idCampaign': [_('No tiene permiso para editar la campaña.')]}
            }, status=status.HTTP_400_BAD_REQUEST)

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


class CamposDireccionView(APIView):
    def get(self, request, pk):
        try:
            base_dato = BaseDatosContacto.objects.get(id=pk)
            data = json.loads(base_dato.metadata).get('nombres_de_columnas', [])
            # TODO: No debería filtrar todos los campos que son telefonicos? (no x nombre nomas)
            return Response([x for x in data if 'telefono' not in x])
        except Exception as e:
            print(">>>>>", e)


class BaseDatosContactoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    phone_fields = serializers.JSONField()
    data_fields = serializers.JSONField()
    external_id_field = serializers.CharField(required=False)

    def validate_name(self, nombre):
        if BaseDatosContacto.objects.filter(nombre=nombre).exists():
            raise serializers.ValidationError(
                _('Ya existe una base de datos de contactos con ese nombre'))
        validar_solo_alfanumericos_o_guiones(nombre)
        validar_longitud_nombre_base_de_contactos(nombre)

        return nombre

    def _sanear_nombre_de_campo(self, nombre):
        """Realiza saneamiento básico del nombre del campo. Con basico se refiere a:
        - eliminar trailing spaces
        - NO pasar a mayusculas
        - reemplazar espacios por '_'
        - eliminar tildes

        Los caracteres invalidos NO son borrados.
        """
        nombre = smart_str(nombre)
        nombre = nombre.strip()  # .upper()
        nombre = DOUBLE_SPACES.sub("_", nombre)
        nombre = elimina_tildes(nombre)
        return nombre

    def _validar_lista_de_campos(self, lista_de_campos):
        if not isinstance(lista_de_campos, list):
            raise serializers.ValidationError(_('Debe ingresar una lista'))
        if len(lista_de_campos) < 1:
            raise serializers.ValidationError(_('Debe ingresar al menos un campo'))
        return [self._sanear_nombre_de_campo(nombre) for nombre in lista_de_campos]

    def validate_phone_fields(self, campos_telefono):
        return self._validar_lista_de_campos(campos_telefono)

    def validate_data_fields(self, campos_dato):
        return self._validar_lista_de_campos(campos_dato)

    def validate_external_id_field(self, campo_id_externo):
        if campo_id_externo:
            return self._sanear_nombre_de_campo(campo_id_externo)

    def validate(self, data):
        campos = set(data['phone_fields']).union(set(data['data_fields']))
        repetidos = False
        repetidos = len(campos) < len(data['phone_fields']) + len(data['data_fields'])
        id_externo = data.get('external_id_field')
        if id_externo:
            repetidos = repetidos or id_externo in campos
        if repetidos:
            raise serializers.ValidationError(
                _('Los nombres de los campos no pueden estar repetidos'))
        return data

    def create(self, data):
        bd_contactos = BaseDatosContacto(
            nombre=data['name'],
            archivo_importacion='',
            nombre_archivo_importacion='',
            estado=BaseDatosContacto.ESTADO_DEFINIDA)
        metadata = bd_contactos.get_metadata()

        nombres = data['phone_fields'] + data['data_fields']
        id_externo = data.get('external_id_field')
        if id_externo:
            nombres.append(id_externo)

        metadata.cantidad_de_columnas = len(nombres)
        metadata.columnas_con_telefono = list(range(len(data['phone_fields'])))
        if id_externo:
            metadata.columna_id_externo = metadata.cantidad_de_columnas - 1
        metadata.nombres_de_columnas = nombres
        metadata.save()
        return bd_contactos


class BaseDatosContactoCreateView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication)
    http_method_names = ['post']
    renderer_classes = (JSONRenderer, )

    def post(self, request):
        request_data = request.data.copy()
        serializer = BaseDatosContactoSerializer(data=request_data)
        if serializer.is_valid():
            bd_contacto = serializer.save()
            metadata = bd_contacto.get_metadata()
            bd_data = {
                'id': bd_contacto.id,
                'name': bd_contacto.nombre,
                'main_phone': metadata.nombre_campo_telefono,
                'external_id': metadata.nombre_campo_id_externo,
                'fields': metadata.nombres_de_columnas,
            }
            return Response(data={'status': 'SUCCESS',
                                  'data': bd_data,
                                  'message': _('Se creo la BD de Contactos de forma exitosa'), },
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data={'message': _('Error en los datos'),
                                  'errors': serializer.errors, },
                            status=status.HTTP_400_BAD_REQUEST)


class ContactoCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.bd_contacto = kwargs.pop('context', {}).get('bd_contacto')
        self.ids_externos = []
        super().__init__(*args, **kwargs)

    class Meta:
        model = Contacto
        fields = [
            'id',
            'telefono',
            'datos',
            'bd_contacto',
            'id_externo'
        ]

    def validar_telefono(self, field, value):
        try:
            TelephoneValidator(value)
        except ValidationError as error:
            raise serializers.ValidationError({field: error.message})
        return value

    def validar_id_externo(self, field, value):
        if value in self.bd_contacto.contactos.all().values_list('id_externo', flat=True)\
           or value in self.ids_externos:
            msg = _('El id externo debe ser único en la base de datos - {}'.format(value))
            raise serializers.ValidationError({field: msg})
        self.ids_externos.append(value)
        return value

    def to_internal_value(self, data):
        bd_contacto = self.bd_contacto
        fields = bd_contacto.get_metadata().nombres_de_columnas
        if set(data.keys()).issubset(set(fields)):
            contact = {}
            metadata = bd_contacto.get_metadata()
            nombre_campo_telefono = metadata.nombre_campo_telefono
            nombre_campo_id_externo = metadata.nombre_campo_id_externo
            fields = metadata.nombres_de_columnas

            if nombre_campo_telefono in data:
                telefono = data.pop(nombre_campo_telefono)
                contact['telefono'] = self.validar_telefono(nombre_campo_telefono, telefono)
            else:
                raise serializers.ValidationError({nombre_campo_telefono: _('campo requerido')})

            if nombre_campo_id_externo in data:
                id_externo = data.pop(nombre_campo_id_externo)
                contact['id_externo'] =\
                    self.validar_id_externo(nombre_campo_id_externo, id_externo)

            contact_datos = []
            for field in fields:
                if field not in [nombre_campo_telefono, nombre_campo_id_externo]:
                    value = data.get(field, '')
                    contact_datos.append(value)
            contact['datos'] = json.dumps(contact_datos)
            contact['bd_contacto'] = self.bd_contacto.id
        else:
            raise serializers.ValidationError(
                {'Error': _('Campos invalidos: {}'.format(
                    list(set(data.keys()).difference(set(fields)))))})

        return super(ContactoCreateSerializer, self).to_internal_value(contact)


class ContactoListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    telefono = serializers.CharField()
    datos = serializers.CharField()
    bd_contacto = serializers.PrimaryKeyRelatedField(queryset=BaseDatosContacto.objects.all())
    id_externo = serializers.CharField()


class ContactoCreateView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication)
    http_method_names = ['post', 'get']
    renderer_classes = (JSONRenderer, )

    def post(self, request, db_pk):
        try:
            bd_contacto = BaseDatosContacto.objects.get(id=db_pk)
        except BaseDatosContacto.DoesNotExist:
            return Response(data={'error': _('Base de datos inexistente')},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ContactoCreateSerializer(
            data=request.data, context={'bd_contacto': bd_contacto}, many=True)
        if serializer.is_valid():
            serializer.save()
            # TODO: OML-1016 - Agregar en Wombat si quien lo crea es supervisor.
            # TODO: Agrego la relación de AgenteEnContacto para todas las campañas preview?
            return Response(data={'status': 'SUCCESS',
                                  'data': serializer.data,
                                  'message': _('Se crearon los contactos de forma exitosa'), },
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data={'message': _('Error en los datos'),
                                  'errors': serializer.errors, },
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, db_pk):
        try:
            bd_contacto = BaseDatosContacto.objects.get(id=db_pk)
            contactos = bd_contacto.contactos.all()
            serializer = ContactoListSerializer(contactos, many=True)
            return Response(data={'status': 'SUCCESS',
                                  'data': serializer.data,
                                  'message': _('Se obtuvieron los contactos de forma exitosa')},
                            status=status.HTTP_200_OK)
        except BaseDatosContacto.DoesNotExist:
            return Response(data={'error': _('Base de datos inexistente')},
                            status=status.HTTP_404_NOT_FOUND)
