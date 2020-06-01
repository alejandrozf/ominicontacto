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

# 3) Probar este codigo como punto de partida hacia un server sin DJANGO_DEBUG_TOOLBAR

# 4)Para testear los tests de integración:
""" "$TESTS_INTEGRACION='True' BROWSER_REAL='True' LOGIN_FAILURE_LIMIT=10 python
     ominicontacto_app/tests/test_integracion/test_all.py" """
# Se puede ver el resultado del reporte:
# ominicontacto_app/tests/test_integracion/reports/reporte_test_integracion.html

from unittest import TestLoader, TestSuite
from HtmlTestRunner import HTMLTestRunner

import os

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

consola = TestLoader().loadTestsFromTestCase(ConsolaTests)
usuarios = TestLoader().loadTestsFromTestCase(UsuariosTests)
acceso_web = TestLoader().loadTestsFromTestCase(AccesoWebTests)
audio = TestLoader().loadTestsFromTestCase(AudioTests)
pausa = TestLoader().loadTestsFromTestCase(PausaTests)
contacto = TestLoader().loadTestsFromTestCase(ContactoTests)
calificacion = TestLoader().loadTestsFromTestCase(CalificacionTests)
formulario = TestLoader().loadTestsFromTestCase(FormularioTests)
sistema_externo = TestLoader().loadTestsFromTestCase(SistemaExternoTests)
sitio_externo = TestLoader().loadTestsFromTestCase(SitioExternoTests)

tests_integracion = TestSuite([consola, usuarios, acceso_web, audio, pausa, contacto,
                               calificacion, formulario, sistema_externo, sitio_externo])


current_directory = os.getcwd()
output_file = current_directory + "/ominicontacto_app/tests/test_integracion/reports/"

runner = HTMLTestRunner(
    output=output_file,
    combine_reports=True,
    report_name="reporte_test_integracion",
    add_timestamp=False,
    report_title='Reporte test de integracion OMnileads'
)

runner.run(tests_integracion)
