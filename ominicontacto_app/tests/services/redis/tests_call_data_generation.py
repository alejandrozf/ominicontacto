# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from mock import patch, call

from ominicontacto_app.services.redis.call_data_generation import CallDataGenerator
from ominicontacto_app.services.redis.connection import create_redis_connection
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (LlamadaLogFactory, CampanaFactory, QueueFactory, )


class CallDataGeneratorTests(OMLBaseTest):
    omitir_actualizar_permisos = True

    def setUp(self):
        super(CallDataGeneratorTests, self).setUp()
        # Crear campanas
        self.campana1 = CampanaFactory.create()
        self.campana2 = CampanaFactory.create()
        self.sla = 10
        self.queue = QueueFactory.create(campana=self.campana1, servicelevel=self.sla)
        self.queue2 = QueueFactory.create(campana=self.campana2, servicelevel=self.sla)
        self.agente_id = 14

    def generar_logs_llamada(self, min_duracion):
        duracion = min_duracion
        for evento in CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL:
            LlamadaLogFactory(campana_id=self.campana1.id, bridge_wait_time=duracion,
                              agente_id=self.agente_id, event=evento)
            duracion += 1

    @patch('redis.Redis.set')
    def test_regenerar_eventos_por_campaña(self, redis_set):
        cantidad = 3
        for i in range(cantidad):
            self.generar_logs_llamada(5)
        generador = CallDataGenerator(create_redis_connection())
        generador.regenerar_eventos_por_campaña()

        call_list = [(x[0]) for x in redis_set.call_args_list]
        for evento in CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL:
            key = generador.get_camp_key(self.campana1.id, evento)
            self.assertIn((key, cantidad), call_list)

    @patch('redis.Redis.set')
    def test_regenerar_eventos_por_agente(self, redis_set):
        cantidad = 3
        for i in range(cantidad):
            self.generar_logs_llamada(5)
        generador = CallDataGenerator(create_redis_connection())
        generador.regenerar_eventos_por_agente()

        call_list = [(x[0]) for x in redis_set.call_args_list]
        for evento in CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL:
            key = generador.get_agent_key(self.agente_id, evento)
            self.assertIn((key, cantidad), call_list)

    @patch('redis.Redis.hset')
    @patch('redis.Redis.sadd')
    def test_regenerar_wait_times_y_sla(self, sadd, hset):
        min_duracion = 5
        self.generar_logs_llamada(min_duracion)
        max_duracion = min_duracion + len(CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL) - 1

        generador = CallDataGenerator(create_redis_connection())
        generador.regenerar_wait_times_y_sla()
        args, kwargs = sadd.call_args
        key = args[0]
        duraciones = args[1:len(args)]
        self.assertEqual(key, generador.get_wait_time_key(self.campana1.id))
        self.assertEqual(set(duraciones), set(range(5, max_duracion + 1)))
        args, kwargs = hset.call_args
        key = args[0]
        self.assertEqual(key, generador.get_sla_key(self.campana1.id))
        stats = {
            'OK': self.sla + 1 - min_duracion,
            'BAD': max_duracion - self.sla,
            'SUM': sum(range(min_duracion, max_duracion + 1)),
            'MAX': max_duracion
        }
        self.assertEqual(kwargs['mapping'], stats)
