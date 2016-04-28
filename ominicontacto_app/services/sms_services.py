# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import connection


class SmsManager():

    def obtener_ultimo_mensaje_por_numero(self):

        cursor = connection.cursor()
        sql = """select timestamp, number, content
                 from mensaje_recibido
                 where timestamp = (select max(timestamp)
                 from mensaje_recibido as m
                 where m.number = mensaje_recibido.number)
        """
        cursor.execute(sql)
        values = cursor.fetchall()
        return values

    def armar_json_mensajes_recibidos(self, mensajes):

        lista_mensajes = []

        for mensaje in mensajes:
            mensaje_dict = {
                'timestamp': mensaje[0],
                'number':  mensaje[1],
                'content': mensaje[2]
            }
            lista_mensajes.append(mensaje_dict)

        json = {
            'mensajes': lista_mensajes
        }
        return json
