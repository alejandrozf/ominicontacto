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

from ominicontacto_app.tests.utiles import OMLBaseTest
from rest_framework import status
from rest_framework.authtoken.models import Token
from ominicontacto_app.models import User
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from ominicontacto_app.tests.utiles import PASSWORD
from ominicontacto_app.tests.factories import CampanaFactory
from whatsapp_app.tests.factories import LineaFactory, ConversacionFactory, MensajeFactory


class ReporteTest(OMLBaseTest):
    def setUp(self):
        super(ReporteTest, self).setUp()
        self.factory = RequestFactory()
        self.admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_reports_status_200(self):
        campana = CampanaFactory()
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reports_sent_messages(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        conversacion = ConversacionFactory.create(
            line=linea,
            campana=campana,
            date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
        )
        for i in range(5):
            MensajeFactory.create(conversation=conversacion, origen=conversacion.line.numero)
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['sent_messages'], 5)

    def test_reports_received_messages(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        conversacion = ConversacionFactory.create(
            line=linea,
            campana=campana,
            destination="5555555",
            date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
        )
        for i in range(5):
            MensajeFactory.create(conversation=conversacion, origen=conversacion.destination)
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['received_messages'], 5)

    def test_reports_interactions_started(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=True
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['interactions_started'], 5)

    def test_reports_attended_chats(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=False,
                atendida=True
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['attended_chats'], 5)

    def test_reports_not_attended_chats(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=False,
                atendida=False
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['not_attended_chats'], 5)

    def test_reports_inbound_chats_attended(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=False,
                atendida=True
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['inbound_chats_attended'], 5)

    def test_reports_inbound_chats_not_attended(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=False,
                atendida=False
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['inbound_chats_not_attended'], 5)

    def test_reports_inbound_chats_expired(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=False,
                expire=(timezone.now() - timezone.timedelta(days=1))
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['inbound_chats_expired'], 5)

    def test_reports_outbound_chats_attended(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=True,
                atendida=True
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['outbound_chats_attended'], 5)

    def test_reports_outbound_chats_not_attended(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=True,
                atendida=False
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['outbound_chats_not_attended'], 5)

    def test_reports_outbound_chats_expired(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=True,
                expire=(timezone.now() - timezone.timedelta(days=1))
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['outbound_chats_expired'], 5)

    def test_reports_outbound_chats_failed(self):
        campana = CampanaFactory()
        linea = LineaFactory(numero="0000000")
        start_date = timezone.now().strftime("%Y-%m-%d")
        end_date = (timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(5):
            ConversacionFactory.create(
                line=linea,
                campana=campana,
                date_last_interaction=timezone.now().astimezone(timezone.get_current_timezone()),
                saliente=True,
                error=True
            )
        url = reverse('whatsapp_app:whatsapp_reports')
        params = {'campaing': campana.pk, 'start_date': start_date, 'end_date': end_date}
        self.client.login(username=self.admin.user.username, password=PASSWORD)
        response = self.client.get(url, params)
        data = response.data['data']
        self.assertEqual(data['outbound_chats_failed'], 5)
