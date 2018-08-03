# -*- coding: utf-8 -*-

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
