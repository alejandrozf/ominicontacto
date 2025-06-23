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

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML

from configuracion_telefonia_app.models import DestinoEntrante


class DestinoEntranteView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, type):
        try:
            destinos = DestinoEntrante.objects.\
                filter(tipo=type).values('id', 'nombre')
            data = {'destinations': list(destinos)}
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DestinoEntranteTiposView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        try:
            # quitar cuando se habiliten el resto tipos de dedestinos
            custom = DestinoEntrante.CUSTOM_DST
            lista_temp = filter(lambda tipo: tipo[0] == custom, DestinoEntrante.TIPOS_DESTINOS)
            destinations_types = [{'type': x, 'name': y} for x, y in lista_temp]
            data = {'destinations_types': destinations_types}
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
