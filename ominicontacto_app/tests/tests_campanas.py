# -*- coding: utf-8 -*-

"""
Tests relacionados con las campañas
"""
from __future__ import unicode_literals

from ominicontacto_app.tests.factories import CampanaFactory

from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.utiles import validar_nombres_campanas

from django.forms import ValidationError


class CampanasTests(OMLBaseTest):

    def setUp(self):
        self.campana = CampanaFactory()

    def test_campana_contiene_atributo_entero_positivo_llamado_objetivo(self):
        self.assertTrue(self.campana.objetivo >= 0)

    def test_validacion_nombres_de_campana_no_permite_caracteres_no_ASCII(self):
        error_ascii = "el nombre no puede contener tildes ni caracteres no ASCII"
        with self.assertRaisesMessage(ValidationError, error_ascii):
            validar_nombres_campanas("áéíóúñ")

    def test_validacion_nombres_de_campana_no_permite_espacios(self):
        with self.assertRaisesMessage(ValidationError, "el nombre no puede contener espacios"):
            validar_nombres_campanas("nombre con espacios")
