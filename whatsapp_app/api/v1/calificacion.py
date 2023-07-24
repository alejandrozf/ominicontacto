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
from ominicontacto_app.models import Contacto, AgenteProfile
from ominicontacto_app.models import (
    CalificacionCliente, OpcionCalificacion, FieldFormulario, RespuestaFormularioGestion)


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    idContact = serializers.PrimaryKeyRelatedField(source='contacto', read_only=True)
    idAgente = serializers.PrimaryKeyRelatedField(
        source='agente', queryset=AgenteProfile.objects.all())
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', read_only=True)
    comments = serializers.CharField(source='observaciones')


class RetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    idContact = serializers.PrimaryKeyRelatedField(source='contacto', read_only=True)
    idAgente = serializers.PrimaryKeyRelatedField(
        source='agente', queryset=AgenteProfile.objects.all())
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', read_only=True)
    comments = serializers.CharField(source='observaciones')
    respuestaFormularioGestion = serializers.SerializerMethodField()

    def get_respuestaFormularioGestion(self, obj):
        if obj.opcion_calificacion.tipo == OpcionCalificacion.GESTION:
            return\
                RespuestaFormularioGestionSerilializer(
                    RespuestaFormularioGestion.objects.filter(calificacion=obj).last()).data
        else:
            return {}


class CreateSerializer(serializers.ModelSerializer):
    idContact = serializers.PrimaryKeyRelatedField(
        source='contacto', queryset=Contacto.objects.all())
    idAgente = serializers.PrimaryKeyRelatedField(
        source='agente', queryset=AgenteProfile.objects.all())
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', queryset=OpcionCalificacion.objects.all())
    comments = serializers.CharField(source='observaciones')

    class Meta:
        model = CalificacionCliente
        fields = [
            'id',
            'idContact',
            'idAgente',
            'idDispositionOption',
            'comments'
        ]


class UpdateSerializer(serializers.ModelSerializer):
    idAgente = serializers.PrimaryKeyRelatedField(
        source='agente', queryset=AgenteProfile.objects.all())
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', queryset=OpcionCalificacion.objects.all())
    comments = serializers.CharField(source='observaciones')

    class Meta:
        model = CalificacionCliente
        fields = [
            'id',
            'idAgente',
            'idDispositionOption',
            'comments'
        ]


class FieldFormularioSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField(source="nombre_campo")
    type = serializers.CharField(source="get_tipo_display")


class OpcionCalificacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source="nombre")
    type = serializers.CharField(source="get_tipo_display")
    form_fields = serializers.SerializerMethodField()

    def get_form_fields(self, obj):
        field_formulario = FieldFormulario.objects.filter(formulario=obj.formulario)
        FieldFormularioSerializer(field_formulario, many=True)
        return FieldFormularioSerializer(field_formulario, many=True).data


class RespuestaFormularioGestionSerilializer(serializers.Serializer):
    metadata = serializers.CharField()


class RespuestaFormularioGestionCreateSerilializer(serializers.ModelSerializer):
    metadata = serializers.CharField()

    class Meta:
        model = RespuestaFormularioGestion
        fields = [
            'id',
            'metadata'
        ]

    def to_internal_value(self, data):
        if not data['metadata']:
            raise serializers.ValidationError(
                {'Error': _('respuestaFormularioGestion es obligatorio')})
        formulario = data['formulario']
        nombres_campos = []
        campos_requeridos = []
        for campo in formulario.campos.all().values_list("nombre_campo", "is_required"):
            nombres_campos.append(campo[0])
            if campo[1]:
                campos_requeridos.append(campo[0])
        if set(data['metadata'].keys()).issubset(set(nombres_campos))\
                and set(campos_requeridos).issubset(set(data['metadata'].keys())):
            data = {
                'metadata': json.dumps(data['metadata'])
            }
        else:
            raise serializers.ValidationError({'Error': _('error en los campos del formulario')})
        return super(RespuestaFormularioGestionCreateSerilializer, self).to_internal_value(data)


