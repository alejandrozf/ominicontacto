# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# APIs para visualizar wallboards

from __future__ import unicode_literals
from rest_framework import serializers
from ominicontacto_app.models import BaseDatosContacto, Campana


class CampaingsOnDBSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    campanas = serializers.SerializerMethodField()

    def get_campanas(self, obj):
        campanas = obj.campanas.all()
        return [{'id': campana.id, 'nombre': campana.nombre}
                for campana in campanas if campana.estado == Campana.ESTADO_ACTIVA]

    class Meta:
        model = BaseDatosContacto
        fields = ('id', 'nombre', 'campanas')
