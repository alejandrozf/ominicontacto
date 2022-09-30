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
from rest_framework import serializers
from ominicontacto_app.models import FieldFormulario, Formulario


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