class RespuestaFormularioGestionUpdateSerilializer(serializers.ModelSerializer):
    metadata = serializers.CharField()

    class Meta:
        model = RespuestaFormularioGestion
        fields = [
            'id',
            'metadata',
        ]

    def to_internal_value(self, data):
        formulario = self.instance.calificacion.opcion_calificacion.formulario
        nombres_campos = []
        campos_requeridos = []
        for campo in formulario.campos.all().values_list("nombre_campo", "is_required"):
            nombres_campos.append(campo[0])
            if campo[1]:
                campos_requeridos.append(campo[0])
        if set(data['metadata'].keys()).issubset(set(nombres_campos)):
            instance_metadata = json.loads(self.instance.metadata)
            instance_metadata.update(data['metadata'])
            data["metadata"] = json.dumps(instance_metadata)
        else:
            raise serializers.ValidationError({'Error': _('error en los campos del formulario')})
        return super(RespuestaFormularioGestionUpdateSerilializer, self).to_internal_value(data)


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def retrieve(self, request, pk):
        try:
            calificacion = CalificacionCliente.objects.get(pk=pk)
            serializer = RetrieveSerializer(calificacion)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvo las calificacion de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except CalificacionCliente.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('CalificacionCliente no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las calificacio')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            request_data = request.data.copy()
            id_user = 2  # request.user.id
            idAgente = AgenteProfile.objects.get(user__id=id_user).id
            request_data.update({'idAgente': idAgente})
            serializer_calificacion = CreateSerializer(data=request_data)
            if serializer_calificacion.is_valid():
                opcion_calificacion =\
                    serializer_calificacion.validated_data.get('opcion_calificacion')
                if opcion_calificacion.tipo == OpcionCalificacion.GESTION:
                    if 'respuestaFormularioGestion' in request_data:
                        respuestaFormularioGestion = request_data.pop('respuestaFormularioGestion')
                    else:
                        respuestaFormularioGestion = {}
                    respuesta = {
                        'metadata': respuestaFormularioGestion,
                        'formulario': opcion_calificacion.formulario
                    }
                    serializer_respuesta =\
                        RespuestaFormularioGestionCreateSerilializer(data=respuesta)
                    if serializer_respuesta.is_valid():
                        calificacion = serializer_calificacion.save()
                        serializer_respuesta.save(calificacion=calificacion)
                    else:
                        return response.Response(
                            data=get_response_data(
                                message=_('Error en los datos del formulario'),
                                errors=serializer_respuesta.errors),
                            status=status.HTTP_400_BAD_REQUEST)
                    return response.Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            message=_('Se creo la calificacion de forma exitosa'),
                            data={**serializer_calificacion.data,
                                  **{"respuestaFormularioGestion": serializer_respuesta.data}}),
                        status=status.HTTP_201_CREATED)

                else:
                    serializer_calificacion.save()
                    return response.Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            message=_('Se creo la calificacion de forma exitosa'),
                            data=serializer_calificacion.data,),
                        status=status.HTTP_201_CREATED)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer_calificacion.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(message=e),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            request_data = request.data.copy()
            id_user = 2  # request.user.id
            idAgente = AgenteProfile.objects.get(user__id=id_user).id
            request_data.update({'idAgente': idAgente})
            instance = CalificacionCliente.objects.get(pk=pk)
            serializer_calificacion = UpdateSerializer(instance, data=request.data, partial=True)
            if serializer_calificacion.is_valid():
                calificacion = serializer_calificacion.save()
                instance =\
                    RespuestaFormularioGestion.objects.filter(calificacion=calificacion).last()
                if instance and 'respuestaFormularioGestion' in request_data:
                    respuestaFormularioGestion = request_data.pop('respuestaFormularioGestion')
                    data = {
                        'metadata': respuestaFormularioGestion
                    }
                    serializer_respuesta = \
                        RespuestaFormularioGestionUpdateSerilializer(instance, data, partial=True)
                    if serializer_respuesta.is_valid():
                        serializer_respuesta.save()
                    else:
                        return response.Response(
                            data=get_response_data(
                                message=_('Error en los datos del formulario'),
                                errors=serializer_respuesta.errors),
                            status=status.HTTP_400_BAD_REQUEST)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se actualizo la calificacion de forma exitosa'),
                        data=serializer_calificacion.data),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Error en los datos'), errors=serializer_calificacion.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except CalificacionCliente.DoesNotExist:
            return response.Response(
                data=get_response_data(
                    message=_('CalificacionCliente no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al actualizar la CalificacionCliente')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True)
    def history(self, request, pk):
        try:
            calificacioncliente = CalificacionCliente.objects.get(pk=pk)
            history = calificacioncliente.history.all().order_by('-history_date')
            serializer = ListSerializer(history, many=True)
            respuesta =\
                RespuestaFormularioGestion.objects.filter(calificacion=calificacioncliente).last()
            if respuesta:
                serializer = ListSerializer(history, many=True)
                respuesta_history = respuesta.history.all().order_by('-history_date')
                serializer_respuesta =\
                    RespuestaFormularioGestionSerilializer(respuesta_history, many=True)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        data={**{"disposition_history": serializer.data},
                              **{"engaged_history": serializer_respuesta.data}}),
                    status=status.HTTP_200_OK)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener el historial de calificacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False,
                       url_path='options/(?P<campaing_id>[^/.]+)')
    def options(self, request, campaing_id):
        try:
            opciones = OpcionCalificacion.objects.filter(campana__id=campaing_id)

            serializer = OpcionCalificacionSerializer(opciones, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener opciones de calificacion')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
