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

import json
from mock import patch

from django.utils.translation import gettext as _
from django.urls import reverse
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    SistemaExternoFactory, QueueMemberFactory
)
from ominicontacto_app.models import Campana, User, AgenteProfile


class APITest(OMLBaseTest):
    """ Tests para la api de Click2Call"""

    def setUp(self):
        super(APITest, self).setUp()

        self.sistema_externo = SistemaExternoFactory()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(user=usr_supervisor, rol=User.SUPERVISOR)

        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)
        usr_agente2 = self.crear_user_agente(username='agente2')
        self.agente2 = self.crear_agente_profile(usr_agente2)
        usr_agente3 = self.crear_user_agente(username='agente3')
        self.agente3 = self.crear_agente_profile(usr_agente3)
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
        QueueMemberFactory.create(member=self.agente2, queue_name=self.campana.queue_campana)

        # self.queue = QueueFactory.create(campana=self.campana)

        self.contacto_1 = self.campana.bd_contacto.contactos.first()
        self.contacto_1.id_externo = 'c1'
        self.contacto_1.save()

        self.urls_api = {
            'AgentsCampaign': 'api_agents_campaign',
            'UpdateAgentsCampaign': 'api_update_campaign_agents',
            'ActiveAgents': 'api_active_agents',
        }

        self.post_update_agents_campaign = {
            "agents": [
                {
                    "agent_id": self.agente.pk,
                    "agent_penalty": "5"
                },
                {
                    "agent_id": self.agente3.pk,
                    "agent_penalty": "3"
                },
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

    @patch('ominicontacto_app.services.queue_member_service.QueueMemberService.'
           'agregar_agentes_en_cola')
    @patch('ominicontacto_app.services.queue_member_service.QueueMemberService.'
           'eliminar_agentes_de_cola')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.disconnect')
    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AmiManagerClient.connect')
    def test_actualizar_agentes_de_campana(
            self, ami_connect, ami_disconnect, eliminar_agentes_de_cola,
            agregar_agentes_en_cola):
        URL = reverse(self.urls_api['UpdateAgentsCampaign'])
        response = self.client.post(URL, json.dumps(self.post_update_agents_campaign),
                                    format='json', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'SUCCESS')
        self.assertEqual(
            response_json['message'],
            _('Se agregaron los agentes de forma exitosa a la campaña'))
        ami_connect.assert_called()
        ami_disconnect.assert_called()
        args, kwargs = eliminar_agentes_de_cola.call_args
        self.assertEqual(self.campana, args[0])
        query_agente2 = AgenteProfile.objects.filter(id=self.agente2.id)
        self.assertEqual(set(args[1]), set(query_agente2))
        args, kwargs = agregar_agentes_en_cola.call_args
        self.assertEqual(self.campana, args[0])
        self.assertEqual(set((self.agente, self.agente3, )), set(args[1]))
        penalties = {self.agente.id: 5, self.agente3.id: 3}
        self.assertEqual(penalties, args[2])
