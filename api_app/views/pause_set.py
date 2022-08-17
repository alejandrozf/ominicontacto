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
from api_app.serializers.pause_set import (
    ConfiguracionDePausaSerializer, ConjuntoDePausaSerializer,
    OpcionesDePausaParaConjuntoSerializer)
from ominicontacto_app.models import ConfiguracionDePausa, ConjuntoDePausa, Pausa
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_app.authentication import ExpiringTokenAuthentication
from api_app.views.permissions import TienePermisoOML


class Pausas(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _(u'Se obtuvieron las pausas de forma exitosa'),
            'pauses': []}
        try:
            data['pauses'] = [
                OpcionesDePausaParaConjuntoSerializer(p).data
                for p in Pausa.objects.filter(
                    eliminada=False)]
            return Response(data=data, status=status.HTTP_200_OK)
        except Pausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener las pausas')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConjuntoDePausaList(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvieron los conjuntos '
                         'de pausas de forma exitosa'),
            'pauseSets': []}
        try:
            conjuntosDePausa = ConjuntoDePausa.objects.all()
            data['pauseSets'] = [
                ConjuntoDePausaSerializer(conjunto).data
                for conjunto in conjuntosDePausa]
            return Response(data=data, status=status.HTTP_200_OK)
        except ConjuntoDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al obtener los conjuntos de pausas')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConjuntoDePausaDetalle(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['get']

    def get(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se obtuvo la informacion del '
                         'conjunto de pausa de forma exitosa'),
            'pauseSetDetail': None}
        try:
            conjuntoDePausa = ConjuntoDePausa.objects.get(pk=pk)
            set_data = {
                'conjunto': ConjuntoDePausaSerializer(conjuntoDePausa).data,
                'pausas': [],
            }
            for pausa in conjuntoDePausa.pausas.all():
                if not pausa.pausa.eliminada:
                    set_data['pausas'].append(
                        ConfiguracionDePausaSerializer(pausa).data)
            data['pauseSetDetail'] = set_data
            return Response(data=data, status=status.HTTP_200_OK)
        except ConjuntoDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _('Error al obtener el '
                                'detalle del conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConjuntoDePausaCreate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se creo el conjunto de pausa de forma exitosa')}
        nombre = request.data.get('nombre')
        pausas = request.data.get('pausas')
        if not nombre:
            data['status'] = 'ERROR'
            data['message'] = _('El nombre del conjunto es requerido')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not pausas or len(pausas) == 0:
            data['status'] = 'ERROR'
            data['message'] = _('Debe existir al menos '
                                'una pausa en el conjunto')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        try:
            conjuntoDePausa = ConjuntoDePausa.objects.create(nombre=nombre)
            for pausa in pausas:
                p = Pausa.objects.get(pk=pausa['pauseId'])
                ConfiguracionDePausa.objects.create(
                    pausa=p, conjunto_de_pausa=conjuntoDePausa,
                    time_to_end_pause=pausa['timeToEndPause'])
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al crear el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConjuntoDePausaUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se actualizo el conjunto de pausa de forma exitosa')}
        nombre = request.data.get('nombre')
        if not nombre:
            data['status'] = 'ERROR'
            data['message'] = _('El nombre del conjunto es requerido')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        try:
            conjunto_de_pausa = ConjuntoDePausa.objects.get(pk=pk)
            conjunto_de_pausa.nombre = nombre
            conjunto_de_pausa.save()
            return Response(data=data, status=status.HTTP_200_OK)
        except ConjuntoDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al actualizar el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConjuntoDePausaDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino el conjunto de pausa de forma exitosa')}
        try:
            conjunto_de_pausa = ConjuntoDePausa.objects.get(pk=pk)
            if not conjunto_de_pausa.tiene_grupos():
                conjunto_de_pausa.delete()
                return Response(data=data, status=status.HTTP_200_OK)
            data['status'] = 'ERROR'
            data['message'] = _('No puedes borrar un conjunto de '
                                'pausas que esta asignado a '
                                'un grupo de agentes')
            return Response(
                data=data, status=status.HTTP_400_BAD_REQUEST)
        except ConjuntoDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfiguracionDePausaCreate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['post']

    def post(self, request):
        data = {
            'status': 'SUCCESS',
            'message': _('Se creo la configuracion '
                         'de pausa de forma exitosa')}
        pausa_id = request.data.get('pauseId')
        conjunto_de_pausa_id = request.data.get('setId')
        time_to_end_pause = request.data.get('timeToEndPause')
        if time_to_end_pause < 0:
            data['status'] = 'ERROR'
            data['message'] = _('El timeout debe ser mayor a cero')
            return Response(
                data=data, status=status.HTTP_400_BAD_REQUEST)
        try:
            pausa = Pausa.objects.get(pk=pausa_id)
        except Pausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            conjunto_de_pausa = ConjuntoDePausa.objects.get(
                pk=conjunto_de_pausa_id)
        except ConjuntoDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe el conjunto de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            ConfiguracionDePausa.objects.create(
                pausa=pausa, conjunto_de_pausa=conjunto_de_pausa,
                time_to_end_pause=time_to_end_pause)
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al crear la configuracion de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfiguracionDePausaDelete(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['delete']

    def delete(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se elimino la configuracion '
                         'de pausa de forma exitosa')}
        try:
            config_de_pausa = ConfiguracionDePausa.objects.get(pk=pk)
            if config_de_pausa.conjunto_de_pausa.se_puede_eliminar_pausa():
                config_de_pausa.delete()
            else:
                data['status'] = 'ERROR'
                data['message'] = _('No puedes dejar a un '
                                    'Conjunto de Pausas vacio')
            return Response(data=data, status=status.HTTP_200_OK)
        except ConfiguracionDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la configuracion de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _(u'Error al eliminar la configuracion de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfiguracionDePausaUpdate(APIView):
    permission_classes = (TienePermisoOML, )
    authentication_classes = (
        SessionAuthentication, ExpiringTokenAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ['put']

    def put(self, request, pk):
        data = {
            'status': 'SUCCESS',
            'message': _('Se actualizo la configuracion '
                         'de pausa de forma exitosa')}
        time_to_end_pause = request.data.get('timeToEndPause')
        try:
            config_pausa = ConfiguracionDePausa.objects.get(pk=pk)
            config_pausa.time_to_end_pause = time_to_end_pause
            config_pausa.save()
            return Response(data=data, status=status.HTTP_200_OK)
        except ConfiguracionDePausa.DoesNotExist:
            data['status'] = 'ERROR'
            data['message'] = _(u'No existe la configuracion de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            data['status'] = 'ERROR'
            data['message'] = _('Error al actualizar '
                                'la configuracion de pausa')
            return Response(
                data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
