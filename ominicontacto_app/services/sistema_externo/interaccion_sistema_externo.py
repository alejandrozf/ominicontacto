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
        headers, error = self.obtener_headers(sitio_externo)
        verify_ssl = True
        if sitio_externo.autenticacion and not sitio_externo.autenticacion.ssl_estricto:
            verify_ssl = False
        if error:
            logger.exception(err_msg.format(headers))
            return headers
        try:
            if sitio_externo.metodo == SitioExterno.GET:
                requests.get(url, params=parametros, headers=headers, verify=verify_ssl)
            elif sitio_externo.formato == SitioExterno.TEXT_PLAIN:
                headers['content_type'] = 'text/plain'
                requests.post(url, data=parametros, headers=headers, verify=verify_ssl)
            elif sitio_externo.formato == SitioExterno.WWW_FORM:
                requests.post(url, data=parametros, headers=headers, verify=verify_ssl)
            elif sitio_externo.formato == SitioExterno.MULTIPART:
                requests.post(url, files=parametros, headers=headers, verify=verify_ssl)
            elif sitio_externo.formato == SitioExterno.JSON:
                requests.post(url, json=parametros, headers=headers, verify=verify_ssl)
        except Exception as e:
            # Si es invalido el token:
            #     pido token de nuevo y reintento 1 vez
            #     Si vuelve a fallar log error y aviso al agente.
            logger.exception(err_msg.format(e))
            return e

    def obtener_headers(self, sitio_externo):
        if sitio_externo.autenticacion:
            token, error = self.obtener_token(sitio_externo.autenticacion)
            if error:
                logger.exception(error)
                return error, True
            else:
                return {'Authorization': 'Bearer ' + token}, False
        return {}, False

    def obtener_token(self, autenticacion):
        """ Devuelve (Token, False) o ("Mensaje de Error", True)"""
        ahora = now()
        if autenticacion.token and autenticacion.expiracion_token \
                and autenticacion.expiracion_token > ahora:
            return autenticacion.token, False
        else:
            return self.actualizar_token(autenticacion)

    def actualizar_token(self, autenticacion):
        parametros = {
            'username': autenticacion.username,
            'password': autenticacion.password
        }
        err_msg = _('Error al actualizar token de AutenticacionSitioExterno: {0}')
        verify_ssl = autenticacion.ssl_estricto
        try:
            ahora = now()
            response = requests.post(autenticacion.url, parametros, verify=verify_ssl)
        except Exception as e:
            return err_msg.format(e), True

        if response.status_code >= 400:
            err_msg = err_msg.format('Status Code invalido: {0}\n{1}'.format(
                response.status_code, response.reason))
            return err_msg, True
        if 'application/json' not in response.headers.get('Content-Type', ''):
            err_msg = err_msg.format('Content-Type inválido')
            return err_msg, True

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

    def leer_campo(self, campo, response_json):
        # En principio se asume que el campo esta en el primer nivel del objeto response.
        return response_json.get(campo, None)
