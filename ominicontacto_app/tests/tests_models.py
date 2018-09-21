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

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

from mock import patch

import datetime
import logging as _logging

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import Campana, ReglasIncidencia
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService

logger = _logging.getLogger(__name__)


class UtilesTest(OMLBaseTest):

    def test_get_agente_profile(self):
        ua = self.crear_user_agente()
        self.assertEqual(ua.get_agente_profile(), None)
        ap = self.crear_agente_profile(ua)
        self.assertEqual(ua.get_agente_profile(), ap)

    def test_get_supervisor_profile(self):
        ua = self.crear_user_supervisor()
        self.assertEqual(ua.get_supervisor_profile(), None)
        sp = self.crear_supervisor_profile(ua)
        self.assertEqual(ua.get_supervisor_profile(), sp)

    def test_agente_inactivo(self):
        ua = self.crear_user_agente()
        ap = self.crear_agente_profile(ua)
        # primero chequeamos que sea un agente inactivo
        self.assertFalse(ap.is_inactive)
        # ahora inactivamos al agente
        ap.desactivar()
        self.assertTrue(ap.is_inactive)
        # ahora activamos al agente
        ap.activar()
        self.assertFalse(ap.is_inactive)


class CampanaTest(OMLBaseTest):

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_campanas_dialer_creadas(self, _convertir_audio):
        """
        - Campana creadas.
        """
        [self.crear_campana_dialer() for _ in range(0, 10)]
        self.assertEqual(Campana.objects.all().count(), 10)

    def test_campanas_manual_creadas(self):
        """
        - Campana creadas.
        """
        [self.crear_campana_manual() for _ in range(0, 10)]
        self.assertEqual(Campana.objects.all().count(), 10)

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_campanas_entrante_creadas(self, _convertir_audio):
        """
        - Campana creadas.
        """
        [self.crear_campana_entrante() for _ in range(0, 10)]
        self.assertEqual(Campana.objects.all().count(), 10)

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_crea_actuacion_vigente(self, _convertir_audio):
        """
        test crea actuacion vigente a campana dialer
        :return:
        """

        campana = self.crear_campana_dialer()
        hora_desde = datetime.time(9, 00)
        hora_hasta = datetime.time(10, 00)
        self.crear_actuacion_vigente(campana, hora_desde=hora_desde,
                                     hora_hasta=hora_hasta)

        self.assertEqual(campana.actuacionvigente.hora_desde, hora_desde)
        self.assertEqual(campana.actuacionvigente.hora_hasta, hora_hasta)

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_crea_regla_incidencia(self, _convertir_audio):
        """
        test crea regla de incidencia para campana dialer
        :return:
        """
        campana = self.crear_campana_dialer()
        estados = [ReglasIncidencia.RS_BUSY, ReglasIncidencia.RS_NOANSWER,
                   ReglasIncidencia.RS_REJECTED, ReglasIncidencia.RS_TIMEOUT,
                   ReglasIncidencia.TERMINATED]
        for estado in estados:
            self.crear_regla_incidencia(campana, estado)

        self.assertEqual(campana.reglas_incidencia.all().count(), 5)

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_campana_activar(self, _convertir_audio):
        """
        - Campana.activar()
        - Campana.objects.obtener_activas()
        - actualizar y poner los assert de manera correcta
        """

        campanas = [self.crear_campana_dialer() for _ in range(0, 10)]
        campanas[0].activar()
        campanas[1].activar()

        # Testeamos que no se active una activa.
        # self.assertRaises(AssertionError, campanas[0].activar)

        campanas[0].pausar()
        # Testeamos que no se active una pausada.
        # self.assertRaises(AssertionError, campanas[0].activar)

        campanas[1].finalizar()
        # Testeamos que no se active una finalizada.
        # self.assertRaises(AssertionError, campanas[1].activar)

        # Testeamos que obtener_activas me devuelva las 2 activas solo.
        campanas[2].activar()
        campanas[3].activar()
        campanas_activas = Campana.objects.obtener_activas()
        for c in campanas[2:3]:
            self.assertIn(c, campanas_activas)

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def test_campana_pausar(self, _convertir_audio):
        """
        - Campana.pausar()
        - Campana.objects.obtener_pausadas()
        - actualizar y poner los assert de manera correcta
        """

        campanas = [self.crear_campana_dialer() for _ in range(0, 10)]
        campanas[0].activar()
        campanas[1].activar()
        campanas[2].activar()
        campanas[0].pausar()
        campanas[1].pausar()

        # Testeamos que no se pause una pausada.
        # self.assertRaises(AssertionError, campanas[0].pausar)

        # Testeamos que no se active con el activar() una pausada.
        # self.assertRaises(AssertionError, campanas[0].activar)

        campanas[2].finalizar()
        # Testeamos que no se pause una finalizada.
        # self.assertRaises(AssertionError, campanas[2].pausar)

        # Testeamos que no se pause una que no esta activa.
        # self.assertRaises(AssertionError, campanas[9].pausar)

        # Testeamos que obtener_pausadas me devuelva las 2 pausadas solo.
        campanas_pausadas = Campana.objects.obtener_pausadas()
        for c in campanas[:2]:
            self.assertIn(c, campanas_pausadas)
