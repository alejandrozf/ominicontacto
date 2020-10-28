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
     ominicontacto_app/tests/test_integracion/tests_calificacion.py" """

from __future__ import unicode_literals

import unittest
import os
from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, crear_calificacion, ADMIN_USERNAME, ADMIN_PASSWORD)
except ImportError:
    pass
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class CalificacionTests(unittest.TestCase):

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

    def test_crear_update_calificaciones(self):
        # Crear 7 nuevas calificaciones.
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            lista_calificaciones = ['Venta', 'No Venta', 'No Interesado',
                                    'No conoce', 'Ya Tiene', 'Es jubilado']
            for items in lista_calificaciones:
                crear_calificacion(self.browser, items)
                self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'
                                .format(items)))
            print('--Se pudo crear 7 calificaciones.--')
        except Exception as e:
            print('--ERROR: No se pudo crear 7 calificaciones.--\n{0}'.format(e))
            raise e
        # Editar la calificacion: "Ya tiene" por "Ya conoce".
        try:
            update_calificacion = 'Ya conoce'
            calificacion = 'Ya Tiene'
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            link_update = self.browser.find_element_by_xpath(
                '//tr[@id = \'{0}\']//a[contains(@href, "/update/")]'
                .format(calificacion))
            href_update = link_update.get_attribute('href')
            self.browser.get(href_update)
            self.browser.find_element_by_id('id_nombre').clear()
            self.browser.find_element_by_id('id_nombre').send_keys(update_calificacion)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                update_calificacion)))
            print('--Se pudo editar la calificacion: "Ya tiene" por "Ya conoce".--')
        except Exception as e:
            print('--Error: No se pudo editar la calificacion:'
                  '"Ya tiene" por "Ya conoce".-- \n{0}'.format(e))
            raise e

    def test_delete_calificaciones(self):
        # Eliminar la calificacion: "No se encuentra".
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            calificacion = 'No se encuentra'
            lista_calificaciones = [calificacion]
            for items in lista_calificaciones:
                crear_calificacion(self.browser, items)
                self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'
                                .format(items)))
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            link_delete = self.browser.find_element_by_xpath(
                '//tr[@id = \'{0}\']//a[contains(@href, "/delete/")]'
                .format(calificacion))
            href_delete = link_delete.get_attribute('href')
            self.browser.get(href_delete)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                calificacion)))
            print('--Se pudo eliminar con exito la calificacion "No se encuentra".--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar una calificacion.-- \n{0}' .format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
