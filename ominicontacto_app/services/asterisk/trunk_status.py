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
from django.utils.translation import gettext as _
from ominicontacto_app.services.asterisk.asterisk_ami import AmiManagerClient


ENDPOINT_HEADER = 'Output:  Endpoint:  '
CONTACT_HEADER = 'Output:       Contact:  '


class TrunkStatusMonitor(object):
    """" Parsea respuestas del comando 'pjsip show endpoints' para obtener estados de troncales"""

    def __init__(self, ami_client=None):
        if ami_client is None:
            ami_client = AmiManagerClient()
        self.ami_client = ami_client

    def _set_unknown_status(self, trunk):
        trunk.status = _('Desconocido')

    def set_trunks_statuses(self, trunks):
        self.ami_client.connect()
        data, error = self.ami_client.pjsip_show_endpoints()
        if error:
            for trunk in trunks:
                self._set_unknown_status(trunk)
                return

        trunks_by_name = {}
        for trunk in trunks:
            trunks_by_name[trunk.nombre] = trunk
            trunk.status = _('Sin Datos')
        lines = data.splitlines()

        i = 12
        while i < len(lines):
            line = lines[i]
            if line.startswith(ENDPOINT_HEADER):
                data, next_i = self._get_endpoint_data(lines, line, i + 1)
                if self._is_trunk_data(data):
                    self._set_trunk_name_and_status(data, trunks_by_name)
            else:
                next_i = i + 1
            i = next_i

        self.ami_client.disconnect()

    def _get_endpoint_data(self, lines, first_line, i):
        key, value = self._parse_endpoint_line_data(first_line)
        data = {key: value}
        while i < len(lines):
            line = lines[i]
            if line.startswith(ENDPOINT_HEADER):
                return data, i
            key, value = self._parse_endpoint_line_data(line)
            if key is None:
                return data, i + 1
            data[key] = value
            i += 1
        return data, i

    def _parse_endpoint_line_data(self, line):
        line = [x for x in line.split(' ') if x != '']
        if len(line) > 2:
            return line[1], line[2:]
        return None, None

    def _is_trunk_data(self, data):
        return 'Contact:' in data

    def _set_trunk_name_and_status(self, data, trunks_by_name):
        contact = data['Contact:']
        name = contact[0].split('/')[0]
        if name in trunks_by_name and len(contact) > 2:
            trunks_by_name[name].status = contact[2]
