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
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets
from api_app.serializers import AudioSerializer
from ominicontacto_app.models import ArchivoDeAudio


class ListadoAudiosView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    serializer_class = AudioSerializer

    def get_queryset(self):
        return ArchivoDeAudio \
            .objects \
            .all() \
            .exclude(borrado=True)
