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
from ominicontacto_app.models import (
    AgenteEnContacto, AgenteEnSistemaExterno, AgenteProfile, ArchivoDeAudio,
    CalificacionCliente, Campana, ConfiguracionDePausa,
    Contacto, FieldFormulario, Formulario, Grupo,
    ConjuntoDePausa, NombreCalificacion, OpcionCalificacion,
    Pausa, SistemaExterno, SitioExterno, User, QueueMember)
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent


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


class AuditSupervisorCRUDEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user')
    object = serializers.CharField(source='content_type')
    name = serializers.CharField(source='object_repr')
    action = serializers.SerializerMethodField()
    additional_information = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='datetime', format="%Y-%m-%d %H:%M")

    class Meta:
        model = CRUDEvent
        fields = ('id', 'username', 'object', 'name', 'action', 'additional_information', 'date')

    def get_additional_information(self, obj):
        if obj.event_type == 2:
            return self.additional_information_display(obj.changed_fields)
        return '-'

    def get_action(self, obj):
        return obj.get_event_type_display()

    def additional_information_display(self, changes, colon=": ", arrow=" \u2192 ", separator="; "):
        substrings = []
        changes = json.loads(changes)
        if changes:
            for field, values in changes.items():
                substring = "{field_name:s}{colon:s}{old:s}{arrow:s}{new:s}".format(
                    field_name=field,
                    colon=colon,
                    old=values[0],
                    arrow=arrow,
                    new=values[1],
                )
                substrings.append(substring)

            return separator.join(substrings)
        return '-'


class AuditSupervisorRequestEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user')
    action = serializers.CharField(source='method')
    date = serializers.DateTimeField(source='datetime', format="%Y-%m-%d %H:%M")
    additional_information = serializers.CharField(source='url')

    class Meta:
        model = RequestEvent
        fields = ('id', 'username', 'action', 'additional_information', 'date')


class AuditSupervisorLoginEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user')
    action = serializers.SerializerMethodField()
    additional_information = serializers.CharField(source='remote_ip')
    date = serializers.DateTimeField(source='datetime', format="%Y-%m-%d %H:%M")

    class Meta:
        model = LoginEvent
        fields = ('id', 'username', 'action', 'additional_information', 'date')

    def get_action(self, obj):
        return obj.get_login_type_display()


class AgenteDeCampanaSerializer(serializers.ModelSerializer):
    agent_id = serializers.SerializerMethodField(read_only=True)
    agent_username = serializers.SerializerMethodField(read_only=True)
    agent_full_name = serializers.SerializerMethodField(read_only=True)
    agent_sip_id = serializers.SerializerMethodField(read_only=True)
    agent_penalty = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QueueMember
        fields = (
            'agent_id', 'agent_username',
            'agent_full_name', 'agent_sip_id', 'agent_penalty',)

    def get_agent_id(self, queue_member):
        return queue_member.member_id

    def get_agent_username(self, queue_member):
        return queue_member.member.user.username

    def get_agent_full_name(self, queue_member):
        return queue_member.membername

    def get_agent_sip_id(self, queue_member):
        return "SIP/{0}".format(queue_member.member.sip_extension)

    def get_agent_penalty(self, queue_member):
        return queue_member.penalty


class AgenteActivoSerializer(serializers.ModelSerializer):
    agent_id = serializers.SerializerMethodField(read_only=True)
    agent_username = serializers.SerializerMethodField(read_only=True)
    agent_full_name = serializers.SerializerMethodField(read_only=True)
    agent_sip_id = serializers.SerializerMethodField(read_only=True)
    agent_penalty = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = (
            'agent_id', 'agent_username',
            'agent_full_name', 'agent_sip_id', 'agent_penalty',)

    def get_agent_id(self, agent_profile):
        return agent_profile.id

    def get_agent_username(self, agent_profile):
        return agent_profile.user.username

    def get_agent_full_name(self, agent_profile):
        return agent_profile.user.get_full_name()

    def get_agent_sip_id(self, agent_profile):
        return "SIP/{0}".format(agent_profile.sip_extension)

    def get_agent_penalty(self, queue_member):
        return 0


class ConjuntoDePausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoDePausa
        fields = ('id', 'nombre')


class SitioExternoSerializer(serializers.ModelSerializer):

    def validarFormato(self, formato, metodo):
        if metodo == SitioExterno.GET and formato:
            raise serializers.ValidationError({
                'formato': 'Si el método es GET, no debe indicarse formato'
            })
        elif metodo == SitioExterno.POST and not formato:
            raise serializers.ValidationError({
                'formato': 'Si el método es POST, debe seleccionar un formato'
            })

    def validarObjetivo(self, objetivo, disparador, formato):
        if formato == SitioExterno.JSON and objetivo:
            raise serializers.ValidationError({
                'objetivo': 'Si el formato es JSON, '
                            'no puede haber un objetivo.'
            })
        if disparador == SitioExterno.SERVER and objetivo:
            raise serializers.ValidationError({
                'objetivo': 'Si el disparador es el servidor, '
                            'no puede haber un objetivo.'
            })
        elif disparador != SitioExterno.SERVER and not objetivo:
            raise serializers.ValidationError({
                'objetivo': 'Debe indicar un objetivo válido'
            })

    def validate(self, data):
        metodo = data['metodo']
        formato = data['formato']
        disparador = data['disparador']
        objetivo = data['objetivo']
        self.validarFormato(formato, metodo)
        self.validarObjetivo(objetivo, disparador, formato)
        if not objetivo or objetivo is None:
            data['objetivo'] = 1
        if not formato or formato is None:
            data['formato'] = 1
        return data

    class Meta:
        model = SitioExterno
        fields = (
            'id', 'nombre', 'url',
            'oculto', 'disparador', 'metodo',
            'formato', 'objetivo')


