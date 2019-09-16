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
import random

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

    def crear_module(self):
        create_module = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/modulo/nuevo/")]')
        href_create_module = create_module.get_attribute('href')
        self.browser.get(href_create_module)
        module_name = 'modulo_test'
        self.browser.find_element_by_id('id_nombre').send_keys(module_name)
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)

    def crear_supervisor(self, username, password):
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        link_create_user = self.browser.find_element_by_id('newUser')
        href_create_user = link_create_user.get_attribute('href')
        self.browser.get(href_create_user)
        self.browser.find_element_by_id('id_0-username').send_keys(username)
        self.browser.find_element_by_id('id_0-password1').send_keys(password)
        self.browser.find_element_by_id('id_0-password2').send_keys(password)
        self.browser.find_element_by_id('id_0-is_supervisor').click()
        self.browser.find_element_by_xpath('//form[@id=\'wizardForm\']/button').click()
        sleep(1)

    def crear_supervisor_tipo_customer(self):
        self.browser.find_elements_by_xpath('//select[@id=\'id_1-rol\']/option')[2].click()
        self.browser.find_elements_by_xpath('//form[@id=\'wizardForm\']/button')[2].click()
        sleep(1)

    def crear_supervisor_tipo_gerente(self):
        self.browser.find_elements_by_xpath('//select[@id=\'id_1-rol\']/option')[0].click()
        self.browser.find_elements_by_xpath('//form[@id=\'wizardForm\']/button')[2].click()
        sleep(1)

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

    # test de creacion y edicion de usuarios

    def test_crear_usuario_tipo_agente_como_administrador(self):
        # login como admin
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        random_username = uuid.uuid4().hex
        agente_username = random_username[:16]
        agente_password = AGENTE_PASSWORD
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
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
            agente_username))
        # Editar agente
        user_list = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/user/list/page1/")]')
        href_user_list = user_list.get_attribute('href')
        self.browser.get(href_user_list)
        link_edit = self.browser.find_element_by_xpath(
            '//tr[@id=\'{0}\']/td/div//a[contains(@href,"/user/update")]'.format(agente_username))
        href_edit = link_edit.get_attribute('href')
        self.browser.get(href_edit)
        nuevo_username = random_username[:16]
        self.browser.find_element_by_id('id_username').clear()
        sleep(1)
        self.browser.find_element_by_id('id_username').send_keys(nuevo_username)
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
            nuevo_username))
        # modificar agente, para ello debe haber 2 modulos creados.
        self.crear_module()
        self.browser.get(href_user_list)
        link_update = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/a[contains(@href, '/user/agenteprofile/update/')]".format(
                nuevo_username))
        href_update = link_update.get_attribute('href')
        self.browser.get(href_update)
        self.browser.find_element_by_xpath('//select[@id=\'id_modulos\']/option').click()
        self.browser.find_elements_by_xpath(
            '//select[@id=\'id_modulos\']/option')[1].click()
        sleep(1)
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.get(href_user_list)
        self.browser.get(href_update)
        self.assertTrue(self.browser.find_elements_by_xpath(
            "//select[@id=\'id_modulos\']/option[@value='2' and @selected='selected']"))
        # Eliminar agente
        self.browser.get(href_user_list)
        link_delete = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/user/delete')]".format(nuevo_username))
        href_delete = link_delete.get_attribute('href')
        self.browser.get(href_delete)
        self.browser.find_element_by_xpath((
            "//button[@type='submit']")).click()
        sleep(1)
        self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
            nuevo_username)))

    def test_crear_usuario_tipo_customer(self):
        # Creación de clientes
        random_customer = uuid.uuid4().hex
        customer_username = random_customer[:16]
        customer_password = '098098ZZZ'
        self.crear_supervisor(customer_username, customer_password)
        self.crear_supervisor_tipo_customer()
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(customer_username))
        # modificar perfil a un perfil de supervisor
        user_list = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/user/list/page1/")]')
        href_user_list = user_list.get_attribute('href')
        self.browser.get(href_user_list)
        link_update = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/a[contains(@href, '/supervisor/')]".format(
                customer_username))
        href_update = link_update.get_attribute('href')
        self.browser.get(href_update)
        self.browser.find_elements_by_xpath("//select[@id=\'id_rol\']/option")[0].click()
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.get(href_user_list)
        self.browser.get(href_update)
        self.assertTrue(self.browser.find_elements_by_xpath(
            "//select[@id=\'id_rol\']/option[@value='2' and @selected='selected']"))

    def test_crear_usuario_tipo_supervisor(self):
        # Creación de supervisor
        random_supervisor = uuid.uuid4().hex
        supervisor_username = random_supervisor[:16]
        supervisor_password = '098098ZZZ'
        self.crear_supervisor(supervisor_username, supervisor_password)
        self.crear_supervisor_tipo_gerente()
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(supervisor_username))
        # modificar perfil a un perfil de administrador
        user_list = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/user/list/page1/")]')
        href_user_list = user_list.get_attribute('href')
        self.browser.get(href_user_list)
        link_update = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/a[contains(@href, '/supervisor/')]".format(
                supervisor_username))
        href_update = link_update.get_attribute('href')
        self.browser.get(href_update)
        self.browser.find_elements_by_xpath("//select[@id=\'id_rol\']/option")[1].click()
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.get(href_user_list)
        self.browser.get(href_update)
        self.assertTrue(self.browser.find_elements_by_xpath(
            "//select[@id=\'id_rol\']/option[@value='1' and @selected='selected']"))

    # test de creación y edición de grupos

    def test_crear_grupo_con_Autounpause(self):
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        link_create_group = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/grupo/nuevo")]')
        href_create_group = link_create_group.get_attribute('href')
        self.browser.get(href_create_group)
        random_name = uuid.uuid4().hex
        group_name = random_name[:16]
        auto_unpause = random.randrange(1, 99)
        self.browser.find_element_by_id('id_nombre').send_keys(group_name)
        self.browser.find_element_by_id('id_auto_unpause').send_keys(auto_unpause)
        self.browser.find_element_by_id('id_auto_attend_ics').click()
        self.browser.find_element_by_id('id_auto_attend_inbound').click()
        self.browser.find_element_by_id('id_auto_attend_dialer').click()
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(group_name))
        # Editar Grupo
        group_list = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/grupo/list/")]')
        href_group_list = group_list.get_attribute('href')
        self.browser.get(href_group_list)
        link_edit = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/update')]".format(group_name))
        href_edit = link_edit.get_attribute('href')
        self.browser.get(href_edit)
        nuevo_groupname = random_name[:16]
        self.browser.find_element_by_id('id_nombre').clear()
        sleep(1)
        self.browser.find_element_by_id('id_nombre').send_keys(nuevo_groupname)
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
            nuevo_groupname))
        # Eliminar grupo
        self.browser.get(href_group_list)
        link_delete = self.browser.find_element_by_xpath(
            "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/delete')]".format(nuevo_groupname))
        href_delete = link_delete.get_attribute('href')
        self.browser.get(href_delete)
        self.browser.find_element_by_xpath((
            "//button[@type='submit']")).click()
        sleep(1)
        self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
            nuevo_groupname)))

    def test_crear_grupo_sin_Autounpause(self):
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        link_create_group = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/grupo/nuevo")]')
        href_create_group = link_create_group.get_attribute('href')
        self.browser.get(href_create_group)
        group_name = uuid.uuid4().hex
        self.browser.find_element_by_id('id_nombre').send_keys(group_name)
        self.browser.find_element_by_id('id_auto_attend_ics').click()
        self.browser.find_element_by_id('id_auto_attend_inbound').click()
        self.browser.find_element_by_id('id_auto_attend_dialer').click()
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)
        self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(group_name))

    # Acceso Web Administrador
    def test_acceso_web_administrador_acceso_exitoso(self):
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        self.assertTrue(self.browser.find_element_by_xpath(
            '//div/a[contains(@href, "/accounts/logout/")]'))

    def test_acceso_web_administrador_acceso_denegado(self):
        clave_erronea = "test"
        self._login(ADMIN_USERNAME, clave_erronea)
        self.assertEqual(self.browser.find_element_by_xpath(
            '//div[@class="alert alert-danger"]/p').text,
            'Invalid Username/Password, please try again')

    # Acceso web Agente
    def test_acceso_web_agente_acceso_exitoso(self):
        self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
        self.assertTrue(self.browser.find_element_by_xpath(
            '//a[contains(@href, "/agente/logout/")]'))

    def test_acceso_web_agente_acceso_denegado(self):
        clave_erronea = "test"
        self._login(AGENTE_USERNAME, clave_erronea)
        self.assertEqual(self.browser.find_element_by_xpath(
            '//div[@class="alert alert-danger"]/p').text,
            'Invalid Username/Password, please try again')

    # Acceso web Supervisor
    def test_accesos_web_supervisor_acceso_exitoso(self):
        random_supervisor = uuid.uuid4().hex
        supervisor_username = random_supervisor[:16]
        supervisor_password = '098098ZZZ'
        self.crear_supervisor(supervisor_username, supervisor_password)
        self.crear_supervisor_tipo_gerente()
        # Deslogueo como admin
        deslogueo = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]')
        href_deslogueo = deslogueo.get_attribute('href')
        self.browser.get(href_deslogueo)
        # Logueo como supervisor
        self._login(supervisor_username, supervisor_password)
        self.assertTrue(self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]'))

    def test_acceso_web_supervisor_acceso_denegado(self):
        # Creación supervisor que vamos a usar para simular un acceso denegado
        random_supervisor = uuid.uuid4().hex
        supervisor_username = random_supervisor[:16]
        supervisor_password = '098098ZZZ'
        self.crear_supervisor(supervisor_username, supervisor_password)
        clave_erronea = 'test'
        # Deslogueo como admin
        deslogueo = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]')
        href_deslogueo = deslogueo.get_attribute('href')
        self.browser.get(href_deslogueo)
        # Logueo como supervisor
        self._login(supervisor_username, clave_erronea)
        self.assertEqual(self.browser.find_element_by_xpath(
            '//div[@class="alert alert-danger"]/p').text,
            'Invalid Username/Password, please try again')

    # Acceso web Customer
    def test_acceso_web_cliente_acceso_exitoso(self):
        # Creación supervisor que vamos a usar para simular un acceso exitoso
        random_customer = uuid.uuid4().hex
        customer_username = random_customer[:16]
        customer_password = '098098ZZZ'
        self.crear_supervisor(customer_username, customer_password)
        self.crear_supervisor_tipo_customer()
        # Deslogue como admin
        deslogueo = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]')
        href_deslogueo = deslogueo.get_attribute('href')
        self.browser.get(href_deslogueo)
        # Logueo como cliente
        self._login(customer_username, customer_password)
        self.assertTrue(self.browser.find_element_by_xpath(
            '//div/a[contains(@href, "/accounts/logout/")]'))

    def test_acceso_web_cliente_acceso_denegado(self):
        # Creación supervisor que vamos a usar para simular un acceso denegado
        random_customer = uuid.uuid4().hex
        customer_username = random_customer[:16]
        customer_password = '098098ZZZ'
        self.crear_supervisor(customer_username, customer_password)
        self.crear_supervisor_tipo_customer()
        clave_erronea = 'test'
        # Deslogue como admin
        deslogueo = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]')
        href_deslogueo = deslogueo.get_attribute('href')
        self.browser.get(href_deslogueo)
        # Logueo como cliente
        self._login(customer_username, clave_erronea)
        self.assertEqual(self.browser.find_element_by_xpath(
            '//div[@class="alert alert-danger"]/p').text,
            'Invalid Username/Password, please try again')

    def test_bloqueo_y_desbloqueo_de_un_usuario(self):
        clave_erronea = 'test'
        # Intento loguearme 3 veces para bloquear la cuenta del usuario
        self._login(AGENTE_USERNAME, clave_erronea)
        self._login(AGENTE_USERNAME, clave_erronea)
        self._login(AGENTE_USERNAME, clave_erronea)
        texto_error = self.browser.find_element_by_xpath('//div/p').text
        self.assertEqual(texto_error[45:93], 'Tu cuenta y dirección IP permanecerán bloqueadas')
        # Vamos al Admin de django para desbloquear este usuario
        self.browser.get('https://{0}/admin'.format(socket.gethostname()))
        self.browser.find_element_by_name('username').send_keys(ADMIN_USERNAME)
        self.browser.find_element_by_name('password').send_keys(ADMIN_PASSWORD)
        self.browser.find_element_by_xpath('//div/input[@type="submit"]').click()
        sleep(2)
        defender = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/admin/defender/")]')
        href_defender = defender.get_attribute('href')
        self.browser.get(href_defender)
        bloqued_user = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/admin/defender/blocks/")]')
        href_bloqued_user = bloqued_user.get_attribute('href')
        self.browser.get(href_bloqued_user)
        self.browser.find_element_by_xpath(
            '//form[@action="/admin/defender/blocks/username/{0}/unblock"]/input[@type="submit"]'
            .format(AGENTE_USERNAME)).click()
        sleep(2)
        # Deslogueo como admin
        self.browser.get('https://{0}/'.format(socket.gethostname()))
        deslogueo = self.browser.find_element_by_xpath(
            '//a[contains(@href, "/accounts/logout/")]')
        href_deslogueo = deslogueo.get_attribute('href')
        self.browser.get(href_deslogueo)
        # Compruebo que el usuario esta desbloqueado
        self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
        self.assertTrue(self.browser.find_element_by_xpath(
            '//div/a[contains(@href, "/agente/logout/")]'))


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
