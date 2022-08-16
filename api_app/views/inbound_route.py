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
from django.utils.translation import ugettext as _
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers import (
    RutaEntranteSerializer, DestinoEntranteSerializer)
from configuracion_telefonia_app.models import DestinoEntrante, RutaEntrante
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionRutaEntranteAsterisk,
    RestablecerConfiguracionTelefonicaError)


class InboundRouteList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron las rutas entrantes '
                         'de forma exitosa'),
            'inboundRoutes': []}
        try:
            rutas_entrantes = RutaEntrante.objects.all().order_by('id')
            data['inboundRoutes'] = [
                RutaEntranteSerializer(r).data for r in rutas_entrantes]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener las rutas entrantes')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InboundRouteCreate(APIView):
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
                'message': _('Se creo la ruta entrante '
                             'de forma exitosa')}
            ruta_entrante = RutaEntranteSerializer(data=request.data)
            if ruta_entrante.is_valid():
                ruta_entrante.save()
                return Response(data=responseData, status=status.HTTP_200_OK)
            else:
                responseData['status'] = 'ERROR'
                responseData['message'] = [
                    ruta_entrante.errors[key] for key in ruta_entrante.errors]
                responseData['errors'] = ruta_entrante.errors
                return Response(
                    data=responseData, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            responseData['status'] = 'ERROR'
            responseData['message'] = _('Error al crear la ruta entrante')
            return Response(
                data=responseData,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InboundRouteUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'errors': {},
            'message': _('Se actualizo la ruta entrante '
                         'de forma exitosa')}
        try:
            ruta_entrante = RutaEntrante.objects.get(pk=pk)
            serializer = RutaEntranteSerializer(
                ruta_entrante, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = [
                    serializer.errors[key] for key in serializer.errors]
                data['errors'] = serializer.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except RutaEntrante.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe la ruta entrante '
                                'que se quiere actualizar')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'la ruta entrante')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InboundRouteDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion de la '
                         'ruta entrante de forma exitosa'),
            'inboundRoute': None}
        try:
            ruta_entrante = RutaEntrante.objects.get(pk=pk)
            data['inboundRoute'] = RutaEntranteSerializer(ruta_entrante).data
            return Response(data=data, status=status.HTTP_200_OK)
        except RutaEntrante.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('No existe la ruta entrante '
                                'para obtener el detalle')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el detalle '
                                'de la ruta entrante')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InboundRouteDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino la ruta entrante '
                         'de forma exitosa')}
        try:
            ruta_entrante = RutaEntrante.objects.get(pk=pk)
            if ruta_entrante.destino.tipo == 1 \
                    and ruta_entrante.destino.content_object.outr:
                data['status'] = 'ERROR'
                data['message'] = _('No está permitido eliminar una '
                                    'Ruta Entrante asociada con una campaña '
                                    'que tiene una Ruta Saliente.')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                sincronizador = SincronizadorDeConfiguracionRutaEntranteAsterisk()
                sincronizador.eliminar_y_regenerar_asterisk(ruta_entrante)
                ruta_entrante.delete()
            return Response(data=data, status=status.HTTP_200_OK)
        except RutaEntrante.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la ruta entrante')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except RestablecerConfiguracionTelefonicaError as e:
            data['status'] = 'ERROR'
            data['message'] = _('Error al eliminar la '
                                'ruta entrante: {0}'.format(e))
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar la ruta entrante')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InboundRouteDestinations(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion de los '
                         'destinos de forma exitosa'),
            'inboundRoutesDestinations': {
                '1': None,
                '2': None,
                '3': None,
                '5': None,
                '9': None,
                '7': None
            }
        }
        try:
            for k, v in DestinoEntrante.TIPOS_DESTINOS:
                destinos = DestinoEntrante.get_destinos_por_tipo(k)
                data['inboundRoutesDestinations'][str(k)] = [
                    DestinoEntranteSerializer(d).data for d in destinos]
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener los destinos '
                                'de las rutas entrantes')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
