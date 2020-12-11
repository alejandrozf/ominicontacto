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


from django.conf import settings
from django_sendfile import sendfile

from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication


class ObtenerArchivoGrabacionView(APIView):
    """Servicio que devuelve un archivo de grabación según su nombre
    """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    http_method_names = ['get']

    def get(self, request):
        filename = request.query_params.get("filename")
        return sendfile(request, settings.SENDFILE_ROOT + filename)
