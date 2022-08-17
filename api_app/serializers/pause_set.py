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
from ominicontacto_app.models import ConfiguracionDePausa, ConjuntoDePausa, Pausa


class ConjuntoDePausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConjuntoDePausa
        fields = ('id', 'nombre')


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


class OpcionesDePausaParaConjuntoSerializer(serializers.ModelSerializer):
    es_productiva = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pausa
        fields = ('id', 'nombre', 'es_productiva')

    def get_es_productiva(self, pausa):
        return pausa.es_productiva()
