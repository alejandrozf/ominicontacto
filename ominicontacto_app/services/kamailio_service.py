# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import psycopg2


class KamailioService():

    def _conectar_base_datos(self):
        connection = psycopg2.connect(database='kamailio', user='kamailio',
                                      password='kamailiorw', host='127.0.0.1',
                                      port='5432')
        cursor = connection.cursor()
        return connection, cursor

    def crear_agente_kamailio(self, agente):
        """
        crear usuario
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """INSERT INTO subscriber (id, username, password, ha1, ha1b)
            VALUES (%(id)s, %(name)s, %(kamailiopass)s, %(ha1)s, %(ha1)s)
            """
            params = {
                'id': agente.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password,
                'ha1': "MD5('{0}::{1}')".format(agente.sip_extension,
                                                agente.sip_password)
            }
            cursor.execute(sql, params)
            print cursor.query
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def update_agente_kamailio(self, agente):
        """
        crear usuario
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """UPDATE subscriber SET username=%(name)s,
                  password=%(kamailiopass)s, ha1=%(ha1)s, ha1b=%(ha1)s
                  WHERE id=%(id)s"""
            params = {
                'id': agente.id,
                'name': agente.sip_extension,
                'kamailiopass': agente.sip_password,
                'ha1': "MD5('{0}::{1}')".format(agente.sip_extension,
                                                agente.sip_password)
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def crear_queue_kamailio(self, queue):
        """
        crear usuario
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """INSERT INTO queue_table (name, timeout, retry, maxlen,
                  wrapuptime, servicelevel, strategy, eventmemberstatus,
                  eventwhencalled, weight, ringinuse, setinterfacevar) values
                  (%(name)s, %(timeout)s, %(retry)s, %(maxlen)s, %(wrapuptime)s,
                  %(servicelevel)s, %(strategy)s, %(eventmemberstatus)s,
                  %(eventwhencalled)s, %(weight)s, %(ringinuse)s,
                  %(setinterfacevar)s)"""
            params = {
                'name': queue.name,
                'timeout': queue.timeout,
                'retry': queue.retry,
                'maxlen': queue.maxlen,
                'wrapuptime': queue.wrapuptime,
                'servicelevel': queue.servicelevel,
                'strategy': queue.strategy,
                'eventmemberstatus': queue.eventmemberstatus,
                'eventwhencalled': queue.eventwhencalled,
                'weight': queue.weight,
                'ringinuse': queue.ringinuse,
                'setinterfacevar': queue.setinterfacevar
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

    def crear_queue_member_kamailio(self, queue_member):
        """
        crear usuario
        """
        connection, cursor = self._conectar_base_datos()

        try:
            sql = """INSERT INTO queue_member_table (membername, queue_name,
                  interface, penalty, paused) values
                  (%(membername)s, %(queue_name)s, %(interface)s, %(penalty)s,
                  %(paused)s)"""
            params = {
                'membername': queue_member.member.user.get_full_name(),
                'queue_name': queue_member.queue.name,
                'interface': queue_member.interface,
                'penalty': queue_member.penalty,
                'paused': queue_member.paused
            }
            cursor.execute(sql, params)
            connection.commit()
            connection.close()
        except psycopg2.DatabaseError, e:
            print "error base de datos"
            print e
            connection.close()

