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
from __future__ import unicode_literals

from mock import patch
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    QueueMemberFactory, ContactoFactory, CampanaFactory, QueueFactory,
)

from api_app.services.calificacion_llamada import CalificacionLLamada
from django.urls import reverse

import json


class StatusCalificacionLlamadaTest(OMLBaseTest):
    def setUp(self):
        super(StatusCalificacionLlamadaTest, self).setUp()
        user = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(user)
        self.agente.grupo.obligar_calificacion = True
        self.client.login(username=user.username, password=PASSWORD)

        self.campana = CampanaFactory.create()
        QueueFactory(campana=self.campana)
        QueueMemberFactory.create(member=self.agente, queue_name=self.campana.queue_campana)
        self.contacto = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto)

    def get_call_data(self):
        call_data = {"id_campana": self.campana.id,
                     "campana_type": self.campana.type,
                     "telefono": "3512349992",
                     "call_id": '123456789',
                     "call_type": "4",
                     "id_contacto": self.contacto.id,
                     "rec_filename": "",
                     "call_wait_duration": ""}
        return call_data

    @patch('redis.Redis.hset')
    @patch('redis.Redis.expire')
    @patch('notification_app.notification.AgentNotifier.send_message')
    @patch('notification_app.notification.RedisStreamNotifier.send')
    def test_api_create_family(self, send, send_message, expire, hset):
        service = CalificacionLLamada()
        call_data = self.get_call_data()
        json_call_data = json.dumps(call_data)
        nombre_family = service._get_nombre_family(self.agente)
        service.create_family(self.agente, call_data, json_call_data, calificado=True,
                              gestion=False, id_calificacion=None)
        variables = {
            'NAME': self.agente.user.get_full_name(),
            'ID': self.agente.id,
            'CALLID': call_data['call_id'],
            'CAMPANA': call_data['id_campana'],
            'TELEFONO': call_data['telefono'],
            'CALIFICADA': 'TRUE',
            'CALLDATA': json_call_data,
            'GESTION': 'FALSE',
            'IDCALIFICACION': 'NONE'
        }
        expire.assert_called_with(nombre_family, 3600 * 24 * 4)
        hset.assert_called_with(nombre_family, mapping=variables)
        send.assert_called_with('calification', self.agente.id)

    @patch('redis.Redis.hget')
    def test_api_get_value(self, hget):
        service = CalificacionLLamada()
        nombre_family = service._get_nombre_family(self.agente)
        service.get_value(self.agente, 'CALIFICADA')
        hget.assert_called_with(nombre_family, 'CALIFICADA')

    @patch('redis.Redis.hgetall')
    def test_api_get_family(self, hgetall):
        service = CalificacionLLamada()
        nombre_family = service._get_nombre_family(self.agente)
        service.get_family(self.agente)
        hgetall.assert_called_with(nombre_family)

    @patch('redis.Redis.hgetall')
    def test_api_status_calificacion_llamada_calificada(self, hgetall):
        url = reverse('api_status_calificacion_llamada')
        service = CalificacionLLamada()
        nombre_family = service._get_nombre_family(self.agente)
        hgetall.return_value = {'CALIFICADA': 'TRUE'}
        response = self.client.post(url)
        hgetall.assert_called_with(nombre_family)
        self.assertEqual(response.json(), {'calificada': 'True'})

    @patch('redis.Redis.hgetall')
    def test_api_status_calificacion_llamada_no_calificada(self, hgetall):
        url = reverse('api_status_calificacion_llamada')
        service = CalificacionLLamada()
        nombre_family = service._get_nombre_family(self.agente)
        hgetall.return_value = {'CALIFICADA': 'FALSE', 'CALLDATA': 'SOME CALL DATA',
                                'GESTION': 'FALSE', 'IDCALIFICACION': 'NONE'}
        response = self.client.post(url)
        hgetall.assert_called_with(nombre_family)
        self.assertEqual(response.json(), {'calificada': 'False', 'calldata': 'SOME CALL DATA'})

    @patch('redis.Redis.hgetall')
    def test_api_status_calificacion_llamada_sin_datos(self, hgetall):
        url = reverse('api_status_calificacion_llamada')
        service = CalificacionLLamada()
        nombre_family = service._get_nombre_family(self.agente)
        hgetall.return_value = {}
        response = self.client.post(url)
        hgetall.assert_called_with(nombre_family)
        self.assertEqual(response.json(), {'calificada': 'True'})
