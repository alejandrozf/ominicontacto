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
from ominicontacto_app.models import SitioExterno


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
