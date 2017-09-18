# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.models'
"""

from __future__ import unicode_literals

import uuid
import datetime
import logging as _logging

from django.conf import settings
from unittest import skip
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import (
    User, Campana, ReglasIncidencia
)
from ominicontacto_app.errors import OmlError
import os

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

    def test_campanas_dialer_creadas(self):
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

    def test_campanas_entrante_creadas(self):
        """
        - Campana creadas.
        """
        [self.crear_campana_entrante() for _ in range(0, 10)]
        self.assertEqual(Campana.objects.all().count(), 10)

    def test_crea_actuacion_vigente(self):
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

    def test_crea_regla_incidencia(self):
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

    def test_campana_activar(self):
        """
        - Campana.activar()
        - Campana.objects.obtener_activas()
        - actualizar y poner los assert de manera correcta
        """

        campanas = [self.crear_campana_dialer() for _ in range(0, 10)]
        campanas[0].activar()
        campanas[1].activar()

        # Testeamos que no se active una activa.
        #self.assertRaises(AssertionError, campanas[0].activar)

        campanas[0].pausar()
        # Testeamos que no se active una pausada.
        #self.assertRaises(AssertionError, campanas[0].activar)

        campanas[1].finalizar()
        # Testeamos que no se active una finalizada.
        #self.assertRaises(AssertionError, campanas[1].activar)

        # Testeamos que obtener_activas me devuelva las 2 activas solo.
        campanas[2].activar()
        campanas[3].activar()
        campanas_activas = Campana.objects.obtener_activas()
        for c in campanas[2:3]:
            self.assertIn(c, campanas_activas)

    def test_campana_pausar(self):
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
        #self.assertRaises(AssertionError, campanas[0].pausar)

        # Testeamos que no se active con el activar() una pausada.
        #self.assertRaises(AssertionError, campanas[0].activar)

        campanas[2].finalizar()
        # Testeamos que no se pause una finalizada.
        #self.assertRaises(AssertionError, campanas[2].pausar)

        # Testeamos que no se pause una que no esta activa.
        #self.assertRaises(AssertionError, campanas[9].pausar)

        # Testeamos que obtener_pausadas me devuelva las 2 pausadas solo.
        campanas_pausadas = Campana.objects.obtener_pausadas()
        for c in campanas[:2]:
            self.assertIn(c, campanas_pausadas)

    def test_crear_campana_de_template(self):
        """
        Crea campana desde un template de campana
        """
        campana = self.crear_campana_dialer()

        hora_desde = datetime.time(9, 00)
        hora_hasta = datetime.time(10, 00)
        self.crear_actuacion_vigente(campana, hora_desde=hora_desde,
                                     hora_hasta=hora_hasta)

        estados = [ReglasIncidencia.RS_BUSY, ReglasIncidencia.RS_NOANSWER,
                   ReglasIncidencia.RS_REJECTED, ReglasIncidencia.RS_TIMEOUT,
                   ReglasIncidencia.TERMINATED]
        for estado in estados:
            self.crear_regla_incidencia(campana, estado)

        campana_creada = campana


        # actualizo campana como template de campana
        # crear util para crear un template de campana dialer

        campana.estado = Campana.ESTADO_TEMPLATE_ACTIVO
        campana.es_template = True
        campana.save()

        # creo campana apartir de un template
        campana_clonada = Campana.objects.crea_campana_de_template(campana)

        # assert para chequear que se haya creado la misma campana
        self.assertEqual(campana_creada.calificacion_campana,
                         campana_clonada.calificacion_campana)
        self.assertEqual(campana_creada.gestion,
                         campana_clonada.gestion)
        self.assertEqual(campana_creada.formulario,
                         campana_clonada.formulario)
        self.assertEqual(campana_creada.sitio_externo,
                         campana_clonada.sitio_externo)
        self.assertEqual(campana_creada.tipo_interaccion,
                         campana_clonada.tipo_interaccion)
        self.assertEqual(campana_creada.queue_campana.maxlen,
                         campana_clonada.queue_campana.maxlen)
        self.assertEqual(campana_creada.queue_campana.wait,
                         campana_clonada.queue_campana.wait)
        self.assertEqual(campana_creada.actuacionvigente.hora_desde,
                         campana_clonada.actuacionvigente.hora_desde)
        self.assertEqual(campana_creada.actuacionvigente.hora_desde,
                         campana_clonada.actuacionvigente.hora_desde)
        self.assertEqual(campana_creada.actuacionvigente.hora_hasta,
                         campana_clonada.actuacionvigente.hora_hasta)
        self.assertEqual(campana_clonada.reglas_incidencia.all().count(), 5)
