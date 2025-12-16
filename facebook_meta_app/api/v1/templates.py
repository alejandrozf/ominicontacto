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
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from facebook_meta_app.api.utils import HttpResponseStatus, get_response_data
from facebook_meta_app.models import Campana
from facebook_meta_app.api.v1.templates_messenger import ListSerializer as PlantillaSerializer


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication,)

    def list(self, request, campana_pk):
        try:
            print(">>>> campana_pk", campana_pk)
            campana = Campana.objects.get(pk=campana_pk)
            configuracion = campana.configuracion_meta_facebook
            data = {
                'facebook_templates': []
            }
            if configuracion:
                plantillas = configuracion.grupo_plantilla_facebook.plantillas
                serializer = PlantillaSerializer(plantillas, many=True)
                data.update({'facebook_templates': serializer.data})
                print(">>>> data", data)
            return response.Response(
                data=get_response_data(
                    status=HttpResponseStatus.SUCCESS,
                    message=_('Se obtuvieron los templates de forma exitosa'),
                    data=data),
                status=status.HTTP_200_OK)
        except Exception as e:
            print("********************************", e)
            return response.Response(
                data=get_response_data(message=_(str(e))),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
