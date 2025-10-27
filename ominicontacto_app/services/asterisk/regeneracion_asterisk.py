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

"""
Servicio de regenarción de archivos de asterisk y reload del mismo
"""

from __future__ import unicode_literals
from configuracion_telefonia_app.models import MusicaDeEspera, Playlist
from configuracion_telefonia_app.regeneracion_configuracion_telefonia import (
    SincronizadorDeConfiguracionTelefonicaEnAsterisk)
from ominicontacto_app.services.asterisk.redis_database import (
    RegenerarAsteriskFamilysOML,
)

import logging
import os

from django.utils.translation import gettext as _

from constance import config
from ominicontacto_app.errors import OmlError
from ominicontacto_app.asterisk_config import (
    AsteriskConfigReloader,
    AudioConfigFile,
    PlaylistsConfigCreator,
    QueuesCreator,
    SipConfigCreator,
)
from ominicontacto_app.models import ArchivoDeAudio
from whatsapp_app.services.redis.linea import StreamDeLineas


logger = logging.getLogger(__name__)


class RestablecerDialplanError(OmlError):
    """Indica que se produjo un error al crear el dialplan."""
    pass


class RegeneracionAsteriskService(object):

    def __init__(self):
        # Sincroniza Queues de Campañas
        self.queues_config_creator = QueuesCreator()
        # Sincroniza Sip De Agentes
        self.sip_config_creator = SipConfigCreator()
        # Sincroniza Modelos de Configuracion Telefonica
        self.sincronizador_config_telefonica = (
            SincronizadorDeConfiguracionTelefonicaEnAsterisk()
        )
        # Sincroniza en AstDB las que faltan en el Sincronizador de
        # Configuracion Telefonica
        self.asterisk_database = RegenerarAsteriskFamilysOML()
        self.playlist_config_creator = PlaylistsConfigCreator()

        # Llama al comando que reinicia Asterisk
        self.reload_asterisk_config = AsteriskConfigReloader()

    def _generar_y_recargar_configuracion_asterisk(self):
        proceso_ok = True
        mensaje_error = ""

        try:
            self.queues_config_creator.create_dialplan()
        except Exception:
            logger.exception(_("ActivacionQueueService: error al "
                               "intentar queues_config_creator()"))

            proceso_ok = False
            mensaje_error += _('Hubo un inconveniente al crear el archivo de '
                               'configuracion del queues de {0}. '.format(config.ASTERISK_TM))

        try:
            self.sip_config_creator.create_config_sip()
        except Exception:
            logger.exception(_("ActivacionAgenteService: error al "
                               "intentar create_config_sip()"))

            proceso_ok = False
            mensaje_error += _('Hubo un inconveniente al crear el archivo de '
                               'configuracion del config sip de {0}. '.format(config.ASTERISK_TM))

        try:
            self.playlist_config_creator.create_config_asterisk()
        except Exception:
            logger.exception(_("PlaylistsConfigCreator: error al "
                               "intentar create_config_sip()"))

            proceso_ok = False
            mensaje_error += _('Hubo un inconveniente al crear el archivo de '
                               'configuracion Playlists (MOH) en {0}. '.format(config.ASTERISK_TM))

        if not proceso_ok:
            raise RestablecerDialplanError(mensaje_error)
        else:
            self.sincronizador_config_telefonica.sincronizar_en_asterisk()
            self.asterisk_database.regenerar_asterisk()
            self.reload_asterisk_config.reload_asterisk()

    def _regenerar_redis_data(self):
        """ Regenera información que debe estar disponible en redis """
        StreamDeLineas().regenerar_stream()

    def _reenviar_archivos_playlist_asterisk(self):
        playlists = Playlist.objects.all()
        for playlist in playlists:
            musica_espera_list = MusicaDeEspera.objects.filter(
                playlist=playlist.pk
            )
            print(list(musica_espera_list))
            for musica in musica_espera_list:
                audio_file_asterisk = AudioConfigFile(musica)
                audio_file_asterisk.copy_asterisk()

    def _reenviar_archivos_audio_asterisk(self):
        audios = ArchivoDeAudio.objects.all()
        print(list(audios))
        for audio in audios:
            audio_file_asterisk = AudioConfigFile(audio)
            audio_file_asterisk.copy_asterisk()

    def regenerar(self):
        self._generar_y_recargar_configuracion_asterisk()
        self._regenerar_redis_data()
        self._reenviar_archivos_playlist_asterisk()
        self._reenviar_archivos_audio_asterisk()
        if not os.getenv('WALLBOARD_VERSION', '') == '':
            from wallboard_app.redis.regeneracion import (
                regenerar_wallboard_data
            )
            regenerar_wallboard_data()
