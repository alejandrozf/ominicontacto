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

"""Tests para los reportes de resultados de una campaña"""

from __future__ import unicode_literals

from mock import patch
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string

# Reportes APP
from reportes_app.reportes.reporte_llamados_contactados_csv import (
    NO_CONECTADO_DESCRIPCION)
from reportes_app.reportes.reporte_resultados import (
    ReporteDeResultadosDeCampana)
from reportes_app.tests.tests_reportes_campanas import BaseTestDeReportes
# Ominicontacto APP
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.models import Campana


class APITest(OMLBaseTest):
    """API para generacion de CSV"""

    def setUp(self):
        super(APITest, self).setUp()
        self.campana = Campana.objects.first()
        usr_sup = self.crear_user_supervisor(username='sup1')
        self.client.login(username=usr_sup.username, password=PASSWORD)
        self.taskId = get_random_string(8)
        self.response_ok = {
            u'status': u'OK',
            u'msg': _(u'Exportación de CSV en proceso'),
            u'id': self.taskId,
        }
        self.post_data = {
            'campanaId': self.campana.pk,
            'taskId': self.taskId,
        }

    def tearDown(self):
        super(APITest, self).tearDown()
        self.client.logout()


class ReporteDeResultadosTests(APITest, BaseTestDeReportes):

    def test_usuario_no_logueado_no_accede_reporte_de_resultados(self):
        self.client.logout()
        url = reverse('reporte_de_resultados', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_usuario_logueado_accede_reporte_de_resultados(self):
        url = reverse('reporte_de_resultados', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_de_resultados.html')

    def test_contactos_en_reporte_de_resultados(self):
        reporte = ReporteDeResultadosDeCampana(self.campana_activa)
        self.assertTrue(
            self.contacto_calificado_gestion.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[
            self.contacto_calificado_gestion.id]
        self.assertEqual(
            contactacion['calificacion'],
            self.opcion_calificacion_gestion.nombre)

        self.assertTrue(
            self.contacto_calificado_no_accion.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[
            self.contacto_calificado_no_accion.id]
        self.assertEqual(
            contactacion['calificacion'],
            self.opcion_calificacion_noaccion.nombre)

        self.assertTrue(
            self.contacto_no_calificado.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_no_calificado.id]
        self.assertIsNone(contactacion['calificacion'])
        self.assertEqual(contactacion['contactacion'], _('Contactado'))
        self.assertTrue(self.contacto_no_atendido.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_no_atendido.id]
        self.assertIsNone(contactacion['calificacion'])
        self.assertEqual(
            contactacion['contactacion'], NO_CONECTADO_DESCRIPCION['NOANSWER'])

    def test_contactos_en_reporte_de_resultados_paginado(self):
        reporte_1 = ReporteDeResultadosDeCampana(self.campana_activa, page_number=1, page_size=1)
        self.assertTrue(reporte_1.is_paginated)
        self.assertEqual(1, len(reporte_1.contactaciones.values()))
        reporte_2 = ReporteDeResultadosDeCampana(self.campana_activa, page_number=1, page_size=2)
        self.assertEqual(2, len(reporte_2.contactaciones.values()))
        reporte_5 = ReporteDeResultadosDeCampana(self.campana_activa, page_number=1, page_size=5)
        self.assertGreaterEqual(5, len(reporte_5.contactaciones.values()))

    @patch('threading.Thread')
    def test_generar_resultados_de_base_csv(self, Thread):
        self.client.login(username='sup1', password=PASSWORD)
        url = reverse('api_exportar_csv_resultados_base_contactados')
        taskId = self.post_data['taskId']
        campanaId = self.post_data['campanaId']
        response = self.client.post(
            url,
            {
                'task_id': taskId,
                'campana_id': campanaId,
                'all_data': 0
            },
            follow=True,
            format='json'
        )
        Thread.assert_called()
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, self.response_ok)

    @patch('threading.Thread')
    def test_generar_todos_resultados_de_base_csv(self, Thread):
        self.client.login(username='sup1', password=PASSWORD)
        url = reverse('api_exportar_csv_resultados_base_contactados')
        taskId = self.post_data['taskId']
        campanaId = self.post_data['campanaId']
        response = self.client.post(
            url,
            {
                'task_id': taskId,
                'campana_id': campanaId,
                'all_data': 1
            },
            follow=True,
            format='json'
        )
        Thread.assert_called()
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json, self.response_ok)
