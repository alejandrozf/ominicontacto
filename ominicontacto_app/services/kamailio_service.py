# -*- coding: utf-8 -*-

"""
Servicio para conexion base de datos de kamailio-debian lo importante en este módulo es la
inserción en subscriber de las cuentas sip
"""

from __future__ import unicode_literals

import psycopg2


class KamailioService():

    def _conectar_base_datos(self):
        """
        Conexion con kamailio-debian
        Deberia sacarse ya que es la misma base de datos django
        :return: returna el connection y el cursor de la base kamailio-debian
        """
        connection = psycopg2.connect(database='kamailio', user='kamailio',
                                      password='kamailiorw', host='127.0.0.1',
                                      port='5432')
        cursor = connection.cursor()
        return connection, cursor

    def crear_agente_kamailio(self, agente):
        """
        insert agente en subscriber
        """
        connection, cursor = self._conectar_base_datos()

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
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def update_agente_kamailio(self, agente):
        """
        update subscriber 
        """
        connection, cursor = self._conectar_base_datos()

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
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def delete_agente_kamailio(self, agente):
        """
        delete registro en subscriber
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """DELETE from subscriber WHERE username like %(username)s"""
            params = {
                'username': str(agente.sip_extension)
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()
