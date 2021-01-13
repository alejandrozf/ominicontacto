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
     ominicontacto_app/tests/test_integracion/tests_sistema_externo.py" """

from __future__ import unicode_literals

import unittest
import uuid
import os

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, get_href, crear_grupo, crear_user, ADMIN_USERNAME,
                                     ADMIN_PASSWORD, AGENTE_PASSWORD)
except ImportError:
    pass

AGENTE_USERNAME = 'agente' + uuid.uuid4().hex[:5]
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class SistemaExternoTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # super(IntegrationTests, cls).setUpClass()
        cls.setUp()
        login(cls.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
        group_name = 'group' + uuid.uuid4().hex[:5]
        crear_grupo(cls.browser, group_name)
        tipo_usuario = 'Agente'
        crear_user(cls.browser, AGENTE_USERNAME, AGENTE_PASSWORD, tipo_usuario)
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

    def test_sistema_externo(self):
        # Crear Sistema Externo
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            nuevo_sistema = '//a[contains(@href, "/sistema_externo/nuevo/")]'
            get_href(self.browser, nuevo_sistema)
            sistema_externo = 'sistema' + uuid.uuid4().hex[:5]
            id_externo = 'id' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').send_keys(sistema_externo)
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_agente_en_sistema-0-agente\']/option')[1].click()
            self.browser.find_element_by_id(
                'id_agente_en_sistema-0-id_externo_agente').send_keys(id_externo)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath(
                            '//tr[@id=\'{0}\']'.format(sistema_externo)))
            print('--Se pudo crear un Sistema Externo.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Sistema Externo.-- \n{0}'. format(e))
            raise e
        # Modificar Sistema Externo
        try:
            group_name = 'group' + uuid.uuid4().hex[:5]
            crear_grupo(self.browser, group_name)
            tipo_usuario = 'Agente'
            agente = 'agente' + uuid.uuid4().hex[:5]
            crear_user(self.browser, agente, AGENTE_PASSWORD, tipo_usuario)
            lista_sistema = '//li/a[contains(@href, "/sistema_externo/list/")]'
            get_href(self.browser, lista_sistema)
            update_sistema = '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                sistema_externo)
            get_href(self.browser, update_sistema)
            nuevo_id = 'id' + uuid.uuid4().hex[:5]
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_agente_en_sistema-1-agente\']/option')[2].click()
            self.browser.find_element_by_id(
                'id_agente_en_sistema-1-id_externo_agente').send_keys(nuevo_id)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            get_href(self.browser, update_sistema)
            self.assertTrue(self.browser.find_elements_by_xpath(
                '//input[@value=\'{0}\']'.format(nuevo_id)))
            print('--Se pudo modificar un Sistema Externo.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar el Sistema Externo--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
