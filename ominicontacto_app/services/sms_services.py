# -*- coding: utf-8 -*-

"""Servicio para el manejo de los sms enviados y recibidos a traves de dinstar"""

from __future__ import unicode_literals

from django.db import connection
from ominicontacto_app.models import MensajeRecibido


class SmsManager():

    def obtener_mensajes_recibidos_por_remitente(self):
        mensajes_recibidos = []
        for mensaje in MensajeRecibido.objects.mensaje_recibido_por_remitente():
            mensajes_recibidos.append(MensajeRecibido.objects.
                                      mensaje_remitente_fecha(mensaje['remitente'],
                                        mensaje['timestamp__max']))
        return mensajes_recibidos

    def obtener_mensaje_enviado_recibido(self, remitente):

        cursor = connection.cursor()
        sql = """select timestamp, remitente, destinatario, content
                 from mensaje_enviado where destinatario like %(remitente)s
                 union select timestamp, remitente, destinatario, content
                 from mensaje_recibido where remitente like concat('%%',
                 substring(%(remitente)s from 7 for 50)) order by timestamp
        """
        params = {
            'remitente': remitente,
        }
        cursor.execute(sql, params)
        values = cursor.fetchall()
        return values

    def armar_json_mensajes_recibidos_enviados(self, mensajes):

        lista_mensajes = []

        for mensaje in mensajes:
            mensaje_dict = {
                'timestamp': mensaje[0],
                'remitente':  mensaje[1],
                'destinatario': mensaje[2],
                'content': mensaje[3]
            }
            lista_mensajes.append(mensaje_dict)

        return lista_mensajes

    def armar_json_mensajes_recibidos_por_remitente(self, mensajes):

        lista_mensajes = []

        for mensaje in mensajes:
            mensaje_dict = {
                'id': mensaje.id,
                'remitente':  mensaje.remitente,
                'content': mensaje.content
            }
            lista_mensajes.append(mensaje_dict)

        return lista_mensajes