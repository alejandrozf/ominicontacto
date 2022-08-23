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
from configuracion_telefonia_app.models import (GrupoHorario, ValidacionTiempo)


class ValidacionTiempoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ValidacionTiempo
        fields = (
            'id', 'tiempo_inicial', 'tiempo_final', 'dia_semana_inicial',
            'dia_semana_final', 'dia_mes_inicio', 'dia_mes_final', 'mes_inicio', 'mes_final'
        )


class GrupoHorarioSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    validaciones_de_tiempo = ValidacionTiempoSerializer(source='validaciones_tiempo', many=True)

    def _validar_validaciones_de_tiempo(self, validaciones_de_tiempo):
        if len(validaciones_de_tiempo) == 0 or not validaciones_de_tiempo:
            raise serializers.ValidationError({
                'validaciones_de_tiempo': 'Debe existir al menos una validacion de tiempo'
            })

    def validate(self, data):
        self._validar_validaciones_de_tiempo(data['validaciones_tiempo'])
        return data

    def _actualizar_validaciones_tiempo(self, grupo_horario, validaciones_tiempo):
        actuales_ids = list(
            grupo_horario.validaciones_tiempo.values_list('id', flat=True))
        nuevos_ids = []
        for vt in validaciones_tiempo:
            vt_id = vt.get('id', None)
            if vt_id:
                nuevos_ids.append(vt_id)
                item = ValidacionTiempo.objects.get(pk=vt_id, grupo_horario=grupo_horario)
                item.tiempo_inicial = vt.get('tiempo_inicial')
                item.tiempo_final = vt.get('tiempo_final')
                item.dia_semana_inicial = vt.get('dia_semana_inicial')
                item.dia_semana_final = vt.get('dia_semana_final')
                item.dia_mes_inicio = vt.get('dia_mes_inicio')
                item.dia_mes_final = vt.get('dia_mes_final')
                item.mes_inicio = vt.get('mes_inicio')
                item.mes_final = vt.get('mes_final')
                item.save()
            else:
                ValidacionTiempo.objects.create(
                    **vt, grupo_horario=grupo_horario)
        diference_ids = list(
            set(actuales_ids) - set(nuevos_ids))
        ValidacionTiempo.objects.filter(pk__in=diference_ids).delete()

    def create(self, validated_data):
        validaciones_de_tiempo = validated_data.pop('validaciones_tiempo')
        grupo_horario = GrupoHorario.objects.create(**validated_data)
        for vt in validaciones_de_tiempo:
            ValidacionTiempo.objects.create(**vt, grupo_horario=grupo_horario)
        return grupo_horario

    def update(self, instance, validated_data):
        validaciones_tiempo = validated_data.pop('validaciones_tiempo')
        instance.nombre = validated_data.get('nombre', instance.nombre)
        self._actualizar_validaciones_tiempo(instance, validaciones_tiempo)
        instance.save()
        return instance

    class Meta:
        model = GrupoHorario
        fields = ('id', 'nombre', 'validaciones_de_tiempo')
