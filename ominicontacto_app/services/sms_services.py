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