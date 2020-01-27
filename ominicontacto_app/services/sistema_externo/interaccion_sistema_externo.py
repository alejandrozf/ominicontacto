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

"""Parser de XML que devuelve Asterisk"""

from __future__ import unicode_literals
import logging
import requests

from django.utils.translation import ugettext as _
from ominicontacto_app.models import SitioExterno

logger = logging.getLogger(__name__)


class InteraccionConSistemaExterno(object):

    def ejecutar_interaccion(self, sitio_externo, agente, campana, contacto, call_data):
        url = sitio_externo.url
        parametros = sitio_externo.get_parametros(agente, campana, contacto, call_data)
        err_msg = _('Error al ejecutar InteraccionConSistemaExterno: {0}')
        try:
            if sitio_externo.metodo == SitioExterno.GET:
                requests.get(url, params=parametros)
            elif sitio_externo.formato == SitioExterno.TEXT_PLAIN:
                requests.post(url, data=parametros, headers={'content_type': 'text/plain'})
            elif sitio_externo.formato == SitioExterno.WWW_FORM:
                requests.post(url, data=parametros)
            elif sitio_externo.formato == SitioExterno.MULTIPART:
                requests.post(url, files=parametros)
            elif sitio_externo.formato == SitioExterno.JSON:
                requests.post(url, json=parametros)
        except Exception as e:
            logger.exception(err_msg.format(e))
            return e
