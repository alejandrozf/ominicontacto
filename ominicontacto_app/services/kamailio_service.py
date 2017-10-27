# -*- coding: utf-8 -*-

"""
Servicio para conexion base de datos de kamailio-debian lo importante en este módulo es la
inserción en subscriber de las cuentas sip
"""

from __future__ import unicode_literals

import psycopg2
from django.db import connection


class KamailioService():

    def crear_agente_kamailio(self, agente):
        """
        insert agente en subscriber
        """
        cursor = connection.cursor()

        try:
            sql = """INSERT INTO subscriber (id, username, password)
            VALUES (%(id)s, %(name)s, %(kamailiopass)s)
            """
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)

        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def update_agente_kamailio(self, agente):
        """
        update subscriber 
        """
        cursor = connection.cursor()

        try:
            sql = """UPDATE subscriber SET username=%(name)s,
                  password=%(kamailiopass)s
                  WHERE id=%(id)s"""
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)

        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def delete_agente_kamailio(self, agente):
        """
        delete registro en subscriber
        """
        cursor = connection.cursor()

        try:
            sql = """DELETE from subscriber WHERE username like %(username)s"""
            params = {
                'username': str(agente.sip_extension)
            }
            cursor.execute(sql, params)

        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()
