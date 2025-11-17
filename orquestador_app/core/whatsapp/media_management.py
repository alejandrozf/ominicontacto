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
import os
import requests
import mimetypes
from django.conf import settings
from django.core.files.storage import default_storage

URL_FILEMANAGER_GUPSHUP = "https://filemanager.gupshup.io/wa/{0}/wa/media/{1}?download=false"
URL_FILEMANAGER_META = "https://graph.facebook.com/v22.0/{0}?phone_number_id={1}"


def meta_get_media_content(line, type, payload):
    headers = {
        "accept": "application/json",
        'Authorization': 'Bearer ' + line.proveedor.configuracion['access_token'],
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = payload[type]
    if 'id' in payload:
        response = requests.get(
            URL_FILEMANAGER_META.format(payload['id'], line.numero), headers=headers)
        if response.status_code == 200:
            response = response.json()
            url = response['url']
            extension = mimetypes.guess_extension(response['mime_type'])
            nombre_archivo = response['id'] + extension
            response_archivo = requests.get(url, headers=headers, stream=True, timeout=30)
            response_archivo.raise_for_status()
            ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'archivos_whatsapp', nombre_archivo)
            with default_storage.open(ruta_archivo, 'wb') as destino:
                for chunk in response_archivo.iter_content(chunk_size=8192):
                    destino.write(chunk)
                media_url = settings.MEDIA_URL + 'archivos_whatsapp/' + nombre_archivo
                message_dict = {
                    "type": type,
                    "previewUrl": media_url,
                    "originalUrl": media_url,
                    "url": media_url,
                    "name": nombre_archivo,
                    "filename": nombre_archivo
                }
                return message_dict
    return {}


def meta_get_media_template(line, link):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + line.proveedor.configuracion['access_token'],
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response_archivo = requests.get(link, headers=headers, stream=True, timeout=30)
    response_archivo.raise_for_status()
    cd = response_archivo.headers.get("Content-Disposition")
    if cd and 'filename' in cd:
        nombre_archivo = cd.split("filename=")[1].strip('"')
    else:
        nombre_archivo = link.split("/")[-1].split('?')[0]
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'archivos_whatsapp', nombre_archivo)
    with default_storage.open(ruta_archivo, 'wb') as destino:
        for chunk in response_archivo.iter_content(chunk_size=8192):
            destino.write(chunk)
        return nombre_archivo
    return ""
