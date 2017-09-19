# -*- coding: utf-8 -*-

"""
Tests relacionados con las campañas
"""

from ominicontacto_app.tests.factories import CampanaFactory

from ominicontacto_app.tests.utiles import OMLBaseTest


class CampanasTests(OMLBaseTest):

    def setUp(self):
        self.campana = CampanaFactory()

    def test_campana_contiene_atributo_entero_positivo_llamado_objetivo(self):
        self.assertEqual(self.campana.objetivo >= 0)
