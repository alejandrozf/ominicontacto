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
import os

from django.utils.translation import ugettext as _
import logging as _logging

logger = _logging.getLogger(__name__)


class PlaylistDirectoryManager(object):

    def _get_path(self, nombre):
        return os.path.join(settings.OML_PLAYLIST_PATH_ASTERISK, nombre)

    def generar_directorio(self, nombre):
        # Me aseguro que exista el directorio para las playlists
        if not os.path.exists(settings.OML_PLAYLIST_PATH_ASTERISK):
            try:
                os.mkdir(settings.OML_PLAYLIST_PATH_ASTERISK)
            except OSError:
                logger.info(_('Error creando directorio: {0}').format(
                    settings.OML_PLAYLIST_PATH_ASTERISK))
                return False

        directory = self._get_path(nombre)
        if os.path.exists(directory):
            return True
        try:
            os.mkdir(directory)
        except OSError:
            logger.info(_('Error creando directorio: {0}').format(directory))
            return False
        else:
            logger.info(_('Se creo el directorio: {0}').format(directory))
        return True

    def eliminar_directorio(self, nombre):
        directory = self._get_path(nombre)
        if not os.path.exists(directory):
            logger.info(_('Error eliminando directorio. El directorio no existe: {0}').format(
                directory))
            return False

        try:
            os.rmdir(directory)
        except OSError:
            logger.info(_('Error al eliminar directorio: {0}').format(
                directory))
            return False
        return True
