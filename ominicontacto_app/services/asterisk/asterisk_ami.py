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

import logging as _logging

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from django.conf import settings
from ominicontacto_app.errors import OmlError

logger = _logging.getLogger(__name__)


class AMIManagerConnector(object):
    """Establece la conexión AMI utilizando la librería pyst2, para manipular asterisk
    """

    def __init__(self):
        self.manager = Manager()
        self.disconnected = False

    def connect(self):
        error = False
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.ASTERISK_HOSTNAME)
        try:
            self.manager.connect(ami_manager_host)
            self.manager.login(ami_manager_user, ami_manager_pass)
        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e))
            error = True
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e))
            error = True
        except ManagerException as e:
            logger.exception("Error {0}".format(e))
            error = True
        return error

    def disconnect(self):
        # Atención: El Manager solo permite una sola conexión
        self.manager.close()
        self.disconnected = True

    # TODO: Refactorizar esta clase. Nombres mas descriptivos.
    #       Permitir ejecutar varios comandos con la misma sesion.
    def _ami_manager(self, action, content):
        if self.disconnected:
            raise OmlError(message='La conexión del Asterisk Manager ya ha sido cerrada')
        if not self.manager.connected():
            raise OmlError(message='El Asterisk Manager no ha sido conectado')

        error = False
        data_returned = ''
        try:
            data_returned = self._ami_action(action, content)
        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e))
            error = True
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e))
            error = True
        except ManagerException as e:
            logger.exception("Error {0}".format(e))
            error = True
        return data_returned, error

    def _ami_action(self, action, content):
        if action == 'command':
            data_returned = self.manager.command(content).data
        elif action == 'QueueAdd':
            event_queuelog = 'ADDMEMBER'
            for i in range(len(content[2])):
                dict = {
                    'Action': action,
                    'Queue': content[2][i],
                    'Interface': content[4],
                    'Penalty': content[3][i],
                    'Paused': 0,
                    'MemberName': content[1]
                }
                data_returned = self.manager.send_action(dict)
        elif action == 'QueueRemove':
            event_queuelog = 'REMOVEMEMBER'
            for i in range(len(content[2])):
                dict = {
                    'Action': action,
                    'Queue': content[2][i],
                    'Interface': content[4],
                }
                data_returned = self.manager.send_action(dict)
        elif action == 'QueuePause':
            if content[6] == 'true':
                event_queuelog = 'PAUSEALL'
            elif content[6] == 'false':
                event_queuelog = 'UNPAUSEALL'
            dict = {
                'Action': action,
                'Interface': content[4],
                'Paused': content[6],
            }
            data_returned = self.manager.send_action(dict)
        elif action == 'dbput':
            family = content[0]
            key = content[1]
            value = content[2]
            data_returned = self.manager.dbput(family, key, value)
        elif action == 'originate':
            channel = content[0]
            exten = content[1]
            data_returned = self.manager.originate(
                channel,
                exten,
                context=content[2],
                caller_id=exten,
                priority=1,
                timeout='25000',
                variables=content[3])
        if action == 'QueueAdd' or action == 'QueueRemove' or action == 'QueuePause':
            dict = {
                'Action': 'QueueLog',
                'Queue': 'ALL',
                'Event': event_queuelog,
                'Uniqueid': 'MANAGER',
                'Interface': content[0]
            }
            if action == 'QueuePause':
                dict['Message'] = content[5]
            data_returned = self.manager.send_action(dict)
        return data_returned


class AmiManagerClient(AMIManagerConnector):

    def __init__(self):
        super(AmiManagerClient, self).__init__()

    def originate(self, channel, context, es_aplicacion, variables_de_canal, is_async,
                  aplication=None, exten=None, priority=None, timeout=None):

        content = {}
        content[0] = channel
        content[1] = exten
        content[2] = context
        content[3] = variables_de_canal
        content[4] = priority or 1
        content[5] = timeout or '25000'
        return self._ami_action('originate', content)

    def dbput(self, family, key, val):
        content = {}
        content[0] = family
        content[1] = key
        content[2] = val
        return self._ami_action('dbput', content)

    def dbget(self, family, key):
        return self.dbget(family, key)

    # TODO: Ver de donde sacar la key para enviar al manager
    def dbdeltree(self, family, key):
        return self.manager.dbdeltree(family, key)

    def queue_add(self, queue, interface, penalty, paused, member_name):
        content = {}
        content[2] = [queue]
        content[4] = content[0] = interface
        content[3] = [penalty]
        content[1] = member_name

        return self._ami_action('QueueAdd', content)

    def queue_remove(self, queue, interface):
        content = {}
        content[2] = [queue]
        content[4] = content[0] = interface

        return self._ami_action('QueueRemove', content)


class AMIManagerConnectorError(OmlError):

    def __init__(self, message, *args, **kwargs):
        super(AMIManagerConnectorError, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return (f'Error al utilizar AMIManagerConnector: {self.message}')
