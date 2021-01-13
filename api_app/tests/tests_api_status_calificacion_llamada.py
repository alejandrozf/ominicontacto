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

    def get_dict_status_calificacion_llamada(self, call_data, json_call_data, calificada):
        if calificada is True:
            calificada = 'TRUE'
        else:
            calificada = 'FALSE'
        dict_status = {
            'NAME': self.agente.user.get_full_name(),
            'ID': str(self.agente.id),
            'CALLID': call_data['call_id'],
            'CAMPANA': str(call_data['id_campana']),
            'TELEFONO': call_data['telefono'],
            'CALIFICADA': calificada,
            'CALLDATA': json_call_data,
        }
        return dict_status

    def status_calificacion_llamada(self):
        url = reverse('api_status_calificacion_llamada')
        redis = CalificacionLLamada()
        post_data = redis.get_family(self.agente)
        response = self.client.post(url, post_data)
        return response

    def test_api_creacion_family_redis_calificacion_llamada(self):
        call_data = self.get_call_data()
        json_call_data = json.dumps(call_data)

        data = self.get_dict_status_calificacion_llamada(call_data, json_call_data, True)
        family = CalificacionLLamada()
        family.create_family(self.agente, call_data, json_call_data,
                             calificado=True)
        self.assertEqual(data, family.get_family(self.agente))

    def test_api_status_llamada_sin_calificar(self):
        call_data = self.get_call_data()
        json_call_data = json.dumps(call_data)
        family = CalificacionLLamada()
        family.create_family(self.agente, call_data, json_call_data,
                             calificado=False)
        response = self.status_calificacion_llamada()
        self.assertEqual(response.data['calificada'], 'False')

    def test_api_status_llamada_calificada(self):
        call_data = self.get_call_data()
        json_call_data = json.dumps(call_data)
        family = CalificacionLLamada()
        family.create_family(self.agente, call_data, json_call_data,
                             calificado=True)
        response = self.status_calificacion_llamada()
        self.assertEqual(response.data['calificada'], 'True')
        data = self.get_dict_status_calificacion_llamada(call_data,
                                                         json_call_data, calificada=True)
        self.assertEqual(data, family.get_family(self.agente))
