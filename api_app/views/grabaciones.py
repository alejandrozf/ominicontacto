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

import os

from django.conf import settings
from django_sendfile import sendfile
from django.utils.translation import ugettext as _

from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from api_app.views.permissions import TienePermisoOML
from api_app.authentication import ExpiringTokenAuthentication
from rest_framework.response import Response
from django.http import HttpResponseRedirect
import threading
from ominicontacto_app.services.grabaciones.generacion_zip_grabaciones \
    import GeneracionZipGrabaciones
import json
import boto3


class ObtenerArchivoGrabacionView(APIView):
    """Servicio que devuelve un archivo de grabación según su nombre
    """
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    http_method_names = ['get']

    def get(self, request):
        filename = request.query_params.get("filename")
        # Si es el comprimido de grabaciones no se busca en S3
        iszip = filename.find("/zip/", 0)

        if (os.getenv('S3_STORAGE_ENABLED') and iszip == -1):
            return self._get_s3_url(filename)

        return sendfile(request, settings.SENDFILE_ROOT + filename)

    def _get_s3_url(self, filename):
        client = boto3.client("s3",
                              aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        url = client.generate_presigned_url('get_object',
                                            Params={'Bucket': os.getenv('S3_BUCKET_NAME'),
                                                    'Key': filename[1:]
                                                    },
                                            ExpiresIn=3600)
        return HttpResponseRedirect(url)


class ObtenerArchivosGrabacionView(APIView):
    # Servicio que genera Zip con grabaciones seleccionadas
    permission_classes = (TienePermisoOML, )
    authentication_classes = (SessionAuthentication, ExpiringTokenAuthentication, )
    http_method_names = ['post']

    def _generar_zip(self, listado_archivos, username, key_task):

        zip_path = os.path.join(settings.SENDFILE_ROOT, 'zip')
        zip_grabaciones = GeneracionZipGrabaciones(listado_archivos, zip_path, key_task, username)
        zip_grabaciones.genera_zip()

    def post(self, request):
        params = request.POST
        supervisor_id = request.user.id
        TASK_ID = 'zip'
        listado_archivos = json.loads(params.get('files'))

        key_task = 'OML:STATUS_DOWNLOAD:RECORDINGS:{0}:{1}'.format(supervisor_id, TASK_ID)

        thread_zip = threading.Thread(
            target=self._generar_zip, args=[listado_archivos, request.user.username, key_task])
        thread_zip.setDaemon(True)
        thread_zip.start()

        return Response(data={
            'status': 'OK',
            'msg': _('Exportación de grabaciones Zip en proceso'),
        })
