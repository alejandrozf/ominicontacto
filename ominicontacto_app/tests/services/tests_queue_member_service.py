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

from ominicontacto_app.services.queue_member_service import QueueMemberService
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (CampanaFactory, QueueFactory, )


class QueueMemberServiceTests(OMLBaseTest):

    def setUp(self):
        super(QueueMemberServiceTests, self).setUp()
        self.campana1 = CampanaFactory.create()
        self.campana2 = CampanaFactory.create()
        self.queue = QueueFactory.create(campana=self.campana1)
        self.queue2 = QueueFactory.create(campana=self.campana2)
        self.agente1 = self.crear_agente_profile()
        self._hacer_miembro(self.agente1, self.campana1)
        self._hacer_miembro(self.agente1, self.campana2)
        self.agente2 = self.crear_agente_profile()
        self._hacer_miembro(self.agente2, self.campana1)
        self.agente3 = self.crear_agente_profile()

    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('redis.Redis.srem')
    @patch('redis.Redis.keys')
    @patch('redis.Redis.delete')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_eliminar_agente_de_colas_asignadas(
            self, connect, delete, keys, srem,
            obtener_sip_agentes_sesiones_activas):
        keys.return_value = []
        service = QueueMemberService()
        self.assertEqual(self.agente1.queue_set.count(), 2)
        keys.return_value = ['OML:CAMPAIGN-AGENTS:1']
        service.eliminar_agente_de_colas_asignadas(self.agente1)
        connect.assert_called()
        obtener_sip_agentes_sesiones_activas.assert_called()
        keys.assert_called_with('OML:CAMPAIGN-AGENTS:*')
        delete.assert_called_with('OML:AGENT-CAMPAIGNS:' + str(self.agente1.id))
        srem.assert_called_with('OML:CAMPAIGN-AGENTS:1', self.agente1.id)
        self.assertEqual(self.agente1.queue_set.count(), 0)

    @patch('ominicontacto_app.services.queue_member_service.QueueMemberService'
           '._remover_agente_cola_asterisk')
    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('redis.Redis.srem')
    @patch('redis.Redis.keys')
    @patch('redis.Redis.delete')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_eliminar_agente_conectado_de_colas_asignadas(
            self, connect, delete, keys, srem,
            obtener_sip_agentes_sesiones_activas, _remover_agente_cola_asterisk):
        obtener_sip_agentes_sesiones_activas.return_value = [self.agente1.sip_extension, ]
        keys.return_value = []
        service = QueueMemberService()
        self.assertEqual(self.agente1.queue_set.count(), 2)
        keys.return_value = ['OML:CAMPAIGN-AGENTS:1']
        service.eliminar_agente_de_colas_asignadas(self.agente1)
        connect.assert_called()
        obtener_sip_agentes_sesiones_activas.assert_called()
        keys.assert_called_with('OML:CAMPAIGN-AGENTS:*')
        delete.assert_called_with('OML:AGENT-CAMPAIGNS:' + str(self.agente1.id))
        self.assertEqual(self.agente1.queue_set.count(), 0)
        _remover_agente_cola_asterisk.assert_has_calls([call(self.campana1, self.agente1),
                                                        call(self.campana2, self.agente1)],
                                                       any_order=True)
        srem.assert_called_with('OML:CAMPAIGN-AGENTS:1', self.agente1.id)

    @patch('ominicontacto_app.services.queue_member_service.QueueMemberService'
           '._remover_agente_cola_asterisk')
    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('redis.Redis.srem')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_eliminar_agentes_de_cola(
            self, connect, srem,
            obtener_sip_agentes_sesiones_activas, _remover_agente_cola_asterisk):
        self.assertEqual(self.agente1.queue_set.count(), 2)
        self.assertEqual(self.agente2.queue_set.count(), 1)
        obtener_sip_agentes_sesiones_activas.return_value = [self.agente2.sip_extension, ]
        service = QueueMemberService()
        service.eliminar_agentes_de_cola(self.campana1, (self.agente1, self.agente2))
        connect.assert_called()
        obtener_sip_agentes_sesiones_activas.assert_called()
        # Se eliminan de la lista de campañas del agente en Redis
        srem.assert_has_calls([
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente1.id), self.campana1.id),
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente2.id), self.campana1.id)],
            any_order=True)
        # Se eliminaron los QueueMember asociados
        self.assertEqual(self.agente1.queue_set.count(), 1)
        self.assertEqual(self.agente2.queue_set.count(), 0)
        # Se remueve de la cola de asterisk el agente conectado
        _remover_agente_cola_asterisk.assert_called_with(self.campana1, self.agente2)

    @patch('ominicontacto_app.services.queue_member_service.QueueMemberService'
           '._adicionar_agente_cola_asterisk')
    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('redis.Redis.sadd')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_agregar_agentes_en_cola(
        self, connect, sadd, obtener_sip_agentes_sesiones_activas, _adicionar_agente_cola_asterisk
    ):
        self.assertEqual(self.agente3.queue_set.count(), 0)
        obtener_sip_agentes_sesiones_activas.return_value = [self.agente2.sip_extension, ]
        service = QueueMemberService()
        penalties = {self.agente2.id: 3, self.agente3.id: 4}
        service.agregar_agentes_en_cola(self.campana2, [self.agente2, self.agente3], penalties)
        obtener_sip_agentes_sesiones_activas.assert_called()
        # Se crean los QueueMember
        id_campana = self.campana2.get_queue_id_name()
        queue_member_2 = self.agente2.campana_member.get(id_campana=id_campana, penalty=3)
        self.agente3.campana_member.get(id_campana=id_campana, penalty=4)
        # Se agregan a la lista de campañas del agente en Redis
        sadd.assert_has_calls([
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente2.id), self.campana2.id),
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente3.id), self.campana2.id)],
            any_order=True)
        connect.assert_called()
        # Se agrega a la cola de asterisk el agente conectado
        _adicionar_agente_cola_asterisk.assert_called_with(
            self.agente2, queue_member_2, self.campana2)

    @patch('ominicontacto_app.services.queue_member_service.obtener_sip_agentes_sesiones_activas')
    @patch('redis.Redis.sadd')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_agregar_agentes_en_cola_sin_penalties(
        self, connect, sadd, obtener_sip_agentes_sesiones_activas
    ):
        self.assertEqual(self.agente3.queue_set.count(), 0)
        obtener_sip_agentes_sesiones_activas.return_value = []
        service = QueueMemberService()
        service.agregar_agentes_en_cola(self.campana2, [self.agente2, self.agente3])
        obtener_sip_agentes_sesiones_activas.assert_called()
        # Se crean los QueueMember
        id_campana = self.campana2.get_queue_id_name()
        self.agente2.campana_member.get(id_campana=id_campana, penalty=0)
        self.agente3.campana_member.get(id_campana=id_campana, penalty=0)
        # Se agregan a la lista de campañas del agente en Redis
        sadd.assert_has_calls([
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente2.id), self.campana2.id),
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente3.id), self.campana2.id)],
            any_order=True)
        connect.assert_called()

    @patch('redis.Redis.sadd')
    def test_agregar_agente_a_campanas(self, sadd):
        service = QueueMemberService(conectar_ami=False)
        service.agregar_agente_a_campanas(self.agente3, [self.campana1, self.campana2])

        self.assertEqual(self.agente3.queue_set.count(), 2)
        id_campana1 = self.campana1.get_queue_id_name()
        id_campana2 = self.campana2.get_queue_id_name()
        # Se crean los QueueMember
        self.agente3.campana_member.get(id_campana=id_campana1, penalty=0)
        self.agente3.campana_member.get(id_campana=id_campana2, penalty=0)
        # Se agregan a la lista de campañas del agente en Redis
        sadd.assert_has_calls([
            call('OML:AGENT-CAMPAIGNS:' + str(self.agente3.id), *[self.campana1.id,
                                                                  self.campana2.id]),
            call('OML:CAMPAIGN-AGENTS:' + str(self.campana2.id), self.agente3.id),
            call('OML:CAMPAIGN-AGENTS:' + str(self.campana1.id), self.agente3.id)
        ], any_order=True)
