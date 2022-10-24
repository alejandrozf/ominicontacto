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
from __future__ import unicode_literals
from ominicontacto_app.services.redis.redis_streams import RedisStreams

import json
import logging as _logging

logger = _logging.getLogger(__name__)


class PlaylistDirectoryManager(object):

    def eliminar_directorio(self, nombre):
        redis_stream = RedisStreams()
        content = {
            'archivo': nombre,
            'type': 'ASTERISK_PLAY_LIST_DIR',
            'action': 'DELETE',
        }
        redis_stream.write_stream('asterisk_conf_updater', json.dumps(content))
        return True
