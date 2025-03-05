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

from __future__ import unicode_literals
from django.utils.translation import gettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.audios_asterisk import AudiosAsteriskSerializer
from configuracion_telefonia_app.models import AudiosAsteriskConf


class AudiosAsteriskListView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los lenguajes de forma exitosa'),
            'languages': None}
        try:
            rutas_entrantes = AudiosAsteriskConf.objects.filter(esta_instalado=True)
            data['languages'] = AudiosAsteriskSerializer(rutas_entrantes, many=True).data
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener los lenguajes')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
