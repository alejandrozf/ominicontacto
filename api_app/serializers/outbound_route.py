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
from configuracion_telefonia_app.models import (
    OrdenTroncal, PatronDeDiscado, RutaSaliente, TroncalSIP)


class RutaSalienteTroncalSIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = TroncalSIP
        fields = ('id', 'nombre')


class PatronDeDiscadoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = PatronDeDiscado
        fields = ('id', 'prepend', 'prefix',
                  'match_pattern')


class OrdenTroncalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = OrdenTroncal
        fields = ('id', 'troncal')


class RutaSalienteSerializer(serializers.ModelSerializer):
    patrones_de_discado = PatronDeDiscadoSerializer(many=True)
    troncales = OrdenTroncalSerializer(source='secuencia_troncales', many=True)

    def _validar_patrones_de_discado(self, patrones_de_discado):
        if len(patrones_de_discado) == 0 or not patrones_de_discado:
            raise serializers.ValidationError({
                'patrones_de_discado': 'Debe existir al menos un patron de discado'
            })

        patrones = []
        for patron in patrones_de_discado:
            prefix = patron['prefix'] if 'prefix' in patron.keys() else None
            match_pattern = patron['match_pattern'] if 'match_pattern' in patron.keys() else None
            if (prefix, match_pattern) in patrones:
                raise serializers.ValidationError({
                    'patrones_de_discado': 'Los patrones de discado deben ser diferentes'
                })
            patrones.append((prefix, match_pattern))

    def _validar_secuencia_de_troncales(self, troncales):
        if len(troncales) == 0 or not troncales:
            raise serializers.ValidationError({
                'troncales': 'Debe existir al menos una troncal'
            })

        troncales_ids = []
        for ordenTroncal in troncales:
            troncal_id = ordenTroncal['troncal'] if 'troncal' in ordenTroncal.keys() else None
            if troncal_id in troncales_ids:
                raise serializers.ValidationError({
                    'troncales': 'Las troncales deben ser diferentes'
                })
            troncales_ids.append(troncal_id)

    def validate(self, data):
        self._validar_secuencia_de_troncales(data['secuencia_troncales'])
        self._validar_patrones_de_discado(data['patrones_de_discado'])
        return data

    def _asignar_orden_en_troncales(self, ruta_saliente, troncales):
        if not ruta_saliente.secuencia_troncales.exists():
            max_orden = 0
        else:
            max_orden = ruta_saliente.secuencia_troncales.last().orden
        for i, troncal in enumerate(troncales, max_orden + 1):
            troncal['orden'] = i

    def _asignar_orden_en_patrones_de_discado(self, ruta_saliente, patrones_de_discado):
        if not ruta_saliente.patrones_de_discado.exists():
            max_orden = 0
        else:
            max_orden = ruta_saliente.patrones_de_discado.last().orden
        for i, patron_de_discado in enumerate(patrones_de_discado, max_orden + 1):
            patron_de_discado['orden'] = i

    def _actualizar_patrones_de_discado(self, ruta_saliente, patrones_de_discado):
        self._asignar_orden_en_patrones_de_discado(ruta_saliente, patrones_de_discado)
        actuales_patrones_de_discado_ids = list(
            ruta_saliente.patrones_de_discado.values_list('id', flat=True))
        nuevos_patrones_de_discado_ids = []
        for patron_de_discado in patrones_de_discado:
            pd_id = patron_de_discado.get('id', None)
            prepend = patron_de_discado.get('prepend')
            prefix = patron_de_discado.get('prefix')
            match_pattern = patron_de_discado.get('match_pattern')
            orden = patron_de_discado.get('orden')
            if pd_id:
                nuevos_patrones_de_discado_ids.append(pd_id)
                item = PatronDeDiscado.objects.get(pk=pd_id, ruta_saliente=ruta_saliente)
                item.prepend = prepend
                item.prefix = prefix
                item.match_pattern = match_pattern
                item.orden = orden
                item.save()
            else:
                PatronDeDiscado.objects.create(
                    **patron_de_discado, ruta_saliente=ruta_saliente)
        diference_ids = list(
            set(actuales_patrones_de_discado_ids) - set(nuevos_patrones_de_discado_ids))
        PatronDeDiscado.objects.filter(pk__in=diference_ids).delete()

    def _actualizar_troncales(self, ruta_saliente, troncales):
        self._asignar_orden_en_troncales(ruta_saliente, troncales)
        actuales_troncales_ids = list(
            ruta_saliente.secuencia_troncales.values_list('id', flat=True))
        nuevos_troncales_ids = []
        for orden_troncal in troncales:
            orden_id = orden_troncal.get('id', None)
            troncal = orden_troncal.get('troncal')
            orden = orden_troncal.get('orden')
            if orden_id:
                nuevos_troncales_ids.append(orden_id)
                item = OrdenTroncal.objects.get(pk=orden_id, ruta_saliente=ruta_saliente)
                item.troncal = troncal
                item.orden = orden
                item.save()
            else:
                OrdenTroncal.objects.create(
                    **orden_troncal, ruta_saliente=ruta_saliente)
        diference_ids = list(
            set(actuales_troncales_ids) - set(nuevos_troncales_ids))
        OrdenTroncal.objects.filter(pk__in=diference_ids).delete()

    def create(self, validated_data):
        patrones_de_discado = validated_data.pop('patrones_de_discado')
        troncales = validated_data.pop('secuencia_troncales')
        ruta_saliente = RutaSaliente.objects.create(**validated_data)
        self._asignar_orden_en_troncales(ruta_saliente, troncales)
        self._asignar_orden_en_patrones_de_discado(ruta_saliente, patrones_de_discado)
        for troncal in troncales:
            OrdenTroncal.objects.create(**troncal, ruta_saliente=ruta_saliente)
        for patron_de_discado in patrones_de_discado:
            PatronDeDiscado.objects.create(**patron_de_discado, ruta_saliente=ruta_saliente)
        return ruta_saliente

    def update(self, instance, validated_data):
        patrones_de_discado = validated_data.pop('patrones_de_discado')
        troncales = validated_data.pop('secuencia_troncales')
        self._actualizar_patrones_de_discado(instance, patrones_de_discado)
        self._actualizar_troncales(instance, troncales)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.ring_time = validated_data.get('ring_time', instance.ring_time)
        instance.dial_options = validated_data.get('dial_options', instance.dial_options)
        instance.save()
        return instance

    class Meta:
        model = RutaSaliente
        fields = ('id', 'nombre', 'ring_time', 'dial_options', 'patrones_de_discado', 'troncales')
