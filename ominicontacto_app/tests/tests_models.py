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
    User, Campana
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

    def test_campanas_creadas(self):
        """
        - Campana creadas.
        """
        [self.crear_campana_dialer() for _ in range(0, 10)]
        self.assertEqual(Campana.objects.all().count(), 10)
