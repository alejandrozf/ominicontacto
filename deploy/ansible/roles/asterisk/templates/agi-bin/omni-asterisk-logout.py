#!{{ install_prefix }}virtualenv/bin/python
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

# este script es invocado como una tarea programada para desloguear a los agentes que no lo hayan
# hecho manualmente después de un determinado tiempo

import sys

from asterisk.manager import Manager, ManagerSocketException, ManagerAuthException, ManagerException

from config import configParser

from utiles import write_time_stderr

sys.stderr = open('{{ install_prefix }}log/agis-errors.log', 'a')


class CustomManager(Manager):
    # El código original de pyst2 no contenía los parámetros 'application' y 'data' en el momento
    # de desarrollar esta funcionalidad por lo que se hizo necesario customizar el método para
    # añadir estos parámetros (ver https://github.com/rdegges/pyst2/issues/41 )
    def originate(self, channel, exten, context='', priority='', timeout='', application='',
                  data='', caller_id='', async=False, account='', variables={}):
        """Originate a call"""

        cdict = {'Action': 'Originate'}
        cdict['Channel'] = channel
        cdict['Exten'] = exten
        if context:
            cdict['Context'] = context
        if priority:
            cdict['Priority'] = priority
        if timeout:
            cdict['Timeout'] = timeout
        if application:
            cdict['Application'] = application
        if data:
            cdict['Data'] = data
        if caller_id:
            cdict['CallerID'] = caller_id
        if async:
            cdict['Async'] = 'yes'
        if account:
            cdict['Account'] = account
        if variables:
            cdict['Variable'] = ['='.join(
                (str(key), str(value))) for key, value in variables.items()]

        response = self.send_action(cdict)

        return response


def logout_inactive_users(users_activity_list, manager):
    for activity_line in users_activity_list.splitlines():
        if activity_line.find("Unavailable") != -1:
            fields_activity = activity_line.split()
            id_user = fields_activity[0]
            sip_number = fields_activity[1].replace("(SIP/", "").replace(")", "")
            channel = 'Local/066LOGOUT@oml-agent-actions/n'
            exten = ''
            # context = ''
            # priority = ''
            application = 'hangup'
            # data = ''
            timeout = 5000
            caller_id = 'auto logout'
            variables = {'AUTOLOGOUT': '{0}-{1}'.format(sip_number, id_user)}
            manager.originate(channel, exten, application=application, timeout=timeout,
                              caller_id=caller_id, variables=variables)


manager = CustomManager()

ami_manager_user = configParser.get('OML', 'AMI_USER')
ami_manager_pass = configParser.get('OML', 'AMI_PASS')
ami_manager_host = configParser.get('OML', 'AMI_HOST')

try:
    manager.connect(ami_manager_host)
    manager.login(ami_manager_user, ami_manager_pass)
    users_activity_list = manager.command("queue show").data
    logout_inactive_users(users_activity_list, manager)
except ManagerSocketException as e:
    write_time_stderr("Error connecting to the manager: {0}".format(e.message))
    sys.exit(1)
except ManagerAuthException as e:
    write_time_stderr("Error logging in to the manager: {0}".format(e.message))
    sys.exit(1)
except ManagerException as e:
    write_time_stderr("Error {0}".format(e.message))
    sys.exit(1)
finally:
    manager.close()
