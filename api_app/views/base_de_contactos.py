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
from django.utils.translation import ugettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.base_de_contactos import (CampaingsOnDBSerializer)
from ominicontacto_app.models import BaseDatosContacto


class CampaingsOnDB(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron las campanas asociadas a la base de '
                         'contactos de forma exitosa'),
            'data': None}
        try:
            db = BaseDatosContacto.objects.get(pk=pk)
            data['data'] = CampaingsOnDBSerializer(db).data
            return Response(data=data, status=status.HTTP_200_OK)
        except BaseDatosContacto.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = 'No existe la base de datos de contactos'
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener las campañas asociadas a la '
                                'base de datos de contactos')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
