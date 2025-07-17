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
import json
from functools import reduce
from operator import or_
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data

from ominicontacto_app.models import Campana, Contacto
from ominicontacto_app.models import TelephoneValidator
from whatsapp_app.models import ConversacionWhatsapp


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(source='telefono')
    data = serializers.SerializerMethodField()
    disposition = serializers.SerializerMethodField()

    def get_disposition(self, obj):
        disposition = obj.calificacioncliente_set.last()
        return disposition.id if disposition else None

    def get_data(self, obj):
        return obj.obtener_datos()


class RetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = [
            'id',
            'telefono',
            'datos',
            'bd_contacto',
        ]


class CreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.campana = kwargs.pop('context', {}).get('campana')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Contacto
        fields = [
            'id',
            'telefono',
            'datos',
            'bd_contacto',
        ]

    def es_campo_telefonico(self, field):
        for i in json.loads(self.campana.bd_contacto.metadata)['cols_telefono']:
            nombre_campo = json.loads(self.campana.bd_contacto.metadata)['nombres_de_columnas'][i]
            if field == nombre_campo:
                return True
        return False

    def validar_telefono(self, field, value):
        try:
            TelephoneValidator(value)
        except ValidationError as error:
            raise serializers.ValidationError({field: error.message})
        return value

    def get_datos_json(self, data):
        datos = []
        for field in json.loads(self.campana.bd_contacto.metadata)['nombres_de_columnas']:
            if data.get(field, '') and self.es_campo_telefonico(field):
                try:
                    TelephoneValidator(data.get(field))
                except ValidationError as error:
                    raise serializers.ValidationError({field: error.message})
            if field != 'telefono':
                campo = data.get(field, '')
                datos.append(campo if campo else "")
        return json.dumps(datos)

    def to_internal_value(self, data):
        mandatory = self.campana.get_campos_obligatorios()
        metadata = self.campana.bd_contacto.get_metadata()
        campos_bd = metadata.nombres_de_columnas
        telefono = metadata.nombre_campo_telefono
        if telefono in data['datos']:
            telefono_val = data['datos'].pop(telefono)
            data['telefono'] = self.validar_telefono(telefono, telefono_val)
        else:
            raise serializers.ValidationError({telefono: _('campo requerido')})
        if set(data['datos'].keys()).issubset(set(campos_bd)):
            if set(data['datos'].keys()).issuperset(set(mandatory)):
                data['datos'] = self.get_datos_json(data['datos'])
            else:
                raise serializers.ValidationError({'Error': _('Faltan campos requeridos')})
        else:
            raise serializers.ValidationError({'Error': _('Error en los campos de contacto')})
        return super(CreateSerializer, self).to_internal_value(data)


class UpdateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.campana = kwargs.pop('context', {}).get('campana')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Contacto
        fields = [
            'id',
            'telefono',
            'datos',
            'bd_contacto',
        ]

    def es_campo_telefonico(self, field):
        for i in json.loads(self.campana.bd_contacto.metadata)['cols_telefono']:
            nombre_campo = json.loads(self.campana.bd_contacto.metadata)['nombres_de_columnas'][i]
            if field == nombre_campo:
                return True
        return False

    def validar_telefono(self, field, value):
        try:
            TelephoneValidator(value)
        except ValidationError as error:
            raise serializers.ValidationError({field: error.message})
        return value

    def get_datos_json(self, data):
        datos = []
        for field in json.loads(self.campana.bd_contacto.metadata)['nombres_de_columnas']:
            if data.get(field, '') and self.es_campo_telefonico(field):
                try:
                    TelephoneValidator(data.get(field))
                except ValidationError as error:
                    raise serializers.ValidationError({field: error.message})
            if field != 'telefono':
                campo = data.get(field, '')
                datos.append(campo if campo else "")
        return json.dumps(datos)

    def to_internal_value(self, data):
        campos_no_editables = self.campana.get_campos_no_editables()
        campos_ocultos = self.campana.get_campos_ocultos()
        metadata = self.campana.bd_contacto.get_metadata()
        campos_bd = metadata.nombres_de_columnas
        telefono = metadata.nombre_campo_telefono
        if telefono in data['datos']:
            telefono_val = data['datos'].pop(telefono)
            data['telefono'] = self.validar_telefono(telefono, telefono_val)
        if set(data['datos'].keys()).issubset(set(campos_bd)):
            if not set(data['datos'].keys()).intersection(set(campos_no_editables))\
                    and not set(data['datos'].keys()).intersection(set(campos_ocultos)):
                data['datos'] = self.get_datos_json(data['datos'])
            else:
                raise serializers.ValidationError(
                    {'error': _('No puede editar campos ocultos o bloqueados')})
        else:
            raise serializers.ValidationError({'Error': _('Error en los campos de contacto')})
        return super(UpdateSerializer, self).to_internal_value(data)


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request, campana_pk):
        try:
            filtro = request.GET.get('search')
            campana = Campana.objects.get(id=campana_pk)
            listado_de_contacto = Contacto.objects.\
                contactos_by_filtro_bd_contacto(campana.bd_contacto, filtro)
        except Exception:
            listado_de_contacto = Contacto.objects.contactos_by_bd_contacto(
                campana.bd_contacto)
        serializer = ListSerializer(listado_de_contacto, many=True)
        return response.Response(
            data=get_response_data(
                status=HttpResponseStatus.SUCCESS,
                message=_('Se obtuvieron las contactos de forma exitosa'),
                data=serializer.data),
            status=status.HTTP_200_OK)

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path='create_contact_from_conversation/(?P<conversacion_pk>[^/.]+)')
    def create_contact_from_conversation(self, request, campana_pk, conversacion_pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            request_data = request.data.copy()
            data = {
                "bd_contacto": campana.bd_contacto.id,
                "datos": request_data
            }
            conversation = ConversacionWhatsapp.objects.get(id=conversacion_pk)
            serializer = CreateSerializer(data=data, context={'campana': campana})
            if serializer.is_valid():
                client = serializer.save()
                conversation.client = client
                conversation.save()
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se creo el nuevo contacto de forma exitosa'),
                        data=ListSerializer(client).data),
                    status=status.HTTP_201_CREATED)
            return response.Response(
                data=get_response_data(
                    message=_('Error en los datos'), errors=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al crear el contacto')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, campana_pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            request_data = request.data.copy()
            data = {
                "bd_contacto": campana.bd_contacto.id,
                "datos": request_data
            }
            serializer = CreateSerializer(data=data, context={'campana': campana})
            if serializer.is_valid():
                client = serializer.save()
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se creo el nuevo contacto de forma exitosa'),
                        data=ListSerializer(client).data),
                    status=status.HTTP_201_CREATED)
            return response.Response(
                data=get_response_data(
                    message=_('Error en los datos'), errors=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(message=_('Error al crear el contacto')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, campana_pk, pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            request_data = request.data.copy()
            data = {
                "datos": request_data
            }
            instance = Contacto.objects.get(pk=pk)
            serializer = UpdateSerializer(
                instance, data=data, partial=True, context={'campana': campana})
            if serializer.is_valid():
                client = serializer.save()
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se actualizo el nuevo contacto de forma exitosa'),
                        data=ListSerializer(client).data),
                    status=status.HTTP_201_CREATED)
            return response.Response(
                data=get_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=_('Error en los datos'), errors=serializer.errors))
        except Contacto.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('Contacto no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("----", e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar el contacto')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["get"])
    def db_fields(self, request, campana_pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            metadata = campana.bd_contacto.get_metadata()
            data = []
            for index, name in enumerate(metadata.nombres_de_columnas, start=0):
                field = {}
                field['name'] = name
                field['mandatory'] = name in campana.get_campos_obligatorios() \
                    or name == metadata.nombre_campo_telefono
                field['block'] = name in campana.get_campos_no_editables()
                field['hide'] = name in campana.get_campos_ocultos()
                field['is_phone_field'] = index in metadata.columnas_con_telefono
                data.append(field)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener los campos de contacto')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["post"])
    def search(self, request, campana_pk):
        try:
            values = request.data.values()
            q_list = [Q(datos__contains=x) for x in values]
            if 'dial_code' in request.data:
                q_list.append(Q(telefono__contains=request.data['dial_code']))
            if 'phone' in request.data:
                q_list.append(Q(telefono=request.data['phone']))
            if 'name' in request.data:
                q_list.append(Q(datos__icontains=request.data['name']))
            campana = Campana.objects.get(id=campana_pk)
            ids_contactos_en_curso = ConversacionWhatsapp.objects\
                .conversaciones_en_curso()\
                .filter(campana_id=campana.pk, client_id__isnull=False)\
                .values_list('client_id', flat=True)
            contactos = Contacto.objects.filter(
                reduce(or_, q_list), bd_contacto=campana.bd_contacto)
            if ids_contactos_en_curso.exists():
                contactos = contactos.exclude(id__in=list(ids_contactos_en_curso))
            serializer = ListSerializer(contactos, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los contactos de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener contactos')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
