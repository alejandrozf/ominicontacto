# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.services.asterisk_database'
"""

from __future__ import unicode_literals


from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.services.asterisk_database import CampanaFamily


class AsteriskDatabaseTest(OMLBaseTest):

    def setUp(self):
        self.campana = self.crear_campana_dialer()

    def test_devuelve_correctamente_dict_campana_asterisk(self):
        """
        este test testea el diccionario de la family de la campana
        """
        servicio = CampanaFamily()
        print servicio.create_dict(self.campana)
