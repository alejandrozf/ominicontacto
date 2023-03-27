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

import os
from rest_framework import serializers
from django.utils.translation import gettext as _
from reportes_app.models import TransferenciaAEncuestaLog

EncuestaEnCampana = None
if not os.getenv('SURVEY_VERSION', '') == '':
    from survey_app.models import EncuestaEnCampana


class TransferenciaAEncuestaLogSerializer(serializers.ModelSerializer):
    campaign_id = serializers.IntegerField(source='campana_id')
    survey_id = serializers.IntegerField(source='encuesta_id')

    class Meta:
        model = TransferenciaAEncuestaLog
        fields = ['campaign_id', 'survey_id', 'callid']

    def create(self, validated_data):
        return TransferenciaAEncuestaLog.objects.create(**validated_data)

    def validate(self, data):
        if not EncuestaEnCampana:
            raise serializers.ValidationError(
                {
                    'SYSTEM': _('Addon no instalado')
                })
        for field in ['campana_id', 'encuesta_id', 'callid']:
            if field not in data:
                raise serializers.ValidationError(
                    {
                        field: _('Parámetro requerido')
                    })
        if not EncuestaEnCampana.objects.filter(campana_id=data['campana_id'],
                                                encuesta_id=data['encuesta_id']).exists():
            raise serializers.ValidationError(
                {
                    'parameters': _('No existe una encuesta para esa campaña')
                })
        return data
