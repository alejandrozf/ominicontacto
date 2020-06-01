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

import os
import unittest
import uuid

from time import sleep

from integracion_metodos import (login, get_href, crear_campos_formulario)

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class FormularioTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # super(IntegrationTests, cls).setUpClass()
        cls.setUp()
        login(cls.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
        try:
            if cls.browser.find_elements_by_id('djHideToolBarButton'):
                print('--ERROR: Se olvido de deshabilitar Django Toolbar.--')
                raise
                exit()
        except Exception:
            pass
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
            self.browser.find_element_by_id('id_nombre').send_keys(nombre_form)
            self.browser.find_element_by_id('id_descripcion').send_keys(descripcion)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            nombre_campos = ['Nombre', 'Fecha nacimiento', 'Opciones', 'Comentarios']
            crear_campos_formulario(self.browser, nombre_campos)
            continuar = '//a[contains(@href, "/vista_previa/")]'
            get_href(self.browser, continuar)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element_by_xpath("//button[@id='finalizar']").click()
            sleep(1)
            lista_form = '//a[contains(@href, "/formulario/list/")]'
            get_href(self.browser, lista_form)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            vista_previa = '//tr[@id = \'{0}\']//a[contains(@href, "/vista/")]'.format(
                nombre_form)
            get_href(self.browser, vista_previa)
            id_campos = ['id_Nombre', 'id_Fecha nacimiento', 'id_Opciones', 'id_Comentarios']
            for items in id_campos:
                self.assertTrue(self.browser.find_elements_by_id(items))
            print('--Se pudo crear un Formulario.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Formulario.-- \n{0}' .format(e))
            raise e
        # Ocultar y Mostrar Formulario.
        try:
            get_href(self.browser, lista_form)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element_by_xpath(
                '//tr[@id=\'{0}\']//span[@id="ocultar"]'.format(nombre_form)).click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath(
                '//tr[@id=\'{0}\']'.format(nombre_form)))
            mostrar_ocultos = '//a[contains(@href, "formulario/list/mostrar_ocultos/")]'
            get_href(self.browser, mostrar_ocultos)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_elements_by_xpath(
                '//tr[@id=\'{0}\']'.format(nombre_form)))
        except Exception as e:
            print('--ERROR: No se pudo ocultar y mostrar un formulario.-- \n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
