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
     ominicontacto_app/tests/test_integracion/tests_pausas.py" """

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
    from integracion_metodos import (login, get_href, ADMIN_USERNAME, ADMIN_PASSWORD)
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class PausaTests(unittest.TestCase):

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

    def test_pausa_productiva(self):
        try:
            # crear pausa productiva
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_pausa = '//a[contains(@href,"/pausa/nuevo")]'
            get_href(self.browser, link_create_pausa)
            pausa_nueva = 'pausa_pro' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').send_keys(pausa_nueva)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_nueva)))
            print('--Se pudo crear una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo crear una pausa productiva.--\n{0}'.format(e))
            raise e
        # modificar pausa productiva
        try:
            link_edit = '//tr[@id=\'{0}\']//a[contains(@href, "/pausa/update/")]'.format(
                pausa_nueva)
            get_href(self.browser, link_edit)
            pausa_recreativa = 'pausa_rec' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').clear()
            sleep(1)
            self.browser.find_element_by_id('id_nombre').send_keys(pausa_recreativa)
            self.browser.find_element_by_xpath("//select/option[@value = 'R']").click()
            sleep(1)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_recreativa)))
            print('--Se pudo modificar una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar una pausa productiva.--\n{0}'.format(e))
            raise e
        # eliminar pausa recreativa
        try:
            link_delete = "//tr[@id=\'{0}\']//a[contains(@href, '/pausa/delete/')]".format(
                pausa_recreativa)
            get_href(self.browser, link_delete)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath(
                "//tr[@id='pausa_eliminada']//td[contains(text(), \'{0}\')]".format(
                    pausa_recreativa)))
            print('--Se pudo eliminar una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar una pausa recreativa.--\n{0}'.format(e))
            raise e
        # reactivar pausa recreativa
        try:
            link_reactivate = "//tr[@id='pausa_eliminada']//td[@id=\'{0}\']//"\
                "a[contains(@href, '/pausa/delete/')]".format(pausa_recreativa)
            get_href(self.browser, link_reactivate)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_recreativa)))
            print('--Se pudo reactivar una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo reactivar una pausa recreativa.--\n{0}'.format(e))
            raise e

    def test_pausa_recreativa(self):
        try:
            # crear pausa recreativa
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_pausa = '//a[contains(@href,"/pausa/nuevo")]'
            get_href(self.browser, link_create_pausa)
            pausa_nueva = 'pausa_rec' + uuid.uuid4().hex[:5]
            self.browser.find_element(By.NAME, 'nombre').send_keys(pausa_nueva)
            self.browser.find_element(By.XPATH, "//select/option[@value = 'R']").click()
            sleep(1)
            self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements(By.XPATH, '//td[text()=\'{0}\']'.format(
                pausa_nueva)))
            print('--Se pudo crear una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo crear una pausa recreativa.--\n{0}'.format(e))
            raise e
        # modificar pausa recreativa
        try:
            link_edit = '//tr[@id=\'{0}\']//a[contains(@href, "/pausa/update/")]'.format(
                pausa_nueva)
            get_href(self.browser, link_edit)
            pausa_productiva = 'pausa_pro' + uuid.uuid4().hex[:5]
            self.browser.find_element(By.NAME, 'nombre').clear()
            sleep(1)
            self.browser.find_element(By.NAME, 'nombre').send_keys(pausa_productiva)
            self.browser.find_element(By.XPATH, "//select/option[@value = 'P']").click()
            sleep(1)
            self.browser.find_element(By.CSS_SELECTOR, ".btn-primary").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements(By.XPATH, '//td[text()=\'{0}\']'.format(
                pausa_productiva)))
            print('--Se pudo modificar una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar una pausa recreativa.--\n{0}'.format(e))
            raise e
        # eliminar pausa productiva
        try:
            link_delete = "//tr[@id=\'{0}\']//a[contains(@href, '/pausa/delete/')]".format(
                pausa_productiva)
            get_href(self.browser, link_delete)
            self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements(
                By.XPATH, "//tr[@id='pausa_eliminada']//td[contains(text(), \'{0}\')]".format(
                    pausa_productiva)))
            print('--Se pudo eliminar una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar una pausa productiva.--\n{0}'.format(e))
            raise e
        # reactivar pausa productiva
        try:
            link_reactivate = "//tr[@id='pausa_eliminada']//td[@id=\'{0}\']//"\
                "a[contains(@href, '/pausa/delete/')]".format(pausa_productiva)
            get_href(self.browser, link_reactivate)
            self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements(By.XPATH, '//td[text()=\'{0}\']'.format(
                pausa_productiva)))
            print('--Se pudo reactivar una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo reactivar una pausa productiva.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
