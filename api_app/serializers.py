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

from __future__ import unicode_literals

from rest_framework import serializers

from ominicontacto_app.models import Campana, AgenteProfile, User, OpcionCalificacion


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


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserSigninSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password')


class OpcionCalificacionSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='nombre')

    class Meta:
        model = OpcionCalificacion
        fields = ('id', 'name')
