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

"""
Tests relacionados a inicializar_entorno
"""

from mock import patch
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.management.commands.inicializar_entorno import Command
from ominicontacto_app.models import AgenteProfile, SupervisorProfile


class TestsInicializarEntorno (OMLBaseTest):

    def setUp(self, *args, **kwargs):
        super(TestsInicializarEntorno, self).setUp(*args, **kwargs)
        admin = self.crear_administrador()
        admin.is_staff = True
        admin.save()

    @patch('redis.Redis.sadd')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.queue_add')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('ominicontacto_app.management.commands.inicializar_entorno.'
           'escribir_ruta_entrante_config')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionDeRutaSalienteEnAsterisk.regenerar_asterisk')
    @patch('configuracion_telefonia_app.regeneracion_configuracion_telefonia.'
           'SincronizadorDeConfiguracionTroncalSipEnAsterisk.regenerar_troncales')
    @patch('ominicontacto_app.services.creacion_queue.ActivacionQueueService.activar')
    @patch('ominicontacto_app.services.asterisk_service.ActivacionAgenteService.activar')
    def test_multiples_agentes(self, activar_agente, activar_queue, regenerar_troncales,
                               regenerar_asterisk, escribir_ruta_entrante_config,
                               obtener_sip_agentes_sesiones_activas, ami_connect,
                               queue_add, sadd):
        inicializar_entorno = Command()
        inicializar_entorno._crear_datos_entorno(False, 3, 2)
        activar_agente.assert_called()
        activar_queue.assert_called()
        regenerar_troncales.assert_called()
        regenerar_asterisk.assert_called()
        escribir_ruta_entrante_config.assert_called()
        obtener_sip_agentes_sesiones_activas.assert_called()
        ami_connect.assert_called()
        self.assertEqual(AgenteProfile.objects.count(), 3)
        self.assertEqual(SupervisorProfile.objects.count(), 4)  # 1 Admin, 1 Gerente, 2 Supervisor