class ConfiguracionDePausaSerializer(serializers.ModelSerializer):
    pause_id = serializers.SerializerMethodField(read_only=True)
    pause_name = serializers.SerializerMethodField(read_only=True)
    pause_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ConfiguracionDePausa
        fields = (
            'id', 'time_to_end_pause', 'pause_name', 'pause_id', 'pause_type')

    def get_pause_id(self, config):
        return config.pausa.pk

    def get_pause_name(self, config):
        return config.pausa.nombre

    def get_pause_type(self, config):
        return config.pausa.get_tipo()


class PausaSerializer(serializers.ModelSerializer):
    es_productiva = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pausa
        fields = ('id', 'nombre', 'es_productiva')

    def get_es_productiva(self, pausa):
        return pausa.es_productiva()


class NombreCalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NombreCalificacion
        fields = (
            'id', 'nombre')


class AgenteProfileSistemaExternoSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = ('id', 'username', 'full_name')

    def get_username(self, agente_profile):
        return agente_profile.user.username

    def get_full_name(self, agente_profile):
        return agente_profile.user.get_full_name()


class AgenteEnSistemaExternoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    def validate(self, data):
        return data

    class Meta:
        model = AgenteEnSistemaExterno
        fields = ('id', 'id_externo_agente', 'agente')


class SistemaExternoSerializer(serializers.ModelSerializer):
    agentes = AgenteEnSistemaExternoSerializer(
        source='agentes_en_sistema', many=True)

    def validate(self, data):
        return data

    def update(self, instance, validated_data):
        agentes_en_sistema = validated_data.pop('agentes_en_sistema')
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.save()
        old_agentes_en_sistema_ids = list(
            instance.agentes_en_sistema.all().values_list('id', flat=True))
        new_agentes_en_sistema_ids = []
        for agente_en_sistema in agentes_en_sistema:
            agente_en_sistema_id = agente_en_sistema.get('id', None)
            agente_id = agente_en_sistema.get('agente')
            id_externo_agente = agente_en_sistema.get('id_externo_agente')
            if agente_en_sistema_id:
                new_agentes_en_sistema_ids.append(agente_en_sistema_id)
                item = AgenteEnSistemaExterno.objects.get(
                    id=agente_en_sistema_id, sistema_externo=instance)
                item.id_externo_agente = agente_en_sistema.get(
                    'id_externo_agente', item.id_externo_agente)
                item.save()
            else:
                AgenteEnSistemaExterno.objects.create(
                    agente=agente_id,
                    sistema_externo=instance,
                    id_externo_agente=id_externo_agente)
        diference_ids = list(
            set(old_agentes_en_sistema_ids) - set(new_agentes_en_sistema_ids))
        AgenteEnSistemaExterno.objects.filter(pk__in=diference_ids).delete()
        return instance

    def create(self, validated_data):
        agentes_en_sistema = validated_data.pop('agentes_en_sistema')
        sistema_externo = SistemaExterno.objects.create(**validated_data)
        for agente_en_sistema in agentes_en_sistema:
            agente = agente_en_sistema.get('agente')
            id_externo_agente = agente_en_sistema.get('id_externo_agente')
            AgenteEnSistemaExterno.objects.create(
                agente=agente,
                sistema_externo=sistema_externo,
                id_externo_agente=id_externo_agente)
        return sistema_externo

    class Meta:
        model = SistemaExterno
        fields = '__all__'


class FieldFormularioSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = FieldFormulario
        fields = ('id', 'nombre_campo', 'orden',
                  'tipo', 'values_select', 'is_required')


class FormularioSerializer(serializers.ModelSerializer):
    campos = FieldFormularioSerializer(many=True)
    se_puede_modificar = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        campos = validated_data.pop('campos')
        formulario = Formulario.objects.create(**validated_data)
        for campo in campos:
            FieldFormulario.objects.create(formulario=formulario, **campo)
        return formulario

    def update(self, instance, validated_data):
        campos = validated_data.pop('campos')
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get(
            'descripcion', instance.descripcion)
        instance.save()
        for campo in instance.campos.all():
            campo.orden += 1000
            campo.save()
        old_campos_ids = list(
            instance.campos.all().values_list('id', flat=True))
        new_campos_ids = []
        for campo in campos:
            campo_id = campo.get('id', None)
            nombre_campo = campo.get('nombre_campo')
            orden = campo.get('orden')
            tipo = campo.get('tipo')
            values_select = campo.get('values_select')
            is_required = campo.get('is_required')
            if campo_id:
                new_campos_ids.append(campo_id)
                item = FieldFormulario.objects.get(
                    id=campo_id, formulario=instance)
                item.nombre_campo = nombre_campo
                item.orden = orden
                item.tipo = tipo
                item.values_select = values_select
                item.is_required = is_required
                item.save()
            else:
                FieldFormulario.objects.create(
                    formulario=instance,
                    nombre_campo=nombre_campo,
                    orden=orden, tipo=tipo,
                    values_select=values_select,
                    is_required=is_required)
        diference_ids = list(
            set(old_campos_ids) - set(new_campos_ids))
        FieldFormulario.objects.filter(pk__in=diference_ids).delete()
        return instance

    class Meta:
        model = Formulario
        fields = '__all__'

    def get_se_puede_modificar(self, formulario):
        return formulario.se_puede_modificar()
