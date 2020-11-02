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
     ominicontacto_app/tests/test_integracion/tests_sitio_externo.py" """

from __future__ import unicode_literals

import unittest
import uuid
import os

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, get_href, formato_sitio, sitio_externo, ADMIN_USERNAME,
                                     ADMIN_PASSWORD)
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class SitioExternoTests(unittest.TestCase):

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

    def test_crear_delete_sitio_externo_agente_get(self):
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            sitio_get = 'sitio' + uuid.uuid4().hex[:5]
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Get
            sitio_externo(self.browser, sitio_get, url)
            self.browser.find_elements_by_xpath('//select[@id=\'id_disparador\']/option')[0].click()
            self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[0].click()
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_get)))
            print('--Se pudo crear un Sitio externo para el disparador agente, metodo GET.--')
        except Exception as e:
            print('--ERROR: No se pudo crear Sitio Externo con disparador Agente, '
                  'metodo GET.--\n{0}'.format(e))
            raise e
        try:
            # Eliminar Sitio Externo
            delete_sitio = '//tr[@id=\'{0}\']//a[contains(@href, "/delete/")]'.format(sitio_get)
            get_href(self.browser, delete_sitio)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_get)))
            print('--Se puede eliminar un Sitio Externo con disparador agente, metodo GET.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un Sitio '
                  'Externo con disparador agente, metodo GET.--\n{0}'.format(e))
            raise e

    def test_crear_update_sitio_externo_agente_post(self):
        try:
            # Metodo Post
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            formato = ['multipart', 'urlencoded', 'text', 'json']
            for items in formato:
                sitio_post = 'sitio' + uuid.uuid4().hex[:5]
                sitio_externo(self.browser, sitio_post, url)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[0].click()
                self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[1].click()
                formato_sitio(self.browser, items)
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                self.assertTrue(self.browser.find_element_by_xpath('//tr[@id=\'{0}\']'.format(
                    sitio_post)))
                # Modificar a Disparador Servidor
                update_servidor = '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                    sitio_post)
                get_href(self.browser, update_servidor)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[2].click()
                self.browser.find_element_by_xpath("//button[@type='submit']").click()
                sleep(1)
                self.assertTrue(self.browser.find_elements_by_xpath(
                    '//tr[@id=\'{0}\']//td[@id = "Server"]'.format(sitio_post)))
            print('--Se pudo crear un Sitio externo para el disparador agente, metodo POST.--')
            print('--Se pudo modificar el sitio Externo a disparador servidor.--')
        except Exception as e:
            print('--ERROR: No se pudo crear Sitio Externo con disparador Agente, '
                  'metodo POST y luego modificarlos a disparador Servidor.--\n{0}'.format(e))
            raise e

    def test_crear_update_sitio_externo_automatico_get(self):
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            sitio_get = 'sitio' + uuid.uuid4().hex[:5]
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Get
            sitio_externo(self.browser, sitio_get, url)
            self.browser.find_elements_by_xpath('//select[@id=\'id_disparador\']/option')[1].click()
            self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[0].click()
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_get)))
            print('--Se pudo crear un Sitio externo para el disparador Automatico, metodo GET.--')
        except Exception as e:
            print('--ERROR: No se pudo crear Sitio Externo con disparador '
                  'Automatico, metodo GET.--\n{0}'.format(e))
            raise e
        try:
            # Modificar a Disparador Servidor
            update_servidor = '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(sitio_get)
            get_href(self.browser, update_servidor)
            self.browser.find_elements_by_xpath('//select[@id=\'id_disparador\']/option')[2].click()
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath(
                '//tr[@id=\'{0}\']//td[@id = "Server"]'.format(sitio_get)))
            print('--Se pudo modificar el sitio Externo a disparador servidor.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar el sitio externo a disparador '
                  'Servidor.--\n{0}'.format(e))
            raise e

    def test_sitio_externo_automatico_post(self):
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Post
            formato = ['multipart', 'urlencoded', 'text', 'json']
            for items in formato:
                sitio_post = 'sitio' + uuid.uuid4().hex[:5]
                sitio_externo(self.browser, sitio_post, url)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[1].click()
                self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[1].click()
                formato_sitio(self.browser, items)
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                self.assertTrue(self.browser.find_element_by_xpath('//tr[@id=\'{0}\']'.format(
                    sitio_post)))
            print('--Se pudo crear un Sitio externo para el disparador Automatico, metodo POST--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Sitio '
                  'Externo con disparador automatico, metodo POST--\n{0}'.format(e))
            raise e
        try:
            # Ocultar y mostrar Sitio Externo
            ocultar_sitio = '//tr[@id=\'{0}\']//a[contains(@href, "/ocultar/")]'.format(
                sitio_post)
            get_href(self.browser, ocultar_sitio)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_post)))
            self.browser.find_element_by_xpath('//a[@onclick]').click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            desocultar = '//tr[@id=\'{0}\']//td//a[contains(@href, "/desocultar/")]'.format(
                sitio_post)
            get_href(self.browser, desocultar)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_post)))
            print('--Se pudo ocultar y mostrar un Sitio externo.--')
        except Exception as e:
            print('--ERROR: No se pudo ocultar y mostrar un Sitio externo.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
