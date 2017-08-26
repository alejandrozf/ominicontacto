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
    User
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
