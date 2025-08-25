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

"""Servicio para generar los curl hacia wombat"""

from __future__ import unicode_literals

import logging
import subprocess
import os
import json
import time
import requests
from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.timezone import now, timedelta
from constance import config as config_constance

logger = logging.getLogger(__name__)


class WombatAPI(object):

    GET_DIALER_STATE_URL = "api/engine/?op=STATE"
    STOP_SERVICE_URL = "api/engine/?op=STOP"
    START_SERVICE_URL = "api/engine/?op=START"

    def update_config_wombat(self, json_file, url_edit):
        """Realiza un update en la config de wombat

        :returns: json -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        filename = os.path.join(settings.OML_WOMBAT_FILENAME,
                                json_file)
        try:
            # subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                           ':'.join([settings.OML_WOMBAT_USER,
                                                     settings.OML_WOMBAT_PASSWORD]),
                                           '-X', 'POST', '--data-urlencode',
                                           '@'.join(['data', filename]),
                                           '/'.join([settings.OML_WOMBAT_URL,
                                                     url_edit])])
            logger.info(_("actualizacion en WOMBAT OK"))
            return json.loads(out)
        except subprocess.CalledProcessError as e:
            logger.warning(_("Exit status erroneo: {0}".format(e.returncode)))
            logger.warning(" - Comando ejecutado: {0}".format(e.cmd))
            print(e)

    def update_lista_wombat(self, nombre_archivo, url_edit):
        """Realiza un update en la config de wombat

        :returns: out -- salida del comando ejectuado hacia wombat.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        try:
            # subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            filename_archivo = settings.OML_WOMBAT_FILENAME + nombre_archivo
            out = subprocess.check_output(['curl', '--user',
                                           ':'.join([settings.OML_WOMBAT_USER,
                                                     settings.OML_WOMBAT_PASSWORD]),
                                           '-m', settings.OML_WOMBAT_TIMEOUT, '-X', 'POST', '-w',
                                           'string', '-d', "@{0}".format(filename_archivo),
                                           '/'.join([settings.OML_WOMBAT_URL,
                                                     url_edit])])
            return out
        except subprocess.CalledProcessError as e:
            logger.warning(_("Exit status erroneo: {0}".format(e.returncode)))
            logger.warning(_(" - Comando ejecutado: {0}".format(e.cmd)))
            print(e)

    def list_config_wombat(self, url_edit):
        # TODO: Renombrar. Impacta en wombat sin parametros (solo url). Devuelve respuesta JSON
        """Realiza un list en la config de wombat

        :returns: json -- exit status de proceso ejecutado.
                  0 (cero) si fue exitoso, otro valor si se produjo
                  un error
        """
        try:
            # subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                           ':'.join([settings.OML_WOMBAT_USER,
                                                     settings.OML_WOMBAT_PASSWORD]),
                                           '-X', 'POST',
                                           '/'.join([settings.OML_WOMBAT_URL,
                                                     url_edit])])
            logger.info(_("list en WOMBAT OK"))
            return json.loads(out)
        except subprocess.CalledProcessError as e:
            logger.warning(_("Exit status erroneo: {0}".format(e.returncode)))
            logger.warning(_(" - Comando ejecutado: {0}".format(e.cmd)))
            print(e)

    def set_call_ext_status(self, url_set_status):
        try:
            # subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                           ':'.join([settings.OML_WOMBAT_USER,
                                                     settings.OML_WOMBAT_PASSWORD]),
                                           '-X', 'POST',
                                           '/'.join([settings.OML_WOMBAT_URL,
                                                     url_set_status])])
            if 'Event CALLSTATUS queued' in str(out):
                logger.info(_("Set extStatus en WOMBAT OK"))
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(_("Exit status erroneo: {0}".format(e.returncode)))
            logger.warning(_(" - Comando ejecutado: {0}".format(e.cmd)))
            print(e)

    def post_json(self, url, object):
        """Realiza un POST a wombat enviando el json de un objeto usando data-urlencode

        :returns: json -- exit status de proceso ejecutado.
                  otro valor si se produjo un error
        """
        try:
            # subprocess.check_call(settings.FTS_RELOAD_CMD,
            #                      stdout=stdout_file, stderr=stderr_file)
            out = subprocess.check_output(['curl', '--user',
                                           ':'.join([settings.OML_WOMBAT_USER,
                                                     settings.OML_WOMBAT_PASSWORD]),
                                           '-X', 'POST', '--data-urlencode',
                                           "data={0}".format(json.dumps(object)),
                                           '/'.join([settings.OML_WOMBAT_URL,
                                                     url])])
            logger.info(_("POST en WOMBAT OK"))
            return json.loads(out)
        except subprocess.CalledProcessError as e:
            logger.warning(_("Exit status erroneo: {0}".format(e.returncode)))
            logger.warning(_(" - Comando ejecutado: {0}".format(e.cmd)))
            print(e)

    def get_dialer_state(self):
        response = self.list_config_wombat(self.GET_DIALER_STATE_URL)
        uptime = None
        if response and 'state' in response:
            state = response['state']
            if 'uptimeMs' in response:
                uptime = response['uptimeMs']
            return state, uptime
        else:
            logger.warning(_("No se pudo obtener el estado del dialer"))
            return None, None

    def agendar_llamada(self, campana, agenda):
        fecha_hora = '.'.join([str(agenda.fecha), str(agenda.hora)])
        telefono = agenda.contacto.telefono
        # TODO: Pasar a WombatAPI
        url_wombat = urljoin(settings.OML_WOMBAT_URL,
                             f'api/calls/?op=addcall&campaign={campana.pk}_{campana.nombre}&'
                             f'number={telefono}&schedule={fecha_hora}&'
                             f'attrs=ID_CAMPANA:{campana.pk},ID_CLIENTE:{agenda.contacto.pk},'
                             f'CAMPANA:{campana.nombre}')
        requests.post(url_wombat)


