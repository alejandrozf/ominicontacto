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

from django.utils.translation import ugettext as _
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (
    SistemaExternoFactory, QueueMemberFactory
)
from ominicontacto_app.models import AgenteEnSistemaExterno, Campana


class Click2CallAPITest(OMLBaseTest):
    """ Tests para la api de Click2Call"""
    PWD = u'admin123'

    def setUp(self):

        self.sistema_externo = SistemaExternoFactory()
        self.sistema_externo_2 = SistemaExternoFactory()
        usr_supervisor = self.crear_user_supervisor(username='sup1')
        self.crear_supervisor_profile(usr_supervisor)
        usr_agente = self.crear_user_agente(username='agente1')
        self.agente = self.crear_agente_profile(usr_agente)
        self.client.login(username=usr_agente.username, password=self.PWD)
        self.agente_2 = self.crear_agente_profile()

        self.campana = self.crear_campana_manual(cant_contactos=3,
                                                 user=usr_supervisor)
        self.campana.sistema_externo = self.sistema_externo
        self.campana.id_externo = 'c1'
        self.campana.estado = Campana.ESTADO_ACTIVA
        self.campana.save()

        self.campana_2 = self.crear_campana_manual(cant_contactos=3,
                                                   user=usr_supervisor)
        self.campana_2.sistema_externo = self.sistema_externo
        self.campana_2.estado = Campana.ESTADO_ACTIVA
        self.campana_2.save()

        # queue_campana = QueueFactory(campana=self.campana)
        QueueMemberFactory.create(member=self.agente, queue_name=self.campana.queue_campana)
        QueueMemberFactory.create(member=self.agente_2, queue_name=self.campana_2.queue_campana)

        agente_externo_1 = AgenteEnSistemaExterno(agente=self.agente,
                                                  sistema_externo=self.sistema_externo,
                                                  id_externo_agente='id_ag_1')
        agente_externo_1.save()
        agente_externo_2 = AgenteEnSistemaExterno(agente=self.agente_2,
                                                  sistema_externo=self.sistema_externo_2,
                                                  id_externo_agente='id_ag_2')
        agente_externo_2.save()
        self.contacto_1 = self.campana.bd_contacto.contactos.first()
        self.contacto_1.id_externo = 'c1'
        self.contacto_1.save()

        bd_contacto = self.crear_base_datos_contacto(cant_contactos=3)
        self.contacto_2 = bd_contacto.contactos.first()

        self.post_data_oml = {
            'idCampaign': str(self.campana.id),
            'idAgent': str(self.agente.id),
            'idContact': str(self.contacto_1.id),
            'phone': '3511111111',
        }
        self.post_data_externo = {
            'idExternalSystem': str(self.sistema_externo.id),
            'idCampaign': str(self.campana.id_externo),
            'idAgent': 'id_ag_1',
            'idContact': str(self.contacto_1.id_externo),
            'phone': '35111111111',
        }

    def make_click2call_post(self, post_data):
        url = reverse('api_click2call')
        response = self.client.post(url, post_data)
        return response

    def test_oml_ids_campana_inexistente(self):
        self.post_data_oml['idCampaign'] = self.post_data_oml['idCampaign'] + '000'
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idCampaign', response.data['errors'])
        self.assertEqual(response.data['errors']['idCampaign'],
                         [_('Escoja una opción válida. Esa opción no está entre las disponibles.')])

    def test_oml_ids_agente_inexistente(self):
        self.post_data_oml['idAgent'] = self.post_data_oml['idAgent'] + '000'
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idAgent', response.data['errors'])
        self.assertEqual(response.data['errors']['idAgent'],
                         [_('Escoja una opción válida. Esa opción no está entre las disponibles.')])

    def test_oml_ids_contacto_inexistente_error(self):
        self.post_data_oml['idContact'] = self.post_data_oml['idContact'] + '000'
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idContact', response.data['errors'])
        self.assertEqual(response.data['errors']['idContact'],
                         [_('Escoja una opción válida. Esa opción no está entre las disponibles.')])

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_oml_ids_sin_contacto_ok(self, call_originate):
        call_originate.return_value = None
        self.post_data_oml.pop('idContact')
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'OK')

    def test_oml_ids_agente_no_en_campana(self):
        self.post_data_oml['idAgent'] = str(self.agente_2.id)
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idAgent', response.data['errors'])
        self.assertEqual(response.data['errors']['idAgent'],
                         [_('El agente no participa en la campaña.')])

    def test_oml_ids_contacto_no_en_campana(self):
        self.post_data_oml['idContact'] = str(self.contacto_2.id)
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idContact', response.data['errors'])
        self.assertEqual(response.data['errors']['idContact'],
                         [_('El contacto no corresponde a la campaña.')])

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_oml_ids_call_ok(self, call_originate):
        call_originate.return_value = None
        response = self.make_click2call_post(self.post_data_oml)
        self.assertEqual(response.data['status'], 'OK')

    def test_external_ids_sistema_externo_inexistente(self):
        self.post_data_externo['idExternalSystem'] = str(self.sistema_externo.id) + '000'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idExternalSystem', response.data['errors'])
        self.assertEqual(response.data['errors']['idExternalSystem'],
                         [_('Sistema externo inexistente.')])

    def test_external_ids_campana_inexistente(self):
        self.post_data_externo['idCampaign'] = self.post_data_externo['idCampaign'] + '000'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idCampaign', response.data['errors'])
        self.assertEqual(response.data['errors']['idCampaign'],
                         [_('Escoja una opción válida. Esa opción no está entre las disponibles.')])

    def test_external_ids_agente_inexistente(self):
        self.post_data_externo['idAgent'] = self.post_data_externo['idAgent'] + '000'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idAgent', response.data['errors'])
        self.assertEqual(response.data['errors']['idAgent'],
                         [_('El agente no corresponde al sistema externo.')])

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_external_ids_contacto_inexistente_ok(self, call_originate):
        call_originate.return_value = None
        self.post_data_externo['idContact'] = self.post_data_externo['idContact'] + '000'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'OK')

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_external_ids_sin_contacto_ok(self, call_originate):
        call_originate.return_value = None
        self.post_data_externo.pop('idContact')
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'OK')

    def test_external_ids_agente_no_en_sistema_externo(self):
        self.post_data_externo['idAgent'] = 'id_ag_2'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idAgent', response.data['errors'])
        self.assertEqual(response.data['errors']['idAgent'],
                         [_('El agente no corresponde al sistema externo.')])

    def test_external_ids_agente_no_en_campana(self):
        agente_externo = AgenteEnSistemaExterno(agente=self.agente_2,
                                                sistema_externo=self.sistema_externo,
                                                id_externo_agente='id_ag_2')
        agente_externo.save()
        self.post_data_externo['idAgent'] = 'id_ag_2'
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertIn('idAgent', response.data['errors'])
        self.assertEqual(response.data['errors']['idAgent'],
                         [_('El agente no participa en la campaña.')])

    @patch('ominicontacto_app.services.click2call.Click2CallOriginator.call_originate')
    def test_external_ids_call_ok(self, call_originate):
        call_originate.return_value = None
        response = self.make_click2call_post(self.post_data_externo)
        self.assertEqual(response.data['status'], 'OK')
