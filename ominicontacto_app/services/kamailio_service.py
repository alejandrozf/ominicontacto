# -*- coding: utf-8 -*-

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
	añado timestamp en columna email-address, para no alterar la tabla
        """
        with connection.cursor() as cursor:
            sql = """INSERT INTO subscriber (id, email_address, username, password)
            VALUES (%(id)s, %(timestamp)s, %(name)s, %(kamailiopass)s)
            """
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
		'timestamp': agente.timestamp,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)

    def update_agente_kamailio(self, agente):
        """
        update subscriber 
        """

        with connection.cursor() as cursor:
            sql = """UPDATE subscriber SET username=%(name)s,
                  password=%(kamailiopass)s,
		  email_address=%(timestamp)s
                  WHERE id=%(id)s"""
            params = {
                'id': agente.user.id,
                'name': agente.sip_extension,
		'timestamp': agente.timestamp,
                'kamailiopass': agente.sip_password
            }
            cursor.execute(sql, params)
            #row = cursor.fetchone()

        #return row

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