class WombatReloader(object):

    STATE_DOWN = 'DOWN'
    STATE_STARTING = 'STARTING'
    STATE_READY = 'READY'

    def __init__(self):
        self.service = WombatAPI()

    def reload(self):
        """ Inicia el proceso de reload """
        # Obtener estado "/api/engine/?op=STATE"
        if config_constance.WOMBAT_DIALER_STATE == self.STATE_DOWN:
            self._start_dialer_for_reload()
            return
        stop_status = self.stop_dialer()
        if stop_status is None:
            logger.warning(
                'No se pudo reiniciar Wombat Dialer. Error en _start_dialer_for_reload')
            return
        time.sleep(5)
        self.start_tries = 0
        self._start_dialer_for_reload()

    def _start_dialer_for_reload(self):
        # Sólo lo inicia si el estado es "DOWN"
        # Si tarda mucho los unicos otros estados que deberia tener es
        # "TERMINATION_REQD" o "TIMEOUT_NO_REPLY"
        logger.debug('Starteando')
        state, uptime = self.service.get_dialer_state()
        if state is not None and state == self.STATE_DOWN:
            config_constance.WOMBAT_DIALER_STATE = self.STATE_STARTING
            response = self.service.list_config_wombat(WombatAPI.START_SERVICE_URL)
            if 'state' in response and response['state'] == self.STATE_READY:
                uptime = response['uptimeMs']
                config_constance.WOMBAT_DIALER_STATE = self.STATE_READY
                self.save_update_datetime(uptime)
                logger.debug('Wombat Reload OK')
                return
            time.sleep(5)
            self.confirm_tries = 0
            self._confirm_dialer_is_ready()
        elif state is not None and state == self.STATE_READY:
            config_constance.WOMBAT_DIALER_STATE = self.STATE_READY
            self.save_update_datetime(uptime)
            return
        else:
            # "TERMINATION_REQD" o "TIMEOUT_NO_REPLY" Espero a ver si deriva en DOWN o READY
            # Intento varias veces hasta cancelar.
            self.start_tries += 1
            if self.start_tries > 5:
                logger.warning(
                    'No se pudo reiniciar Wombat Dialer. Error en _start_dialer_for_reload')
                return
            time.sleep(5)
            self._start_dialer_for_reload()

    def _confirm_dialer_is_ready(self):
        # Termina cuando wombat dialer llega al estado "READY"
        # Si tarda mucho el unico otro estado que deberia tener es "TIMEOUT_NO_REPLY" (?)
        state, uptime = self.service.get_dialer_state()
        if state == 'READY':
            self.config_constance.WOMBAT_DIALER_STATE = self.STATE_READY
            self.save_update_datetime(uptime)
            return
        else:
            # Espero la confirmación un cierto numero de veces
            self.confirm_tries += 1
            if self.confirm_tries > 5:
                logger.warning(
                    'No se pudo reiniciar Wombat Dialer. Error en confirm_dialer_is_ready')
                return
            time.sleep(5)
            self._confirm_dialer_is_ready()

    def synchronize_local_state(self):
        """ Obtiene el estado de Wombat y actualiza el valor en Constance """
        state, uptime = self.service.get_dialer_state()
        if state is None:
            logger.warning('Error al buscar estado de wombat: ', state)
            return None, None, None
        if state == self.STATE_READY:
            config_constance.WOMBAT_DIALER_STATE = self.STATE_READY
            self.save_update_datetime(uptime)
            return self.STATE_READY, state, uptime
        elif state in ['TIMEOUT_NO_REPLY', 'TERMINATION_REQD', self.STATE_DOWN]:
            config_constance.WOMBAT_DIALER_STATE = self.STATE_DOWN
            self.save_update_datetime()
            return self.STATE_DOWN, state, uptime
        else:
            logger.warning('Error al buscar estado de wombat: ', state)
            return None, None, None

    def stop_dialer(self):
        config_constance.WOMBAT_DIALER_STATE = self.STATE_DOWN
        response = self.service.list_config_wombat(WombatAPI.STOP_SERVICE_URL)
        if response is None or 'state' not in response:
            logger.warning('Wombat Dialer STOP Failure.')
            logger.warning(response)
            return None
        return response['state']

    def force_start_dialer(self):
        response = self.service.list_config_wombat(WombatAPI.START_SERVICE_URL)
        if response and 'state' in response and response['state'] == self.STATE_READY:
            uptime = response['uptimeMs']
            config_constance.WOMBAT_DIALER_STATE = self.STATE_READY
            self.save_update_datetime(uptime)
        else:
            config_constance.WOMBAT_DIALER_STATE = self.STATE_DOWN
            self.save_update_datetime()
        return response

    def save_update_datetime(self, uptime=0):
        since = now() - timedelta(milliseconds=uptime)
        config_constance.WOMBAT_DIALER_UPDATE_DATETIME = since
        return since
