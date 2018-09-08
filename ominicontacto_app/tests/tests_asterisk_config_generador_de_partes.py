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
from ominicontacto_app.asterisk_config_generador_de_partes import (
    GeneradorDePedazoDeRutasSalientesFactory, GeneradorParaFailedRutaSaliente,
    GeneradorParaPatronRuta
)
from configuracion_telefonia_app.tests.factories import (
    RutaSalienteFactory, PatronDeDiscadoFactory
)

from mock import Mock


class GeneradorDePedazoDeRutasSalientesFactoryTest(OMLBaseTest):
    """
    Testea que la clase GeneradorDePedazoDeRutasSalientesFactory instancie el
    objeto generador adecuado según los parametros proveidos.
    """

    def test_crear_generador_para_failed_ruta_saliente(self):
        generador = GeneradorDePedazoDeRutasSalientesFactory()

        self.assertTrue(isinstance(generador.crear_generador_para_failed(
                                   Mock()), GeneradorParaFailedRutaSaliente))

    def test_crear_generador_para_ruta(self):
        generador = GeneradorDePedazoDeRutasSalientesFactory()
        ruta = RutaSalienteFactory()
        patron = PatronDeDiscadoFactory(ruta_saliente=ruta)
        param_generales = {
            'oml-ruta-id': ruta.id,
            'oml-ruta-dialpatern': ''.join(("_", str(patron.prefix), patron.match_pattern)),
        }

        generador_para_ruta = generador.crear_generador_para_patron_ruta_saliente(param_generales)
        self.assertTrue(isinstance(generador_para_ruta, GeneradorParaPatronRuta))
