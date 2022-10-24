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
from rest_framework import serializers
from ominicontacto_app.models import AgenteProfile, QueueMember


class AgenteDeCampanaSerializer(serializers.ModelSerializer):
    agent_id = serializers.SerializerMethodField(read_only=True)
    agent_username = serializers.SerializerMethodField(read_only=True)
    agent_full_name = serializers.SerializerMethodField(read_only=True)
    agent_sip_id = serializers.SerializerMethodField(read_only=True)
    agent_penalty = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QueueMember
        fields = (
            'agent_id', 'agent_username',
            'agent_full_name', 'agent_sip_id', 'agent_penalty',)

    def get_agent_id(self, queue_member):
        return queue_member.member_id

    def get_agent_username(self, queue_member):
        return queue_member.member.user.username

    def get_agent_full_name(self, queue_member):
        return queue_member.membername

    def get_agent_sip_id(self, queue_member):
        return "SIP/{0}".format(queue_member.member.sip_extension)

    def get_agent_penalty(self, queue_member):
        return queue_member.penalty


class AgenteActivoSerializer(serializers.ModelSerializer):
    agent_id = serializers.SerializerMethodField(read_only=True)
    agent_username = serializers.SerializerMethodField(read_only=True)
    agent_full_name = serializers.SerializerMethodField(read_only=True)
    agent_sip_id = serializers.SerializerMethodField(read_only=True)
    agent_penalty = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AgenteProfile
        fields = (
            'agent_id', 'agent_username',
            'agent_full_name', 'agent_sip_id', 'agent_penalty',)

    def get_agent_id(self, agent_profile):
        return agent_profile.id

    def get_agent_username(self, agent_profile):
        return agent_profile.user.username

    def get_agent_full_name(self, agent_profile):
        return agent_profile.user.get_full_name()

    def get_agent_sip_id(self, agent_profile):
        return "SIP/{0}".format(agent_profile.sip_extension)

    def get_agent_penalty(self, queue_member):
        return 0
