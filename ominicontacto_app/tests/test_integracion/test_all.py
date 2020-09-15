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

# Tests de integración (no usar en un entorno de producción de un cliente!!)

# tener en cuenta que las credenciales del agente que se va a testar deben estar igualmente
# especificadas en las variables  de entorno AGENTE_USERNAME y AGENTE_PASSWORD; además este agente
# debe estar asignado al menos a una campaña
# Por otra parte las credenciales del admin deberan estar especificadas en las variables de entorno
# ADMIN_USERNAME y ADMIN_PASSWORD

# Prerequisitos:
# 1) Chrome (o Chromium) 76 instalado, tarjeta de audio presente en el host
# 2) chromedriver desde
# "https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip"

# 3) instalar selenium y copiar el geckodriver en /usr/bin del host donde corre omniapp

# 4) Instalar xvfb y pyvirtualdisplay
# sudo apk add xvfb
# pip install pyvirtualdisplay --user
# pip install html-testRunner --user

# 3) Probar este codigo como punto de partida hacia un server sin DJANGO_DEBUG_TOOLBAR

# 4)Para testear los tests de integración:
""" "$TESTS_INTEGRACION='True' BROWSER_REAL='True' LOGIN_FAILURE_LIMIT=10 python
ominicontacto_app/tests/test_integracion/test_all.py" """

import unittest
import os

try:
    from tests_consola import ConsolaTests
    from tests_usuarios import UsuariosTests
    from tests_acceso_web import AccesoWebTests
    from tests_audio import AudioTests
    from tests_pausas import PausaTests
    from tests_contacto import ContactoTests
    from tests_calificacion import CalificacionTests
    from tests_formulario import FormularioTests
    from tests_sistema_externo import SistemaExternoTests
    from tests_sitio_externo import SitioExternoTests
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class TestIntegracionSuite(unittest.TestCase):
    def testSuite(self):

        tests_integracion = unittest.TestSuite()
        tests_integracion.addTests([
            unittest.defaultTestLoader.loadTestsFromTestCase(ConsolaTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(UsuariosTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(AccesoWebTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(AudioTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(PausaTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(ContactoTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(CalificacionTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(FormularioTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(SistemaExternoTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(SitioExternoTests),
        ])


if __name__ == '__main__':
    unittest.main()
