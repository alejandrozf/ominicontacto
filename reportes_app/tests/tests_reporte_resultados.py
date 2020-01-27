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

from reportes_app.reportes.reporte_llamados_contactados_csv import NO_CONECTADO_DESCRIPCION
from reportes_app.tests.tests_reportes_campanas import BaseTestDeReportes
from reportes_app.reportes.reporte_resultados import ReporteDeResultadosDeCampana


class ReporteDeResultadosTests(BaseTestDeReportes):

    def test_usuario_no_logueado_no_accede_reporte_de_resultados(self):
        self.client.logout()
        url = reverse('reporte_de_resultados', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    @patch('reportes_app.archivos_de_reporte.reporte_de_resultados.ReporteDeResultadosCSV.'
           'generar_archivo_descargable')
    def test_usuario_logueado_accede_reporte_de_resultados(self, generar_archivo_descargable):
        url = reverse('reporte_de_resultados', args=[self.campana_activa.pk])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'reporte_de_resultados.html')
        self.assertTrue(generar_archivo_descargable.called)

    @patch('reportes_app.archivos_de_reporte.reporte_de_resultados.ReporteDeResultadosCSV.'
           'generar_archivo_descargable')
    def test_contactos_en_reporte_de_resultados(self, generar_archivo_descargable):
        reporte = ReporteDeResultadosDeCampana(self.campana_activa)

        self.assertTrue(self.contacto_calificado_gestion.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_calificado_gestion.id]
        self.assertEqual(contactacion['calificacion'], self.opcion_calificacion_gestion.nombre)

        self.assertTrue(self.contacto_calificado_no_accion.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_calificado_no_accion.id]
        self.assertEqual(contactacion['calificacion'], self.opcion_calificacion_noaccion.nombre)

        self.assertTrue(self.contacto_no_calificado.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_no_calificado.id]
        self.assertIsNone(contactacion['calificacion'])
        self.assertEqual(contactacion['contactacion'], _('Contactado'))

        self.assertTrue(self.contacto_no_atendido.id in reporte.contactaciones)
        contactacion = reporte.contactaciones[self.contacto_no_atendido.id]
        self.assertIsNone(contactacion['calificacion'])
        self.assertEqual(contactacion['contactacion'], NO_CONECTADO_DESCRIPCION['NOANSWER'])
