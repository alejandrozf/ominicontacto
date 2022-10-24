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
from rest_framework import serializers
from ominicontacto_app.models import AgenteEnSistemaExterno, AgenteProfile, SistemaExterno


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
