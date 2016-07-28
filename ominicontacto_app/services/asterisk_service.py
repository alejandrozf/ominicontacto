# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import MySQLdb

from django.conf import settings


class AsteriskService():

    def _conectar_base_datos(self):
        connection = MySQLdb.connect(
            db=settings.DATABASE_MYSQL_ASTERISK['BASE'],
            user=settings.DATABASE_MYSQL_ASTERISK['USER'],
            passwd=settings.DATABASE_MYSQL_ASTERISK['PASSWORD'],
            host=settings.DATABASE_MYSQL_ASTERISK['HOST']
        )
        cursor = connection.cursor()
        return connection, cursor

    def insertar_cola_asterisk(self, queue):
        """
        insert cola en asterisk
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """INSERT INTO miscdests (description, destdial) values
                  (%(description)s, %(destdial)s)"""
            params = {
                'description': queue.name,
                'destdial': '0077' + str(queue.queue_asterisk)
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except MySQLdb.DatabaseError, e:
            print "error base de datos"
            connection.close()

    def delete_cola_asterisk(self, queue):
        """
        delete cola en asterisk
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """DELETE FROM miscdests WHERE description=%(description)s"""
            params = {
                'description': queue.name
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except MySQLdb.DatabaseError, e:
            print "error base de datos"
            connection.close()
