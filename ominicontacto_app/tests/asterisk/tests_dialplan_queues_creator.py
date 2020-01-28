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
Tests del metodo 'ominicontacto_app.asterisk_config_generador_de_partes'
"""

from __future__ import unicode_literals

from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import Campana
from ominicontacto_app.asterisk_config import QueuesCreator
from ominicontacto_app.tests.factories import (
    CampanaFactory, QueueFactory
)


class QueuesCreatorTest(OMLBaseTest):
    """
    Testea que se generen bien los dialplan para Campañas
    """

    def setUp(self):
        self.campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        self.queue_entrante = QueueFactory(campana=self.campana_entrante)

    def test_generar_dialplan_entrante_default(self):
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('autopauseunavail=yes', dialplan)
        self.assertIn('autopause=no', dialplan)
        self.assertIn('autopausebusy=no', dialplan)
        self.assertIn('announce-holdtime=no', dialplan)
        self.assertIn('queue-callswaiting=queue-callswaiting', dialplan)
        self.assertIn('queue-thereare=queue-thereare', dialplan)
        self.assertIn('queue-youarenext=queue-youarenext', dialplan)

    def test_generar_dialplan_entrante_autopause(self):
        self.queue_entrante.autopause = True
        self.queue_entrante.autopausebusy = True
        creator = QueuesCreator()
        dialplan = creator._generar_dialplan_entrantes(self.campana_entrante)
        self.assertIn('autopauseunavail=yes', dialplan)
        self.assertIn('autopause=all', dialplan)
        self.assertIn('autopausebusy=yes', dialplan)

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
