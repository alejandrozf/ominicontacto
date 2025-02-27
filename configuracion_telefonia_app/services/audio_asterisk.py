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
import logging
import os
import requests
import tempfile
import base64
import json
from pathlib import Path
from django.utils.translation import gettext_lazy as _

from ominicontacto_app.services.redis.redis_streams import RedisStreams
from configuracion_telefonia_app.models import AudiosAsteriskConf

logger = logging.getLogger(__name__)


class AsteriskSoundsInstaller():
    ASTERISK_SOUNDS_URL = 'https://downloads.asterisk.org/pub/telephony/sounds/'

    def install(self, language):
        if language == 'po':
            return self._install_portuguese()

        try:
            filename_full_path = self._download_asterisk_sound(language)

            __, nombre_archivo = os.path.split(filename_full_path)
            sound_tar_data = Path(filename_full_path).read_bytes()
            res = base64.b64encode(sound_tar_data)
            res = res.decode('utf-8')
            redis_stream = RedisStreams()
            content = {
                'archivo': nombre_archivo,
                'type': 'ASTERISK_SOUNDS',
                'action': 'COPY',
                'language': language,
                'content': res
            }
            self._create_audios_asterisk_conf(language)
            redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))
            return False
        except Exception as e:
            logger.error(_("Error al instalar el paquete de idioma: {0}".format(e)))
            return True

    def _download_asterisk_sound(self, language):
        filename = 'asterisk-core-sounds-{0}-wav-current.tar.gz'.format(language)
        url = self.ASTERISK_SOUNDS_URL + filename
        response = requests.get(url, stream=True)
        filename_full_path = os.path.join(tempfile.gettempdir(), filename)
        handle = open(filename_full_path, "wb")  # ver el
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        return filename_full_path

    def _create_audios_asterisk_conf(self, language):
        audios, created = AudiosAsteriskConf.objects.get_or_create(
            paquete_idioma=language, defaults={'esta_instalado': True})
        if not created:
            audios.esta_instalado = True
            audios.save()

    def _install_portuguese(self):
        # Download From:
        # https://github.com/marcelsavegnago/issabel_sounds_pt_BR
        # self._create_audios_asterisk_conf('po')
        # Upload to redis
        pass
