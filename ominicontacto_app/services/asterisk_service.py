# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import MySQLdb


class AsteriskService():

    def _conectar_base_datos(self):
        connection = MySQLdb.connect(db='asterisk', user='omnileads',
                                     passwd='admin123', host='172.16.20.222'
                                     )
        cursor = connection.cursor()
        return connection, cursor

    def crear_agente_kamailio(self, queue):
        """
        crear usuario
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
