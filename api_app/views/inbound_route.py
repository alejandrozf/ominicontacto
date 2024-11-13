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
import json
from django.utils.translation import gettext as _
from api_app.utils.routes.inbound import (
    eliminar_ruta_entrante_config, escribir_ruta_entrante_config)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.inbound_route import (
    RutaEntranteSerializer, DestinoEntranteSerializer)
from configuracion_telefonia_app.models import DestinoEntrante, RutaEntrante


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
            data = {
                'status': 'SUCCESS',
                'errors': {},
                'message': _('Se creo la ruta entrante '
                             'de forma exitosa')}
            serializador = RutaEntranteSerializer(data=request.data)
            if serializador.is_valid():
                ruta_entrante = serializador.save()
                if not escribir_ruta_entrante_config(self, ruta_entrante):
                    data['message'] = _('Se creo la ruta entrante pero no se pudo '
                                        'cargar la configuración telefónica')
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = json.dumps(serializador.errors)
                data['errors'] = serializador.errors
                return Response(
                    data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al crear la ruta entrante')
            return Response(
                data=data,
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
                delete_st = eliminar_ruta_entrante_config(self, ruta_entrante)
                serializer.save()
                create_st = escribir_ruta_entrante_config(self, ruta_entrante)
                if not delete_st or not create_st:
                    data['message'] = _('Se actualizo la ruta entrante pero no se pudo '
                                        'cargar la configuración telefónica')
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data['status'] = 'ERROR'
                data['message'] = json.dumps(serializer.errors)
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
                if not eliminar_ruta_entrante_config(self, ruta_entrante):
                    data['message'] = _('Se actualizo la ruta entrante pero no se pudo '
                                        'cargar la configuración telefónica')
                ruta_entrante.delete()
                return Response(data=data, status=status.HTTP_200_OK)
        except RutaEntrante.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la ruta entrante')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
                '11': None,
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
