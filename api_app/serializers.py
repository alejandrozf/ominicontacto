# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from ominicontacto_app.models import Campana


class CampanaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campana
        fields = ('nombre', 'id', 'objetivo')
