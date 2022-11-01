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
from __future__ import unicode_literals

import json
from mock import patch

from django.utils.translation import gettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    SistemaExternoFactory, QueueMemberFactory
)
from ominicontacto_app.models import Campana, User


class APITest(OMLBaseTest):
    """ Tests para la api de Click2Call"""

    def setUp(self):
        super(APITest, self).setUp()

        self.sistema_externo = SistemaExternoFactory()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)

        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)
        self.client.login(username=usr_supervisor.username, password=PASSWORD)
        # Campaña
        bd_contacto = self.crear_base_datos_contacto(cant_contactos=3, columna_id_externo='id_ext')
        self.campana = self.crear_campana_manual(cant_contactos=3,
                                                 user=usr_supervisor,
                                                 bd_contactos=bd_contacto)
        self.campana.sistema_externo = self.sistema_externo
        self.campana.id_externo = 'c1'
        self.campana.estado = Campana.ESTADO_ACTIVA
        self.campana.save()

        QueueMemberFactory.create(member=self.agente, queue_name=self.campana.queue_campana)

        # self.queue = QueueFactory.create(campana=self.campana)

        self.contacto_1 = self.campana.bd_contacto.contactos.first()
        self.contacto_1.id_externo = 'c1'
        self.contacto_1.save()

        self.urls_api = {
            'AgentsCampaign': 'api_agents_campaign',
            'UpdateAgentsCampaign': 'api_update_agents_campaign',
            'ActiveAgents': 'api_active_agents',
        }

        self.post_update_agents_campaign = {
            "agents": [
                {
                    "agent_id": self.agente.pk,
                    "agent_penalty": "5"
                }
            ],
            "campaign_id": self.campana.pk
        }


class AddAgentsToCampaignTest(APITest):
    def test_obtener_agentes_de_campana(self):
        URL = reverse(self.urls_api['AgentsCampaign'], args=[self.campana.pk, ])
        response = self.client.get(URL, follow=True)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los agentes de forma exitosa'))

    def test_obtener_agentes_activos(self):
        URL = reverse(self.urls_api['ActiveAgents'])
        response = self.client.get(URL, follow=True)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se obtuvieron los agentes de forma exitosa'))

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.disconnect')
    @patch('ominicontacto_app.services.creacion_queue.ActivacionQueueService.activar')
    @patch('asterisk.manager.Manager.send_action')
    @patch('api_app.views.campaigns.add_agents_to_campaign.obtener_sip_agentes_sesiones_activas')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_actualizar_agentes_de_campana(
            self, connect, obtener_sip_agentes_sesiones_activas,
            send_action, activar, disconnect):
        obtener_sip_agentes_sesiones_activas.return_value = [self.agente.sip_extension]
        URL = reverse(self.urls_api['UpdateAgentsCampaign'])
        response = self.client.post(URL, json.dumps(self.post_update_agents_campaign),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se agregaron los agentes de forma exitosa a la campaña'))
