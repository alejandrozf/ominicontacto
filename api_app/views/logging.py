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

from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from api_app.authentication import ExpiringTokenAuthentication
from api_app.serializers.reportes import TransferenciaAEncuestaLogSerializer
from api_app.views.permissions import TienePermisoOML


class TransferenciaAEncuestaLogCreateView(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        try:
            responseData = {
                'status': 'SUCCESS',
                'errors': {},
                'message': _('Se creo el Log de transferencia a Encuesta')}
            agente = self.request.user.get_agente_profile()
            serializer = TransferenciaAEncuestaLogSerializer(data=request.data)
            if not serializer.is_valid():
                responseData['status'] = 'ERROR'
                responseData['message'] = [
                    serializer.errors[key] for key in serializer.errors]
                responseData['errors'] = serializer.errors
                return Response(
                    data=responseData, status=status.HTTP_400_BAD_REQUEST)

            # Ver si agente esta asignado a la campaña? Y si lo desasignan durante la llamada?
            transferencia = serializer.save()
            transferencia.agente_id = agente.id
            transferencia.save()
            return Response(data=responseData, status=status.HTTP_200_OK)

        except Exception:
            responseData['status'] = 'ERROR'
            responseData['message'] = _('Error al crear el Log de transferencia')
            return Response(
                data=responseData,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
