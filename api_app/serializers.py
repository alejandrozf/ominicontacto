# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from ominicontacto_app.models import Campana, AgenteProfile


class CampanaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campana
        fields = ('nombre', 'id', 'objetivo')


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.get_full_name()


class AgenteProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserRelatedField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = ('id', 'user')
