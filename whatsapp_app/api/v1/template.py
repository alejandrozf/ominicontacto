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
from whatsapp_app.api.utils import HttpResponseStatus, get_response_data
from whatsapp_app.models import Campana, Linea
from whatsapp_app.api.v1.plantilla_mensaje import ListSerializer as PlantillaSerializer
from whatsapp_app.api.v1.template_whatsapp import ListSerializer as TemplateSerializer


class ViewSet(viewsets.ViewSet):
    permission_classes = [TienePermisoOML]
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication,)

    def list(self, request, campana_pk):
        try:
            campana = Campana.objects.get(pk=campana_pk)
            configuracionwhatsapp = campana.configuracionwhatsapp.last()
            data = {
                'message_templates': []
            }
            if configuracionwhatsapp:
                plantillas = configuracionwhatsapp.grupo_plantilla_whatsapp.plantillas
                serializer = PlantillaSerializer(plantillas, many=True)
                data.update({'message_templates': serializer.data})

            if 'line_id' in self.request.GET:
                line = Linea.objects.get(id=self.request.GET['line_id'])
                templates_whatsapp =\
                    line.templates_whatsapp.filter(is_active=True).exclude(tipo='BUTTON')
                serializer = TemplateSerializer(templates_whatsapp, many=True)
                data['whatsapp_templates'] = serializer.data

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
