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
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from facebook_meta_app.api.permissions import TienePermisoCanalFacebookAgente
from facebook_meta_app.api.utils import HttpResponseStatus, get_response_data

from ominicontacto_app.models import Campana, Contacto
from ominicontacto_app.models import TelephoneValidator
from facebook_meta_app.models import ConversationMessengerMetaApp


MAX_SEARCH_RESULTS = 20


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(source='telefono')
    page_client_id = serializers.CharField(source='facebook', required=False)
    data = serializers.SerializerMethodField()
    disposition = serializers.SerializerMethodField()

    def get_disposition(self, obj):
        disposition = obj.calificacioncliente_set.last()
        return disposition.id if disposition else None

    def get_data(self, obj):
        return obj.obtener_datos()


class RetriveSerializer(serializers.ModelSerializer):
    page_client_id = serializers.CharField(source='facebook', required=False)

    class Meta:
        model = Contacto
        fields = [
            'id',
            'telefono',
            'facebook',
            'datos',
            'bd_contacto',
        ]


class CreateSerializer(serializers.ModelSerializer):
    page_client_id = serializers.CharField(source='facebook', required=False)

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
            'page_client_id',
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

    def validar_page_client_id(self, field, value):
        if not value:
            raise serializers.ValidationError({field: _('campo requerido')})
        return value

    def get_datos_json(self, data):
        datos = []
        metadata = self.campana.bd_contacto.get_metadata()
        for field in metadata.nombres_de_columnas_de_datos:
            if data.get(field, '') and self.es_campo_telefonico(field):
                try:
                    TelephoneValidator(data.get(field))
                except ValidationError as error:
                    raise serializers.ValidationError({field: error.message})
            campo = data.get(field, '')
            datos.append(campo if campo else "")
        return json.dumps(datos)

    def to_internal_value(self, data):
        mandatory = list(self.campana.get_campos_obligatorios())
        metadata = self.campana.bd_contacto.get_metadata()
        campos_bd = metadata.nombres_de_columnas
        telefono = metadata.nombre_campo_telefono
        if telefono in data['datos']:
            telefono_val = data['datos'].pop(telefono)
            data['telefono'] = self.validar_telefono(telefono, telefono_val)
        else:
            data['telefono'] = ''
            mandatory = [field for field in mandatory if field != telefono]
        if 'page_client_id' in data['datos']:
            page_client_id_val = data['datos'].pop('page_client_id')
            data['page_client_id'] =\
                self.validar_page_client_id('page_client_id', page_client_id_val)
        # else:
        #     raise serializers.ValidationError({'page_client_id': _('campo requerido')})

        if set(data['datos'].keys()).issubset(set(campos_bd)):
            if set(data['datos'].keys()).issuperset(set(mandatory)):
                data['datos'] = self.get_datos_json(data['datos'])
            else:
                raise serializers.ValidationError({'Error': _('Faltan campos requeridos')})
        else:
            raise serializers.ValidationError({'Error': _('Error en los campos de contacto')})
        return super(CreateSerializer, self).to_internal_value(data)


class UpdateSerializer(serializers.ModelSerializer):
    page_client_id = serializers.CharField(source='facebook', required=True)

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
            'page_client_id',
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

    def validar_page_client_id(self, field, value):
        if not value:
            raise serializers.ValidationError({field: _('campo requerido')})
        return value

    def get_datos_json(self, data):
        datos = []
        metadata = self.campana.bd_contacto.get_metadata()
        for field in metadata.nombres_de_columnas_de_datos:
            if data.get(field, '') and self.es_campo_telefonico(field):
                try:
                    TelephoneValidator(data.get(field))
                except ValidationError as error:
                    raise serializers.ValidationError({field: error.message})
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
        else:
            data['telefono'] = self.instance.telefono
        if 'page_client_id' in data['datos']:
            page_client_id_val = data['datos'].pop('page_client_id')
            data['page_client_id'] = self.validar_page_client_id(
                'page_client_id', page_client_id_val)
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
    permission_classes = [TienePermisoCanalFacebookAgente]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def _contact_queryset(self, campana):
        return Contacto.objects.filter(
            bd_contacto=campana.bd_contacto
        ).select_related('bd_contacto')

    def _active_contact_ids(self, campana, exclude_conversation_id=None):
        conversations = ConversationMessengerMetaApp.objects.filter(
            is_disposition=False,
            campana_id=campana.pk,
            client_id__isnull=False,
        )
        if exclude_conversation_id:
            conversations = conversations.exclude(pk=exclude_conversation_id)
        return conversations.values_list('client_id', flat=True)

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
                message=_('Se obtuvieron los contactos de forma exitosa'),
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
            conversation = ConversationMessengerMetaApp.objects.get(id=conversacion_pk)
            if 'page_client_id' not in request_data and conversation.page_client_id:
                request_data['page_client_id'] = conversation.page_client_id
            data = {
                "bd_contacto": campana.bd_contacto.id,
                "datos": request_data
            }
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
            else:
                print(serializer.errors)
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
    def suggest_match(self, request, campana_pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            conversation_id = request.data.get('conversation_id')
            if not conversation_id:
                return response.Response(
                    data=get_response_data(
                        message=_('Conversación requerida')),
                    status=status.HTTP_400_BAD_REQUEST)
            conversation = ConversationMessengerMetaApp.objects.only(
                'id', 'page_client_id'
            ).get(id=conversation_id)
            if not conversation.page_client_id:
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Sin coincidencia sugerida'),
                        data=None),
                    status=status.HTTP_200_OK)
            active_contact_ids = self._active_contact_ids(
                campana, exclude_conversation_id=conversation.pk)
            queryset = self._contact_queryset(campana).filter(
                facebook=conversation.page_client_id
            ).exclude(id__in=list(active_contact_ids))
            contact = queryset.only(
                'id', 'telefono', 'facebook', 'datos', 'bd_contacto_id',
                'bd_contacto__metadata'
            ).first()
            serializer = ListSerializer(contact) if contact else None
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvo la coincidencia sugerida'),
                    data=serializer.data if serializer else None),
                status=status.HTTP_200_OK)
        except ConversationMessengerMetaApp.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('Conversación no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener coincidencia sugerida')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=["post"])
    def search(self, request, campana_pk):
        try:
            campana = Campana.objects.get(id=campana_pk)
            search = (request.data.get('search') or '').strip()
            phone = (request.data.get('phone') or '').strip()
            name = (request.data.get('name') or '').strip()
            conversation_id = request.data.get('conversation_id')
            try:
                limit = int(request.data.get('limit', MAX_SEARCH_RESULTS))
            except (TypeError, ValueError):
                limit = MAX_SEARCH_RESULTS
            limit = max(1, min(limit, 50))

            active_contact_ids = list(
                self._active_contact_ids(
                    campana, exclude_conversation_id=conversation_id))
            base_queryset = self._contact_queryset(campana)
            if active_contact_ids:
                base_queryset = base_queryset.exclude(id__in=active_contact_ids)

            candidate_terms = [term for term in [search, phone, name] if term]
            if not candidate_terms:
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se obtuvieron los contactos de forma exitosa'),
                        data=[]),
                    status=status.HTTP_200_OK)
            filters = Q()
            for term in candidate_terms:
                filters |= (
                    Q(telefono__icontains=term) |
                    Q(facebook__icontains=term) |
                    Q(id_externo__icontains=term) |
                    Q(datos__icontains=term)
                )

            contactos = base_queryset.filter(filters).only(
                'id', 'telefono', 'facebook', 'datos', 'bd_contacto_id',
                'bd_contacto__metadata'
            ).distinct()[:limit]
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
