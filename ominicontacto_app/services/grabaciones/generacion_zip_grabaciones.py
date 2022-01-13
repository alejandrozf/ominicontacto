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

"""
Servicio para generar reporte csv de las reportes de los agentes
"""
from __future__ import unicode_literals

import os
import zipfile
from django.conf import settings
import redis
from math import ceil
import io
import csv
import boto3


class GeneracionZipGrabaciones:
    def __init__(self, listado_archivos, zip_path, key_task, username):
        self.listado_archivos = listado_archivos
        self.key_task = key_task
        self.username = username
        self.zip_path = zip_path
        if not os.path.exists(self.zip_path):
            os.makedirs(self.zip_path, mode=0o755)
        self.zip_name = os.path.join(self.zip_path, self._generar_zip_name(self.username))

        self.redis_connection = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.CONSTANCE_REDIS_CONNECTION['port'],
            decode_responses=True)

    def genera_zip(self):
        compression = zipfile.ZIP_DEFLATED
        zf = zipfile.ZipFile(self.zip_name, mode="w")
        in_memory_csv = io.StringIO()
        csv_writer = csv.writer(in_memory_csv)
        csv_writer.writerows([['Fecha', 'Tipo de llamada', 'Teléfono cliente',
                               'Agente', 'Campaña', 'Calificación', 'Nombre grabación']])
        progreso = 0
        cantidad_archivos = len(self.listado_archivos)
        self.redis_connection.publish(self.key_task, progreso)
        i = 1
        for archivo in self.listado_archivos:
            obs = ''
            if (os.getenv('S3_STORAGE_ENABLED') == 'true'):
                self._save_file_from_s3(archivo, settings.SENDFILE_ROOT)
            archivo_path = os.path.join(settings.SENDFILE_ROOT, archivo['archivo'])
            try:
                zf.write(archivo_path, archivo['archivo'], compress_type=compression)
            except Exception:
                obs = ' (ERROR EN DESCARGA)'

            progreso = ceil(i / cantidad_archivos * 100)
            self.redis_connection.publish(self.key_task, progreso)
            i += 1
            csv_line = [[
                archivo['fecha'],
                archivo['tipo_llamada'],
                archivo['telefono_cliente'],
                archivo['agente'],
                archivo['campana'],
                archivo['calificacion'],
                archivo['archivo'] + obs
            ]]
            csv_writer.writerows(csv_line)
        in_memory_csv.seek(0)
        zf.writestr('datos.csv', in_memory_csv.getvalue(), compress_type=compression)
        zf.close()

        self.redis_connection.publish(self.key_task, self._generar_zip_name(self.username))

    # En un futuro ver si es neesario generar un nombre acorde a un patrón
    def _generar_zip_name(self, username):
        return f'{username}-grabaciones.zip'

    def _save_file_from_s3(self, archivo, local_path):
        s3 = boto3.resource("s3",
                            aws_access_key_id=os.getenv('API_CLOUD_ACCESS_KEY'),
                            aws_secret_access_key=os.getenv('API_CLOUD_SECRET_KEY'))

        pathr = os.path.dirname(os.path.join(settings.SENDFILE_ROOT, archivo['archivo']))
        if not os.path.exists(pathr):
            os.makedirs(pathr, mode=0o755)
        try:
            s3.Bucket(os.getenv('S3_BUCKET_NAME')) \
                .download_file(archivo['archivo'],
                               os.path.join(settings.SENDFILE_ROOT, archivo['archivo']))
        except Exception:
            return False
        return True
