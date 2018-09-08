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

"""
Servicio para conexion base de datos de kamailio-debian lo importante en este módulo es la
inserción en subscriber de las cuentas sip
"""

from __future__ import unicode_literals

from django.db import connection


class KamailioService():

    def crear_agente_kamailio(self, agente):
        """
        insert agente en subscriber
        """
        with connection.cursor() as cursor:
            sql = """INSERT INTO subscriber (id, username, password)
            VALUES (%(id)s, %(name)s, %(kamailiopass)s)
            """
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)

    def update_agente_kamailio(self, agente):
        """
        update subscriber
        """

        with connection.cursor() as cursor:
            sql = """UPDATE subscriber SET username=%(name)s,
                  password=%(kamailiopass)s
                  WHERE id=%(id)s"""
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)
            row = cursor.fetchone()

        return row

    def delete_agente_kamailio(self, agente):
        """
        delete registro en subscriber
        """

        with connection.cursor() as cursor:
            sql = """DELETE from subscriber WHERE username like %(username)s"""
            params = {
                'username': str(agente.sip_extension)
            }
            cursor.execute(sql, params)
