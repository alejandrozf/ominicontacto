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
     ominicontacto_app/tests/test_integracion/tests_acceso_web.py" """

from __future__ import unicode_literals

import os
import unittest
import uuid

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, crear_user, crear_grupo, get_href, ADMIN_USERNAME,
                                     ADMIN_PASSWORD, AGENTE_PASSWORD, ADMIN_PASSWORD_RESET,
                                     TESTS_INTEGRACION_HOSTNAME)
except ImportError:
    pass

AGENTE_USERNAME = 'agente' + uuid.uuid4().hex[:5]
LOGIN_FAILURE_LIMIT = int(os.getenv('LOGIN_FAILURE_LIMIT'))
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class AccesoWebTests(unittest.TestCase):

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

    # Acceso web Agente
    def test_acceso_web_agente_acceso_exitoso(self):
        try:
            login(self.browser, AGENTE_USERNAME, AGENTE_PASSWORD)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//a[contains(@href, "/agente/logout/")]'))
            print('--Acceso web agente: Acceso exitoso.--')
        except Exception as e:
            print('--ERROR: Acceso web agente: Acceso NO exitoso.--\n{0}'.format(e))
            raise e

    def test_acceso_web_agente_acceso_denegado(self):
        try:
            clave_erronea = "test"
            login(self.browser, AGENTE_USERNAME, clave_erronea)
            self.assertEqual(self.browser.find_element_by_xpath(
                '//div[@class="alert alert-danger"]/p').text,
                'Invalid Username/Password, please try again')
            print('--Acceso web agente: Acceso denegado.--')
        except Exception as e:
            print('--ERROR: Acceso web agente: Acceso NO denegado.--\n{0}'.format(e))
            raise e

    # Acceso web Supervisor
    def test_accesos_web_usuarios_con_supervisorprofile_acceso_exitoso(self):
        tipo_usuario = ['Administrador', 'Gerente', 'Supervisor', 'Referente']
        for usuario in tipo_usuario:
            try:
                login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
                user = usuario + uuid.uuid4().hex[:5]
                password = '098098ZZZ'
                crear_user(self.browser, user, password, usuario)
                # Deslogueo
                deslogueo = '//a[contains(@href, "/accounts/logout/")]'
                get_href(self.browser, deslogueo)
                # Logueo
                login(self.browser, user, password)
                self.assertTrue(self.browser.find_element_by_xpath(
                    '//a[contains(@href, "/accounts/logout/")]'))
                get_href(self.browser, deslogueo)
                print('--Acceso web ' + usuario + ': Acceso exitoso.--')
            except Exception as e:
                print('--ERROR: Acceso web ' + usuario + ': Acceso NO exitoso.--\n{0}'.format(e))
                raise e

    def test_acceso_web_usuarios_con_supervisorprofile_acceso_denegado(self):
        tipo_usuario = ['Administrador', 'Gerente', 'Supervisor', 'Referente']
        for usuario in tipo_usuario:
            try:
                # Creacion supervisor que vamos a usar para simular un acceso denegado
                login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
                user = usuario + uuid.uuid4().hex[:5]
                password = '098098ZZZ'
                crear_user(self.browser, user, password, usuario)
                clave_erronea = 'test'
                # Deslogueo como admin
                deslogueo = '//a[contains(@href, "/accounts/logout/")]'
                get_href(self.browser, deslogueo)
                # Logueo como supervisor
                login(self.browser, user, clave_erronea)
                self.assertEqual(self.browser.find_element_by_xpath(
                    '//div[@class="alert alert-danger"]/p').text,
                    'Invalid Username/Password, please try again')
                print('--Acceso web ' + usuario + ': Acceso denegado.--')
            except Exception as e:
                print('--ERROR: Acceso web ' + usuario + ': Acceso NO denegado.--\n{0}'.format(e))
                raise e

    def test_bloqueo_y_desbloqueo_de_un_usuario(self):
        try:
            clave_erronea = 'test'
            # Intento loguearme 12 veces para bloquear la cuenta del usuario
            intentos = LOGIN_FAILURE_LIMIT + 2
            for i in range(intentos):
                login(self.browser, AGENTE_USERNAME, clave_erronea)
            texto_error = self.browser.find_element_by_xpath('//div/p').text
            self.assertEqual(texto_error[0:24], 'Haz tratado de loguearte')
            print('--Se pudo bloquear un usuario.--')
        except Exception as e:
            print('--ERROR: No se pudo bloquear un usuario.--\n{0}'.format(e))
            raise e
        try:
            # Vamos al Admin de django para desbloquear este usuario
            self.browser.get('https://{0}/admin'.format(TESTS_INTEGRACION_HOSTNAME))
            self.browser.find_element_by_name('username').send_keys(ADMIN_USERNAME)
            # Prueba con la password reseteada
            try:
                self.browser.find_element_by_name('password').send_keys(ADMIN_PASSWORD_RESET)
                self.browser.find_element_by_xpath('//div/input[@type="submit"]').click()
                sleep(2)
            except Exception:
                pass
            # Prueba con la password por defecto del admin
            try:
                self.browser.find_element_by_name('password').send_keys(ADMIN_PASSWORD)
                self.browser.find_element_by_xpath('//div/input[@type="submit"]').click()
                sleep(2)
            except Exception:
                pass
            defender = '//a[contains(@href, "/admin/defender/")]'
            get_href(self.browser, defender)
            bloqued_user = '//a[contains(@href, "/admin/defender/blocks/")]'
            get_href(self.browser, bloqued_user)
            self.browser.find_element_by_xpath(
                '//form[@action="/admin/defender/blocks/username/{0}/unblock"]/'
                'input[@type="submit"]'.format(AGENTE_USERNAME)).click()
            sleep(2)
            # Deslogueo como admin
            self.browser.get('https://{0}/'.format(TESTS_INTEGRACION_HOSTNAME))
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            get_href(self.browser, deslogueo)
            # Compruebo que el usuario esta desbloqueado
            login(self.browser, AGENTE_USERNAME, AGENTE_PASSWORD)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//div/a[contains(@href, "/agente/logout/")]'))
            print('--Se pudo desbloquear con exito un usuario.--')
        except Exception as e:
            print('--ERROR: No se pudo desbloquear con exito un usuario.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
