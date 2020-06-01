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
""" TESTS_INTEGRACION='True' BROWSER_REAL='True' LOGIN_FAILURE_LIMIT=10 python
ominicontacto_app/tests/test_integracion/tests_consola.py """

from __future__ import unicode_literals

import os
import unittest
import uuid

from time import sleep

from integracion_metodos import (login, crear_grupo, crear_user, asignar_agente_campana_manual)

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
USER = os.getenv('USER')

CAMPANA_MANUAL = os.getenv('CAMPANA_MANUAL')

AGENTE_USERNAME = 'agente' + uuid.uuid4().hex[:5]
AGENTE_PASSWORD = '098098ZZZ'

BROWSER_REAL = os.getenv('BROWSER_REAL')
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')

MSG_MICROFONO = 'Se necesita un browser real con microfono'


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class ConsolaTests(unittest.TestCase):

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
        group_name = 'group' + uuid.uuid4().hex[:5]
        crear_grupo(cls.browser, group_name)
        tipo_usuario = 'Agente'
        crear_user(cls.browser, AGENTE_USERNAME, AGENTE_PASSWORD, tipo_usuario)
        if BROWSER_REAL == 'True':
            asignar_agente_campana_manual(cls.browser, AGENTE_USERNAME)
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

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_se_registra_correctamente(self):
        try:
            login(self.browser, AGENTE_USERNAME, AGENTE_PASSWORD)
            self.assertEqual(self.browser.find_element_by_id('dial_status').text,
                             'Agent connected to asterisk')
            print('--Se pudo registrar correctamente un agente.--')
        except Exception as e:
            print('--ERROR: No se pudo registrar correctamente un agente.--\n{0}'.format(e))
            raise e

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_puede_realizar_llamada_fuera_de_campana(self):
        try:
            numero_externo = '351111111'
            login(self.browser, AGENTE_USERNAME, AGENTE_PASSWORD)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element_by_id('call_off_campaign_menu').click()
            sleep(1)
            self.browser.find_element_by_id('phone_off_camp').send_keys(numero_externo)
            self.browser.find_element_by_id('call_phone_off_campaign').click()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            sleep(1)
            self.assertEqual(self.browser.find_element_by_id('dial_status').text,
                             'Connected to {0}'.format(numero_externo))
            print('--Se pudo realizar una llamada fuera de la campana.--')
        except Exception as e:
            print('--ERROR: No se pudo realizar una llamada fuera de la campana.--\n{0}'.format(e))
            raise e

    # def test_agente_puede_recibir_llamada_entrante(self):
    #     pass

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_puede_realizar_llamada_saliente_campana_sin_identificar_contacto(self):
        # asume al menos una campana asignada al agente
        try:
            numero_externo = '351111111'
            login(self.browser, AGENTE_USERNAME, AGENTE_PASSWORD)
            self.browser.find_element_by_id('numberToCall').send_keys(numero_externo)
            self.browser.find_element_by_id('call').click()
            sleep(1)
            self.browser.find_element_by_id('SelectCamp').click()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.switch_to.frame(self.browser.find_element_by_tag_name('iframe'))
            sleep(1)
            self.browser.find_element_by_id('id_btn_no_identificar').click()
            sleep(1)
            self.browser.switch_to.default_content()
            self.assertEqual(self.browser.find_element_by_id('dial_status').text,
                             'Connected to {0}'.format(numero_externo))
            print('--Se pudo realizar una llamada saliente sin identificar contacto con exito.--')
        except Exception as e:
            print('--ERROR: No se pudo realizar una llamada saliente '
                  'sin identificar contacto.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
