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

from configuracion_telefonia_app.models import DestinoEntrante, RutaEntrante
from rest_framework import serializers


class DestinoEntranteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = DestinoEntrante
        fields = ('id', 'nombre', 'tipo')


class RutaEntranteSerializer(serializers.ModelSerializer):
    destino = DestinoEntranteSerializer()

    def get_destino(self, validated_data):
        destino = validated_data.pop('destino')
        validated_data['destino'] = DestinoEntrante.objects.get(
            pk=destino['id'])

    def update(self, instance, validated_data):
        self.get_destino(validated_data)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.prefijo_caller_id = validated_data.get(
            'prefijo_caller_id', instance.prefijo_caller_id)
        instance.idioma = validated_data.get('idioma', instance.idioma)
        instance.destino = validated_data.get('destino', instance.destino)
        instance.save()
        return instance

    def create(self, validated_data):
        self.get_destino(validated_data)
        ruta = RutaEntrante.objects.create(**validated_data)
        return ruta

    class Meta:
        model = RutaEntrante
        fields = '__all__'
