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

# 4) correr "$BROWSER_REAL='True' TESTS_INTEGRACION='True' python ominicontacto_app/tests/tests.py"
# para testear los tests de integración incluyendo los que necesitan audio en el browser

from __future__ import unicode_literals

import os
import socket
import unittest
import uuid

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

AGENTE_USERNAME = os.getenv('AGENTE_USERNAME')
AGENTE_PASSWORD = os.getenv('AGENTE_PASSWORD')

BROWSER_REAL = os.getenv('BROWSER_REAL')
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')

MSG_MICROFONO = 'Se necesita un browser real con micrófono'


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integración')
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--use-fake-ui-for-media-stream')
        chrome_options.add_argument('--use-fake-device-for-media-stream')
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en'})
        # si se pone visible=1 se muestra el browser en medio de los tests
        self.display = Display(visible=0, size=(1366, 768))
        self.display.start()
        self.browser = webdriver.Chrome(options=chrome_options)

    def tearDown(self):
        self.browser.close()
        self.display.stop()

    def _login(self, username, password):
        self.browser.get('https://{0}'.format(socket.gethostname()))
        self.browser.find_element_by_name('username').send_keys(username)
        self.browser.find_element_by_name('password').send_keys(password)
        self.browser.find_element_by_tag_name('button').click()
        sleep(2)

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_se_registra_correctamente(self):
        self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
        self.assertEqual(self.browser.find_element_by_id('dial_status').text, 'Registered Agent')

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_puede_realizar_llamada_fuera_de_campana(self):
        numero_externo = '351111111'
        self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        self.browser.find_element_by_id('call_off_campaign_menu').click()
        sleep(1)
        self.browser.find_element_by_id('phone_off_camp').send_keys(numero_externo)
        self.browser.find_element_by_id('call_phone_off_campaign').click()
        webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
        sleep(1)
        self.assertEqual(self.browser.find_element_by_id('dial_status').text,
                         'Connected to {0}'.format(numero_externo))

    # def test_agente_puede_recibir_llamada_entrante(self):
    #     pass

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_puede_realizar_llamada_saliente_campana_sin_identificar_contacto(self):
        # asume al menos una campaña asignada al agente
        numero_externo = '351111111'
        self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
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

    def test_crear_usuario_tipo_agente_como_administrador(self):
        # login como admin
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        agente_username = uuid.uuid4().hex
        agente_password = uuid.uuid4().hex
        # rellenar etapa1 del wizard de creación de usuario (agente)
        link_create_user = self.browser.find_element_by_id('newUser')
        href_create_user = link_create_user.get_attribute('href')
        self.browser.get(href_create_user)
        self.browser.find_element_by_id('id_0-username').send_keys(agente_username)
        self.browser.find_element_by_id('id_0-password1').send_keys(agente_password)
        self.browser.find_element_by_id('id_0-password2').send_keys(agente_password)
        self.browser.find_element_by_id('id_0-is_agente').click()
        self.browser.find_element_by_xpath('//form[@id=\'wizardForm\']/button').click()
        sleep(1)
        self.browser.find_element_by_xpath('//select[@id=\'id_2-modulos\']/option').click()
        self.browser.find_elements_by_xpath('//select[@id=\'id_2-grupo\']/option')[1].click()
        self.browser.find_elements_by_xpath('//form[@id=\'wizardForm\']/button')[2].click()
        sleep(1)
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(agente_username))


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
