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
# Para testear este test de integración:
""" "$TESTS_INTEGRACION='True' LOGIN_FAILURE_LIMIT=10 python
     ominicontacto_app/tests/test_integracion/tests_formulario.py" """

from __future__ import unicode_literals

import unittest
import uuid
import os

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from integracion_metodos import (login, get_href, crear_campos_formulario, ADMIN_USERNAME,
                                     ADMIN_PASSWORD)
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class FormularioTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # super(IntegrationTests, cls).setUpClass()
        cls.setUp()
        login(cls.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
        cls.tearDown()

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--use-fake-ui-for-media-stream')
        chrome_options.add_argument('--use-fake-device-for-media-stream')
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en'})
        chrome_options.add_argument('--ignore-certificate-errors')
        # si se pone visible=1 se muestra el browser en medio de los tests
        self.display = Display(visible=0, size=(1366, 768))
        self.display.start()
        self.browser = webdriver.Chrome(options=chrome_options)

    @classmethod
    def tearDown(self):
        self.browser.close()
        self.display.stop()

    def test_crear_formularios(self):
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            nuevo_formulario = '//a[contains(@href, "/formulario/nuevo")]'
            get_href(self.browser, nuevo_formulario)
            nombre_form = 'form' + uuid.uuid4().hex[:5]
            descripcion = 'Este form fue generado para tests'
            self.browser.find_element(By.NAME, 'nombre').send_keys(nombre_form)
            self.browser.find_element(By.NAME, 'descripcion').send_keys(descripcion)
            self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
            self.browser.implicitly_wait(3)

            nombre_campos = ['Nombre', 'Fecha_nacimiento', 'Opciones', 'Comentarios']
            crear_campos_formulario(self.browser, nombre_campos)
            self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
            self.browser.implicitly_wait(3)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
            self.browser.implicitly_wait(3)
            self.browser.find_element(By.LINK_TEXT, "YES").click()
            self.browser.implicitly_wait(3)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element(By.XPATH, '//tr[@id = \'{0}\']/td[4]/a'.format(nombre_form)
                                      ).click()
            for items in nombre_campos:
                self.assertTrue(self.browser.find_elements(By.NAME, items))
                print('--Se pudo crear un Formulario con un campo \'{0}\'.--'.format(items))
        except Exception as e:
            print('--ERROR: No se pudo crear un Formulario.-- \n{0}' .format(e))
            raise e
        # Ocultar y Mostrar Formulario.
        try:
            self.browser.find_element(By.CSS_SELECTOR, ".btn-outline-primary").click()
            self.browser.implicitly_wait(3)
            self.browser.find_element(By.XPATH, '//tr[@id=\'{0}\']/td[5]'.format(nombre_form)
                                      ).click()  # oculto form
            sleep(3)
            self.assertFalse(self.browser.find_elements(By.XPATH, '//tr[@id=\'{0}\']'.format(
                nombre_form)))
            mostrar_ocultos = '//a[contains(@href, "formulario/list/mostrar_ocultos/")]'
            get_href(self.browser, mostrar_ocultos)
            self.browser.find_element(By.XPATH, '//tr[@id=\'{0}\']/td[5]'.format(nombre_form)
                                      ).click()  # muestro form
            self.assertTrue(self.browser.find_elements(By.XPATH, '//tr[@id=\'{0}\']'.format(
                nombre_form)))
            print('--Se pudo ocultar y mostrar un formulario.--')
        except Exception as e:
            print('--ERROR: No se pudo ocultar y mostrar un formulario.-- \n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
