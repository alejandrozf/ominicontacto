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

import json

from django.forms import ValidationError

from rest_framework import serializers

from ominicontacto_app.forms import FormularioNuevoContacto
from ominicontacto_app.models import AgenteEnContacto, AgenteProfile, ArchivoDeAudio, \
    CalificacionCliente, Campana, Contacto, Grupo, OpcionCalificacion, User
from auditlog.models import LogEntry


class CalificacionClienteSerializerMixin(object):

    error_dict = {
        'status': 'ERROR',
        'msg': 'There is another disposition for this contact on this campaign'
    }

    def create(self, validated_data):
        try:
            return super(CalificacionClienteSerializerMixin, self).create(validated_data)
        except ValidationError:
            raise serializers.ValidationError(self.error_dict)

    def update(self, instance, validated_data):
        try:
            return super(CalificacionClienteSerializerMixin, self).update(instance, validated_data)
        except ValidationError:
            raise serializers.ValidationError(self.error_dict)


class CampanaSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: Pasar al inglés
    class Meta:
        model = Campana
        fields = ('nombre', 'id', 'objetivo')


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.get_full_name()


class AgenteProfileIDSerializer(serializers.HyperlinkedModelSerializer):
    user = UserRelatedField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = ('id', 'user')


class AgenteProfileNameSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    group = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = ('id', 'username', 'full_name', 'group')

    def get_username(self, agente_profile):
        return agente_profile.user.username

    def get_full_name(self, agente_profile):
        return agente_profile.user.get_full_name()

    def get_group(self, agente_profile):
        return agente_profile.grupo_id


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserSigninSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password')


class OpcionCalificacionSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='nombre')
    hidden = serializers.BooleanField(source='oculta')

    class Meta:
        model = OpcionCalificacion
        fields = ('id', 'name', 'hidden')


class CalificacionClienteSerializer(
        CalificacionClienteSerializerMixin, serializers.ModelSerializer):

    idContact = serializers.PrimaryKeyRelatedField(source='contacto', read_only=True)
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', read_only=True)
    comments = serializers.CharField(source='observaciones')

    class Meta:
        model = CalificacionCliente
        fields = ('id', 'idContact', 'callid', 'idDispositionOption', 'comments')

    def to_internal_value(self, data):
        request = self.context['request']
        id_sistema_externo = data.get('idExternalSystem')
        id_contacto = data.get('idContact')
        observaciones = data.get('comments', '')
        id_opcion_calificacion = data.get('idDispositionOption')
        try:
            id_opcion_calificacion = int(id_opcion_calificacion)
            if self.instance and self.instance.opcion_calificacion.id == id_opcion_calificacion:
                opcion_calificacion = self.instance.opcion_calificacion
            else:
                opcion_calificacion = OpcionCalificacion.objects.filter(
                    pk=id_opcion_calificacion, oculta=False).first()
        except ValueError:
            opcion_calificacion = None

        if opcion_calificacion is None:
            errors = {
                'status': 'ERROR',
                'idDispositionOption': 'Disposition option id not found'
            }
            raise serializers.ValidationError(errors)
        agente = request.user.agenteprofile
        contacto = None
        if id_sistema_externo is None:
            # se asume que el id de contacto es "interno"
            contacto = opcion_calificacion.campana.bd_contacto.contactos.filter(
                pk=id_contacto).first()
        elif id_contacto is not None:
            # el id de contacto lo identifica en un sistema externo
            contacto = opcion_calificacion.campana.bd_contacto.contactos.filter(
                id_externo=id_contacto).first()
        if contacto is None:
            errors = {
                'status': 'ERROR',
                'idContact': 'Contact id not found'
            }
            raise serializers.ValidationError(errors)
        return {
            'contacto': contacto,
            'agente': agente,
            'observaciones': observaciones,
            'opcion_calificacion': opcion_calificacion,
            'callid': data.get('callid')
        }


class ContactoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contacto
        fields = '__all__'

    def create(self, validated_data):
        id_externo = validated_data.get('id_externo')
        if id_externo != '' and id_externo is not None:
            base_datos = validated_data.get('bd_contacto')
            contacto_con_id_externo = base_datos.contactos.filter(id_externo=id_externo)
            if contacto_con_id_externo.exists():
                errors = {
                    'status': 'ERROR',
                    'idExternalContact':
                        'There is another contact with this external id on this database'}
                raise serializers.ValidationError(errors)
        return super(ContactoSerializer, self).create(validated_data)


class CalificacionClienteNuevoContactoSerializer(
        CalificacionClienteSerializerMixin, serializers.ModelSerializer):
    idDispositionOption = serializers.PrimaryKeyRelatedField(
        source='opcion_calificacion', read_only=True)
    comments = serializers.CharField(source='observaciones')

    class Meta:
        model = CalificacionCliente
        fields = ('id', 'callid', 'idDispositionOption', 'comments')

    def to_internal_value(self, data):
        request = self.context['request']
        telefono = data.get('phone', None)
        id_externo = data.get('idExternalContact')
        if id_externo == '':
            # porque el modelo no admite valores en blanco
            # pero sí nulos
            id_externo = None
        id_opcion_calificacion = data.get('idDispositionOption')
        observaciones = data.get('comments', '')
        opcion_calificacion = OpcionCalificacion.objects.filter(
            oculta=False, pk=id_opcion_calificacion).first()
        if opcion_calificacion is None:
            errors = {
                'status': 'ERROR',
                'idDispositionOption': 'Disposition option id not found'
            }
            raise serializers.ValidationError(errors)
        agente = request.user.agenteprofile
        campana = opcion_calificacion.campana
        bd_contacto = campana.bd_contacto
        # obtenemos los campos de la BD del contacto
        metadata = bd_contacto.get_metadata()
        campos_contacto = metadata.nombres_de_columnas_de_datos

        datos = []
        for nombre in bd_contacto.get_metadata().nombres_de_columnas_de_datos:
            campo = data.get(FormularioNuevoContacto.get_nombre_input(nombre))
            datos.append(campo)
        datos_contacto_json = json.dumps(datos)
        tmp_data = data.copy()
        tmp_data['datos'] = datos_contacto_json
        tmp_data['telefono'] = telefono
        tmp_data['bd_contacto'] = bd_contacto.pk
        tmp_data['id_externo'] = id_externo

        contacto_serializer = ContactoSerializer(data=tmp_data)
        if contacto_serializer.is_valid():
            contacto = contacto_serializer.save()
            if campana.type == Campana.TYPE_PREVIEW:
                # se registra la asignacion del agente al contacto
                agente_en_contacto = campana._crear_agente_en_contacto(
                    contacto, agente.pk, campos_contacto,
                    estado=AgenteEnContacto.ESTADO_ASIGNADO, orden=1)
                agente_en_contacto.save()
        else:
            errors = {
                'status': 'ERROR',
                'contacto': 'Contact data is invalid'
            }
            raise serializers.ValidationError(errors)
        return {
            'contacto': contacto,
            'agente': agente,
            'observaciones': observaciones,
            'opcion_calificacion': opcion_calificacion,
            'callid': data.get('callid')
        }


class AudioSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ArchivoDeAudio
        fields = ('id', 'name')

    def get_name(self, audio):
        return audio.__str__()


class GrupoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nombre')

    class Meta:
        model = Grupo
        fields = ('id', 'name')


class AuditSupervisorSerializer(serializers.ModelSerializer):
    actor = serializers.CharField()
    object = serializers.CharField(source='content_type')
    name = serializers.CharField(source='object_repr')
    action = serializers.CharField(source='get_action_display')
    date = serializers.DateTimeField(source='timestamp', format="%Y-%m-%d %H:%M")
    changes = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ('id', 'actor', 'object', 'name', 'action', 'changes', 'date')

    def get_changes(self, obj):
        if obj.action == 1:
            return obj.changes_str
        return '-'
