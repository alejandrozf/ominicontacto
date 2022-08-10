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
from django.utils.timezone import now, timedelta
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
            # Si es invalido el token:
            #     pido token de nuevo y reintento 1 vez
            #     Si vuelve a fallar log error y aviso al agente.
            logger.exception(err_msg.format(e))
            return e

    def obtener_token(self, autenticacion):
        """ Devuelve (Token, False) o ("Mensaje de Error", True)"""
        ahora = now()
        if autenticacion.token and autenticacion.expiracion_token \
                and autenticacion.expiracion_token > ahora:
            return autenticacion.token, False
        else:
            return self.actualizar_token(autenticacion)

    def actualizar_token(self, autenticacion, verify_ssl=True):
        parametros = {
            'username': autenticacion.username,
            'password': autenticacion.password
        }
        err_msg = _('Error al actualizar token de AutenticacionSitioExterno: {0}')
        try:
            ahora = now()
            response = requests.post(autenticacion.url, parametros, verify=verify_ssl)
        except requests.exceptions.SSLError as e:
            if verify_ssl:
                # Si hay error de validación SSL intento nuevamente sin verificar.
                # (debería configurarse en AutenticacionSitioExterno?)
                self.actualizar_token(autenticacion, verify_ssl=False)
                return autenticacion.token, False
            else:
                err_msg.format(e), True
        except Exception as e:
            logger.exception(err_msg.format(e))
            return err_msg.format(e), True

        if response.headers.get('Content-Type') == 'application/json':
            response_json = response.json()
            token = self.leer_campo(autenticacion.campo_token, response_json)
            if token is None:
                return err_msg.format('No se pudo obtener el token'), True
            autenticacion.token = token

            if autenticacion.duracion > 0:
                autenticacion.expiracion_token = ahora + timedelta(seconds=autenticacion.duracion)
            else:
                duracion = self.leer_campo(autenticacion.campo_duracion, response_json)
                duracion = int(float(duracion))
                autenticacion.expiracion_token = ahora + timedelta(seconds=duracion)
            autenticacion.save()
            return autenticacion.token, False
        else:
            return err_msg.format('Content-Type inválido'), True

    def leer_campo(self, campo, response_json):
        # En principio se asume que el campo esta en el primer nivel del objeto response.
        return response_json.get(campo, None)
