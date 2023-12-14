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

import ldap3
import re
from constance import config as config_constance


def parse_ms_simple_user(username, dn):
    nodes = re.findall(r"(?i)(?<=DC=)[^,]+", dn)
    return '{0}@{1}'.format(username, '.'.join(nodes))


def parse_ldap_user(username):
    if not config_constance.EXTERNAL_AUTH_MS_SIMPLE_AUTH:
        return 'cn={0},{1}'.format(username, config_constance.EXTERNAL_AUTH_DN)
    return parse_ms_simple_user(username, config_constance.EXTERNAL_AUTH_DN)


def authenticate_in_ldap(username, password):
    authentication_ok = False
    service_error = False

    user = parse_ldap_user(username)
    server = ldap3.Server(config_constance.EXTERNAL_AUTH_SERVER, connect_timeout=5)
    conn = ldap3.Connection(server, user, password)
    try:
        conn.bind()
    except ldap3.core.exceptions.LDAPExceptionError:
        service_error = True

    authentication_ok = conn.bound
    return authentication_ok, service_error


"""
docker run --rm -p 10389:10389 -p 10636:10636 rroemhild/test-openldap
docker exec -it gracious_hermann sh

"""
