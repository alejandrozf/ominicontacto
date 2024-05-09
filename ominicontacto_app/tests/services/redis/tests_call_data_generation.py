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

from mock import patch

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
        self.tipo_llamada = 3

    def generar_logs_llamada(self, min_duracion):
        duracion = min_duracion
        for evento in CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL:
            LlamadaLogFactory(campana_id=self.campana1.id, bridge_wait_time=duracion,
                              agente_id=self.agente_id, event=evento,
                              tipo_llamada=self.tipo_llamada)
            duracion += 1

    @patch('redis.Redis.hset')
    def test_regenerar_eventos_por_campaña(self, redis_hset):
        cantidad = 3
        for i in range(cantidad):
            self.generar_logs_llamada(5)
        generador = CallDataGenerator(create_redis_connection())
        generador.regenerar_eventos_por_campana()
        key = CallDataGenerator.CALLDATA_CAMP_KEY.format(self.campana1.id)
        eventos = {}
        for evento in CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL:
            key_evento = f'CALLTYPE:{self.tipo_llamada}:{evento}'
            eventos[key_evento] = cantidad
        redis_hset.assert_called_with(key, mapping=eventos)

    @patch('redis.Redis.rpush')
    def test_regenerar_wait_times_y_sla(self, sadd):
        min_duracion = 5
        self.generar_logs_llamada(min_duracion)
        max_duracion = min_duracion + len(CallDataGenerator.EVENTOS_FIN_CONEXION_ORIGINAL) - 1

        generador = CallDataGenerator(create_redis_connection())
        generador.regenerar_wait_times()
        args, kwargs = sadd.call_args
        key = args[0]
        duraciones_registradas = list(args[1:len(args)])
        self.assertEqual(key, generador.CALLDATA_WAIT_KEY.format(self.campana1.id))
        duraciones_esperadas = list(range(5, max_duracion + 1))
        self.assertEqual(len(duraciones_registradas), len(duraciones_esperadas))
        duraciones_esperadas.sort()
        duraciones_registradas.sort()
        self.assertEqual(duraciones_registradas, duraciones_esperadas)
