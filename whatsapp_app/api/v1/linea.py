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
from django.utils.translation import ugettext as _
from django.db.models import F, Func, Value, JSONField
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from configuracion_telefonia_app.models import DestinoEntrante, OpcionDestino
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.services.redis.linea import StreamDeLineas
from whatsapp_app.models import Linea, ConfiguracionWhatsappCampana, MenuInteractivoWhatsapp
from whatsapp_app.api.v1.linea_serializers import (
    ListSerializer, LineaRetrieveSerializer, UpdateSerializer, LineaCreateSerializer,
    DestinoDeLineaCreateSerializer, )
from ominicontacto_app.models import Campana


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )

    def list(self, request):
        try:
            queryset = Linea.objects.filter(
                is_active=True
            ).annotate(
                created_jsonb=Func(
                    Value("date"),
                    Func(F("created_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("created_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
                updated_jsonb=Func(
                    Value("date"),
                    Func(F("updated_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("updated_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            ).order_by(
                "nombre",
            )
            serializer = ListSerializer(queryset, many=True)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron las líneas de forma exitosa'),
                    data=serializer.data),
                status=status.HTTP_200_OK)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener las líneas')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            request_data = request.data.copy()
            if 'destination' not in request_data:
                return response.Response(data=get_response_data(
                    message=_('Error en los datos'), errors={
                        'destination': [_('Este campo es requerido.')]}),
                    status=status.HTTP_400_BAD_REQUEST)
            destino_data = request_data.pop('destination')
            serializer = LineaCreateSerializer(data=request_data)
            if serializer.is_valid():
                serializer_destino = DestinoDeLineaCreateSerializer(data=destino_data)
                if serializer_destino.is_valid():
                    serializer_destino.save()
                    destino = serializer_destino.destino
                    line = serializer.save(
                        destino=destino,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    if line.destino.tipo == DestinoEntrante.CAMPANA:
                        if not destino.content_object.whatsapp_habilitado:
                            destino.content_object.whatsapp_habilitado = True
                            destino.content_object.save()
                            confwhatsappcampana = ConfiguracionWhatsappCampana(
                                campana=destino.content_object,
                                linea=line,
                                nivel_servicio=90,
                                created_by=request.user,
                                updated_by=request.user,
                            )
                            confwhatsappcampana.save()
                    if line.destino.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                        destino.content_object.is_main = True
                        destino.content_object.save()
                        menu_ids = [menu.get('id')
                                    for menu in serializer_destino.data['data'] if 'id' in menu]
                        if menu_ids:
                            MenuInteractivoWhatsapp.objects.filter(
                                id__in=menu_ids).update(line=line.id)

                    serialized_data = serializer.data
                    serialized_data['destination'] = serializer_destino.data
                    StreamDeLineas().notificar_nueva_linea(line)
                    return response.Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            message=_('Se creo la línea de forma exitosa'),
                            data=serialized_data),
                        status=status.HTTP_201_CREATED)
                else:
                    return response.Response(
                        data=get_response_data(message=_('Error en los datos'),
                                               errors={'destination': serializer_destino.errors}),
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response(
                    data=get_response_data(message=_('Error en los datos'),
                                           errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(
                data=get_response_data(message=_('Error al crear la línea') + str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:
            queryset = Linea.objects.filter(
                is_active=True
            ).annotate(
                created_jsonb=Func(
                    Value("date"),
                    Func(F("created_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("created_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
                updated_jsonb=Func(
                    Value("date"),
                    Func(F("updated_at"), Value("YYYY-MM-DD"), function="to_char"),
                    Value("user"),
                    F("updated_by__username"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            )
            instance = queryset.get(pk=pk)
            serializer = LineaRetrieveSerializer(instance)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    data=serializer.data,
                    message=_('Se obtuvo la línea de forma exitosa')),
                status=status.HTTP_200_OK)
        except Linea.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Línea no encontrada')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return response.Response(
                data=get_response_data(
                    message=_('Error al obtener la línea: ') + str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            queryset = Linea.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            request_data = request.data.copy()
            if 'destination' not in request_data:
                return response.Response(data=get_response_data(
                    message=_('Error en los datos'), errors={
                        'destination': [_('Este campo es requerido.')]}),
                    status=status.HTTP_400_BAD_REQUEST)
            destino_data = request_data.pop('destination')
            serializer = UpdateSerializer(instance, data=request_data, partial=True)
            if serializer.is_valid():
                serializer_destino =\
                    DestinoDeLineaCreateSerializer(data=destino_data, context={'line': instance})
                if serializer_destino.is_valid():
                    # Primero desconectar destino anterior de la línea para poderlo borrar
                    # pues es un campo PROTECT
                    instance.destino = None
                    instance.save()
                    for menu_old in instance.menuinteractivo.all():
                        try:
                            destino_old = DestinoEntrante.objects.get(
                                object_id=menu_old.pk,
                                tipo=DestinoEntrante.MENU_INTERACTIVO_WHATSAPP)
                            opciones_destino =\
                                OpcionDestino.objects.filter(destino_anterior=destino_old)
                            for option in opciones_destino:
                                if option.destino_siguiente.tipo ==\
                                        DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                                    option.destino_siguiente.delete()
                                option.delete()
                            destino_old.delete()
                            menu_old.delete()
                        except Exception:
                            instance.menuinteractivo.update(line=None)
                    serializer_destino.save()
                    destino = serializer_destino.destino
                    line = serializer.save(
                        destino=destino,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    if line.destino.tipo == DestinoEntrante.CAMPANA:
                        if not destino.content_object.whatsapp_habilitado:
                            destino.content_object.whatsapp_habilitado = True
                            destino.content_object.save()
                            confwhatsappcampana = ConfiguracionWhatsappCampana(
                                campana=destino.content_object,
                                linea=line,
                                nivel_servicio=90,
                                created_by=request.user,
                                updated_by=request.user,
                            )
                            confwhatsappcampana.save()
                    if line.destino.tipo == DestinoEntrante.MENU_INTERACTIVO_WHATSAPP:
                        destino.content_object.is_main = True
                        destino.content_object.save()

                    serialized_data = serializer.data
                    serialized_data['destination'] = serializer_destino.data
                    StreamDeLineas().notificar_nueva_linea(line)
                    return response.Response(
                        data=get_response_data(
                            status=HttpResponseStatus.SUCCESS,
                            message=_('Se creo la línea de forma exitosa'),
                            data=serialized_data),
                        status=status.HTTP_201_CREATED)
                else:
                    return response.Response(
                        data=get_response_data(
                            message=_('Error en los datos') + ' destination: {}'.format(
                                serializer_destino.errors),
                            errors={'destination': serializer_destino.errors}),
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response(
                    data=get_response_data(message=_('Error en los datos'),
                                           errors=serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(
                data=get_response_data(message=_('Error al crear la línea >>>') + str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            queryset = Linea.objects.filter(is_active=True)
            instance = queryset.get(pk=pk)
            if not instance.configuracionwhatsapp.exclude(
                    campana__estado=Campana.ESTADO_BORRADA, campana__whatsapp_habilitado=False):
                instance.is_active = False
                instance.save()
                StreamDeLineas().notificar_linea_eliminada(instance)
                return response.Response(
                    data=get_response_data(
                        status=HttpResponseStatus.SUCCESS,
                        message=_('Se elimino la línea de forma exitosa')),
                    status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=get_response_data(
                        message=_('Esta línea está siendo usada por alguna campaña activa.')),
                    status=status.HTTP_401_UNAUTHORIZED)
        except Linea.DoesNotExist:
            return response.Response(
                data=get_response_data(message=_('Línea no encontrado')),
                status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return response.Response(
                data=get_response_data(
                    message=_('Error al eliminar la línea')),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
