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

"""
Tests del metodo 'ominicontacto_app.asterisk_config_generador_de_partes'
"""

from __future__ import unicode_literals

from configuracion_telefonia_app.models import DestinoEntrante
from configuracion_telefonia_app.tests.factories import IVRFactory

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import Campana
from ominicontacto_app.asterisk_config import QueuesCreator
from ominicontacto_app.tests.factories import (
    CampanaFactory, QueueFactory
)
from django.db import connections


class QueuesCreatorTest(OMLBaseTest):
    """
    Testea que se generen bien los dialplan para Campañas
    """

    def setUp(self):
        self.campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        self.queue_entrante = QueueFactory(campana=self.campana_entrante)

        connections['replica']._orig_cursor = connections['replica'].cursor
        connections['replica'].cursor = connections['default'].cursor

    def test_generar_dialplan_entrante_default(self):
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('announce-holdtime=no', dialplan)
        self.assertIn('queue-callswaiting=queue-callswaiting', dialplan)
        self.assertIn('queue-thereare=queue-thereare', dialplan)
        self.assertIn('queue-youarenext=queue-youarenext', dialplan)

    def test_generar_dialplan_announce_holdtime_activated(self):
        self.queue_entrante.announce_holdtime = 'yes'
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('announce-holdtime=yes', dialplan)

    def test_generar_dialplan_announce_holdtime_activated_once(self):
        self.queue_entrante.announce_holdtime = 'once'
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('announce-holdtime=once', dialplan)

    def test_generar_dialplan_entrante_ivr_breakout(self):
        ivr = IVRFactory()
        destino_ivr = DestinoEntrante.crear_nodo_ruta_entrante(ivr)
        self.queue_entrante.ivr_breakdown = destino_ivr
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('context=sub-oml-module-ivrbreakout', dialplan)

    def test_generar_dialplan_entrante_posicion_de_anuncios_default(self):
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('announce-position=no', dialplan)

    def test_generar_dialplan_entrante_posicion_de_anuncios(self):
        self.queue_entrante.announce_position = True
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('announce-position=yes', dialplan)
