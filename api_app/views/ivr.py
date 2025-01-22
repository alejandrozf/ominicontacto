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
from api_app.utils import HttpResponseStatus, get_response_data
from api_app.utils.ivr import (
    eliminar_nodo_ivr_config, eliminar_nodos_y_asociaciones, escribir_nodo_ivr_config)
from ominicontacto_app.models import ArchivoDeAudio
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.serializers.ivr import (
    AudioOptionsSerializer, DestinationTypesSerializer,
    IVRCreateSerializer, IVRSerializer)
from configuracion_telefonia_app.models import IVR, DestinoEntrante

EMPTY_CHOICE = (None, '---------')


class IVRList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        try:
            ivrs = IVR.objects.all().order_by('id')
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los IVRs de forma exitosa'),
                    data=[IVRSerializer(ivr).data for ivr in ivrs]),
                status=status.HTTP_200_OK)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al obtener los ivrs')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRCreate(APIView):
    permission_classes = (TienePermisoOML, )
    parser_classes = (MultiPartParser, FormParser, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request, format=None):
        try:
            req_data = request.data.copy()
            for key in req_data:
                if req_data[key] == 'null':
                    req_data[key] = None
            req_data['destination_options_json'] = req_data['destination_options']
            serializer = IVRCreateSerializer(data=req_data)
            if serializer.is_valid():
                ivr = serializer.save()
                msg = _('Se creo el IVR de forma exitosa')
                if not escribir_nodo_ivr_config(self, ivr):
                    msg = _('Se creo el IVR pero no se pudo '
                            'cargar la configuración telefónica')
                return Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=msg,
                        data=IVRSerializer(ivr).data),
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    data=get_response_data(
                        message=_('Error en los datos enviados'),
                        errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al crear el IVR')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    parser_classes = (MultiPartParser, FormParser, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk, format=None):
        try:
            ivr = IVR.objects.get(pk=pk)
            req_data = request.data.copy()
            for key in req_data:
                if req_data[key] == 'null':
                    req_data[key] = None
            req_data['destination_options_json'] = req_data['destination_options']
            serializer = IVRCreateSerializer(ivr, data=req_data)
            if serializer.is_valid():
                ivr = serializer.save()
                msg = _('Se actualizo el IVR de forma exitosa')
                nodo = DestinoEntrante.get_nodo_ruta_entrante(ivr)
                nodo.nombre = ivr.nombre
                nodo.save()
                if not escribir_nodo_ivr_config(self, ivr):
                    msg = _('Se actualizo el IVR pero no se pudo '
                            'cargar la configuración telefónica')
                return Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=msg,
                        data=IVRSerializer(ivr).data),
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    data=get_response_data(
                        message=_('Error en los datos enviados'),
                        errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except IVR.DoesNotExist:
            return Response(
                data=get_response_data(
                    message=_('No existe el IVR')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al actualizar el IVR')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRDetail(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        try:
            ivr = IVR.objects.get(pk=pk)
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvo la informacion del IVR de forma exitosa'),
                    data=IVRSerializer(ivr).data),
                status=status.HTTP_200_OK)
        except IVR.DoesNotExist:
            return Response(
                data=get_response_data(
                    message=_('No existe el IVR')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al obtener el detalle del IVR')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        try:
            ivr = IVR.objects.get(pk=pk)
            nodo = DestinoEntrante.get_nodo_ruta_entrante(ivr)
            permitido_eliminar = True
            if nodo.es_destino_en_flujo_de_llamada():
                permitido_eliminar = False
                msg = _('No se puede eliminar un objeto que es destino en un flujo de llamada.')
            elif nodo.es_destino_failover():
                permitido_eliminar = False
                campanas_failover = nodo.campanas_destino_failover.values_list('nombre', flat=True)
                msg = _(
                    'No se puede eliminar la campaña.'
                    'Es usada como destino failover de las campañas:'
                    ' {0}').format(",".join(campanas_failover))
            if not permitido_eliminar:
                return Response(
                    data=get_response_data(
                        message=_('Error en los datos enviados'),
                        errors=msg),
                    status=status.HTTP_400_BAD_REQUEST)
            msg = _('Se elimino el IVR de forma exitosa')
            if not eliminar_nodo_ivr_config(self, ivr):
                msg = _('Se elimino el IVR pero no se pudo '
                        'cargar la configuración telefónica')
            eliminar_nodos_y_asociaciones(self, ivr)
            ivr.delete()
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=msg),
                status=status.HTTP_200_OK)
        except IVR.DoesNotExist:
            return Response(
                data=get_response_data(
                    message=_('No existe el IVR')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al eliminar el IVR')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRAudioOptions(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        try:
            audios = ArchivoDeAudio.objects.all().order_by('id')
            data = [{'id': None, 'descripcion': '-----------'}] +\
                [AudioOptionsSerializer(a).data for a in audios]
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los archivos de audio de forma exitosa'),
                    data=data),
                status=status.HTTP_200_OK)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al obtener los archivos de audio')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IVRDestinationTypes(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        try:
            data = {
                '1': None,
                '2': None,
                '3': None,
                '5': None,
                '9': None,
                '7': None
            }
            for k, __ in DestinoEntrante.TIPOS_DESTINOS:
                destinos = DestinoEntrante.get_destinos_por_tipo(k)
                data[str(k)] = [{'id': None, 'nombre': '-----------'}] + [
                    DestinationTypesSerializer(d).data for d in destinos]
            return Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los destinos de forma exitosa'),
                    data=data),
                status=status.HTTP_200_OK)
        except Exception:
            return Response(
                data=get_response_data(
                    message=_('Error al obtener los destinos')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
