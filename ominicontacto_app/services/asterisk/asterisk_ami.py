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

import logging as _logging

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from django.conf import settings

logger = _logging.getLogger(__name__)


class AMIManagerConnector(object):
    """Establece la conexión AMI utilizando la librería pyst2, para manipular asterisk
    """

    def _ami_manager(self, action, content):
        error = False
        data_returned = ''
        manager = Manager()
        ami_manager_user = settings.ASTERISK['AMI_USERNAME']
        ami_manager_pass = settings.ASTERISK['AMI_PASSWORD']
        ami_manager_host = str(settings.ASTERISK_HOSTNAME)
        try:
            manager.connect(ami_manager_host)
            manager.login(ami_manager_user, ami_manager_pass)
            data_returned = self._ami_action(manager, action, content)
            manager.close()
        except ManagerSocketException as e:
            logger.exception("Error connecting to the manager: {0}".format(e.message))
            error = True
        except ManagerAuthException as e:
            logger.exception("Error logging in to the manager: {0}".format(e.message))
            error = True
        except ManagerException as e:
            logger.exception("Error {0}".format(e.message))
            error = True
        return data_returned, error

    def _ami_action(self, manager, action, content):
        if action == 'command':
            data_returned = manager.command(content).data
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
                data_returned = manager.send_action(dict)
        elif action == 'QueueRemove':
            event_queuelog = 'REMOVEMEMBER'
            for i in range(len(content[2])):
                dict = {
                    'Action': action,
                    'Queue': content[2][i],
                    'Interface': content[4],
                }
                data_returned = manager.send_action(dict)
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
            data_returned = manager.send_action(dict)
        elif action == 'dbput':
            family = content[0]
            key = content[1]
            value = content[2]
            data_returned = manager.dbput(family, key, value)
        elif action == 'originate':
            channel = content[0]
            exten = content[1]
            data_returned = manager.originate(
                channel,
                exten,
                context=content[2],
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
            data_returned = manager.send_action(dict)
        return data_returned
