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

# 4)Para testear los tests de integración:
# "$TESTS_INTEGRACION='True' LOGIN_FAILURE_LIMIT=10 python ominicontacto_app/tests/tests.py"
# Para los que necesitan audio en el browser, agregar "$BROWSER_REAL='True'"

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
USER = os.getenv('USER')

CAMPANA_MANUAL = os.getenv('CAMPANA_MANUAL')

AGENTE_USERNAME = 'agente' + uuid.uuid4().hex[:5]
AGENTE_PASSWORD = '098098ZZZ'

BROWSER_REAL = os.getenv('BROWSER_REAL')
TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')
LOGIN_FAILURE_LIMIT = int(os.getenv('LOGIN_FAILURE_LIMIT'))

MSG_MICROFONO = 'Se necesita un browser real con micrófono'

TESTS_INTEGRACION_HOSTNAME = os.getenv('TESTS_INTEGRACION_HOSTNAME')
if not TESTS_INTEGRACION_HOSTNAME:
    TESTS_INTEGRACION_HOSTNAME = socket.gethostname()


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integración')
class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # super(IntegrationTests, cls).setUpClass()
        cls.setUp()
        cls._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        try:
            if cls.browser.find_elements_by_id('djHideToolBarButton'):
                print('--ERROR: Se olvido de deshabilitar Django Toolbar.--')
                raise
                exit()
        except Exception:
            pass
        group_name = 'group' + uuid.uuid4().hex[:5]
        cls.crear_grupo(group_name)
        cls.crear_agente(AGENTE_USERNAME, AGENTE_PASSWORD)
        if BROWSER_REAL == 'True':
            cls.asignar_agente_campana_manual()
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

    @classmethod
    def _login(self, username, password):
        self.browser.get('https://{0}'.format(TESTS_INTEGRACION_HOSTNAME))
        self.browser.find_element_by_name('username').send_keys(username)
        self.browser.find_element_by_name('password').send_keys(password)
        self.browser.find_element_by_tag_name('button').click()
        sleep(2)

    def get_href(self, href):
        link = self.browser.find_element_by_xpath(href)
        href = link.get_attribute('href')
        self.browser.get(href)

    @classmethod
    def asignar_agente_campana_manual(self):
        list_manual_href = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/campana_manual/lista/")]')
        href_manual = list_manual_href.get_attribute('href')
        self.browser.get(href_manual)
        link_add_agent = self.browser.find_element_by_xpath(
            '//tr[@id=\'{0}\']/td/div//a[contains(@href, "/queue_member/")]'.format(CAMPANA_MANUAL))
        href_add_agent = link_add_agent.get_attribute('href')
        self.browser.get(href_add_agent)
        self.browser.find_element_by_xpath('//select/option[contains(text(), \'{0}\')]'
                                           .format(AGENTE_USERNAME)).click()
        self.browser.find_element_by_xpath((
            "//button[@id='id_guardar']")).click()
        sleep(1)

    @classmethod
    def crear_agente(self, username, password):
        link_create_user = self.browser.find_element_by_id('newUser')
        href_create_user = link_create_user.get_attribute('href')
        self.browser.get(href_create_user)
        self.browser.find_element_by_id('id_0-username').send_keys(username)
        self.browser.find_element_by_id('id_0-first_name').send_keys(username)
        self.browser.find_element_by_id('id_0-password1').send_keys(password)
        self.browser.find_element_by_id('id_0-password2').send_keys(password)
        self.browser.find_element_by_id('id_0-is_agente').click()
        self.browser.find_element_by_xpath('//form[@id=\'wizardForm\']/button').click()
        sleep(1)
        self.browser.find_elements_by_xpath('//select[@id=\'id_2-grupo\']/option')[1].click()
        self.browser.find_elements_by_xpath('//form[@id=\'wizardForm\']/button')[2].click()
        sleep(1)

    @classmethod
    def crear_grupo(self, group_name):
        link_create_group = self.browser.find_element_by_xpath(
            '//a[contains(@href,"/grupo/nuevo")]')
        href_create_group = link_create_group.get_attribute('href')
        self.browser.get(href_create_group)
        self.browser.find_element_by_id('id_nombre').send_keys(group_name)
        self.browser.find_element_by_id('id_auto_attend_inbound').click()
        self.browser.find_element_by_id('id_auto_attend_dialer').click()
        self.browser.find_element_by_xpath((
            "//button[@type='submit' and @id='id_registrar']")).click()
        sleep(1)

    def crear_BD(self, path, base_datos, multinum):
        self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
        href_nueva_BD = '//a[contains(@href,"/base_datos_contacto/nueva/")]'
        self.get_href(href_nueva_BD)
        self.browser.find_element_by_id('id_nombre').send_keys(base_datos)
        self.browser.find_element_by_id('id_archivo_importacion').send_keys(path)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        sleep(1)

        if multinum:
            self.browser.find_element_by_xpath('//label/input[@value = "phone"]').click()
            self.browser.find_element_by_xpath('//label/input[@value = "cell"]').click()
        else:
            self.browser.find_element_by_xpath('//label/input[@value = "telefono"]').click()

        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        sleep(1)

    def crear_blacklist(self, path, base_datos):
        link_create_blacklist = '//a[contains(@href,"/backlist/nueva")]'
        self.get_href(link_create_blacklist)
        self.browser.find_element_by_id('id_nombre').send_keys(base_datos)
        self.browser.find_element_by_id('id_archivo_importacion').send_keys(path)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        sleep(1)

    def crear_campos_formulario(self, campos):
        for items in campos:
            self.browser.find_element_by_id('id_nombre_campo').send_keys(items)
            if items == 'Nombre':
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_tipo\']/option')[1].click()
            elif items == 'Fecha nacimiento':
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_tipo\']/option')[2].click()
            elif items == 'Opciones':
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_tipo\']/option')[3].click()
                for i in range(10):
                    self.browser.find_element_by_id('id_value_item').send_keys(i)
                    self.browser.find_element_by_id('agregar_lista').click()
                    sleep(1)
            elif items == 'Comentarios':
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_tipo\']/option')[4].click()
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)

    def crear_calificacion(self, calificacion):
        for items in calificacion:
            calificacion = self.browser.find_element_by_xpath(
                "//a[contains(@href, '/calificacion/nuevo/')]")
            href_calificacion = calificacion.get_attribute('href')
            self.browser.get(href_calificacion)
            self.browser.find_element_by_id('id_nombre').send_keys(items)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'
                            .format(items)))

    def sitio_externo(self, sitio, url):
        nuevo_sitio = '//a[contains(@href, "/sitio_externo/nuevo/")]'
        self.get_href(nuevo_sitio)
        self.browser.find_element_by_id('id_nombre').send_keys(sitio)
        self.browser.find_element_by_id('id_url').send_keys(url)

    def formato_sitio(self, items):
        if items == 'multipart':
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_formato\']/option')[1].click()
        elif items == 'urlencoded':
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_formato\']/option')[2].click()
        elif items == 'text':
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_formato\']/option')[3].click()
        elif items == 'json':
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_formato\']/option')[4].click()
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
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
        try:
            self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
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
            print('--Se pudo realizar una llamada fuera de la campaña.--')
        except Exception as e:
            print('--ERROR: No se pudo realizar una llamada fuera de la campaña.--\n{0}'.format(e))
            raise e

    # def test_agente_puede_recibir_llamada_entrante(self):
    #     pass

    @unittest.skipIf(BROWSER_REAL != 'True', MSG_MICROFONO)
    def test_agente_puede_realizar_llamada_saliente_campana_sin_identificar_contacto(self):
        # asume al menos una campaña asignada al agente
        try:
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
            print('--Se pudo realizar una llamada saliente sin identificar contacto con exito.--')
        except Exception as e:
            print('--ERROR: No se pudo realizar una llamada saliente '
                  'sin identificar contacto.--\n{0}'.format(e))
            raise e

    # test de creacion y edicion de usuarios

    def test_crear_usuario_tipo_agente_como_administrador(self):
        # Creación de un agente
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            agente_username = 'agente' + uuid.uuid4().hex[:5]
            agente_password = AGENTE_PASSWORD
            # rellenar etapa1 del wizard de creación de usuario (agente)
            self.crear_agente(agente_username, agente_password)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                agente_username))
            print('--Se pudo crear un agente.')
        except Exception as e:
            print('--ERROR: No se pudo crear un agente.--\n{0}'.format(e))
            raise e
        # Editar agente
        try:
            user_list = '//a[contains(@href,"/user/list/page1/")]'
            self.get_href(user_list)
            link_edit = '//tr[@id=\'{0}\']/td/div//a'\
                        '[contains(@href,"/user/update")]'.format(agente_username)
            self.get_href(link_edit)
            nuevo_username = 'agente' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_username').clear()
            sleep(1)
            self.browser.find_element_by_id('id_username').send_keys(nuevo_username)
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                nuevo_username))
            print('--Se pudo editar un agente.--')
        except Exception as e:
            print('--ERROR: No se pudo editar un agente.--\n{0}'.format(e))
            raise e

    def test_modificar_eliminar_agente(self):
        # modificar grupo del agente.
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            agente_username = 'agente' + uuid.uuid4().hex[:5]
            agente_password = AGENTE_PASSWORD
            self.crear_agente(agente_username, agente_password)
            group_name = 'grupo' + uuid.uuid4().hex[:5]
            self.crear_grupo(group_name)
            user_list = '//a[contains(@href,"/user/list/page1/")]'
            self.get_href(user_list)
            link_update = "//tr[@id=\'{0}\']/td/a[contains"\
                          "(@href, '/user/agenteprofile/update/')]".format(agente_username)
            self.get_href(link_update)
            self.browser.find_element_by_xpath("//select[@id='id_grupo']/option[text()=\'{0}\']"
                                               .format(group_name)).click()
            sleep(1)
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.get_href(user_list)
            self.get_href(link_update)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_element_by_xpath(
                "//select[@id=\'id_grupo\']/option[text()=\'{0}\']".format(group_name)))
            print('--Se pudo modificar el grupo de un agente.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar el grupo de un agente.--\n{0}'.format(e))
            raise e
        # Eliminar agente
        try:
            self.get_href(user_list)
            link_delete = "//tr[@id=\'{0}\']/td/div//"\
                          "a[contains(@href,'/user/delete')]".format(agente_username)
            self.get_href(link_delete)
            self.browser.find_element_by_xpath((
                "//button[@type='submit']")).click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                agente_username)))
            print('--Se pudo eliminar un agente.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un agente.--\n{0}'.format(e))
            raise e

    def test_crear_usuario_tipo_customer(self):
        # Creación de clientes
        try:
            customer_username = 'cliente' + uuid.uuid4().hex[:5]
            customer_password = '098098ZZZ'
            self.crear_supervisor(customer_username, customer_password)
            self.crear_supervisor_tipo_customer()
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(customer_username))
            print('--Se pudo crear un usuario tipo customer.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un usuario tipo customer.--\n{0}'.format(e))
            raise e
        # modificar perfil a un perfil de supervisor
        try:
            user_list = '//a[contains(@href,"/user/list/page1/")]'
            self.get_href(user_list)
            link_update = "//tr[@id=\'{0}\']/td/a[contains(@href, '/supervisor/')]".format(
                          customer_username)
            self.get_href(link_update)
            self.browser.find_elements_by_xpath("//select[@id=\'id_rol\']/option")[0].click()
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.get_href(user_list)
            self.get_href(link_update)
            self.assertTrue(self.browser.find_elements_by_xpath(
                "//select[@id=\'id_rol\']/option[@value='2' and @selected]"))
            print('--Se pudo modificar a un perfil de supervisor.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar a un perfil de supervisor.--\n{0}'.format(e))
            raise e
        # Volver a modificiar a un perfil de cliente
        try:
            self.get_href(user_list)
            self.get_href(link_update)
            self.browser.find_elements_by_xpath("//select[@id=\'id_rol\']/option")[2].click()
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.get_href(user_list)
            self.get_href(link_update)
            self.assertTrue(self.browser.find_elements_by_xpath(
                "//select[@id=\'id_rol\']/option[@value='4' and @selected]"))
            print('--Se pudo modificar a un perfil de cliente.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar a un perfil de cliente.--\n{0}'.format(e))
            raise e

    def test_crear_usuario_tipo_supervisor(self):
        # Creación de supervisor
        try:
            supervisor_username = 'supervisor' + uuid.uuid4().hex[:5]
            supervisor_password = '098098ZZZ'
            self.crear_supervisor(supervisor_username, supervisor_password)
            self.crear_supervisor_tipo_gerente()
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(supervisor_username))
            print('--Se pudo crear un Supervisor Gerente.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Supervisor Gerente.--\n{0}'.format(e))
            raise e
        # modificar perfil a un perfil de administrador
        try:
            user_list = '//a[contains(@href,"/user/list/page1/")]'
            self.get_href(user_list)
            link_update = '//tr[@id=\'{0}\']/td/a[contains(@href, "/supervisor/")]'.format(
                          supervisor_username)
            self.get_href(link_update)
            self.browser.find_elements_by_xpath("//select[@id=\'id_rol\']/option")[1].click()
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.get_href(user_list)
            self.get_href(link_update)
            self.assertTrue(self.browser.find_elements_by_xpath(
                "//select[@id=\'id_rol\']/option[@value='1' and @selected]"))
            print('--Se pudo modificar a un perfil de administrador.')
        except Exception as e:
            print('--ERROR: No se pudo modificar a un perfil de administrador.--\n{0}'.format(e))
            raise e

    # test de creación y edición de grupos

    def test_crear_grupo_con_Autounpause(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_group = '//a[contains(@href,"/grupo/nuevo")]'
            self.get_href(link_create_group)
            group_name = 'grupo' + uuid.uuid4().hex[:5]
            auto_unpause = random.randrange(1, 99)
            self.browser.find_element_by_id('id_nombre').send_keys(group_name)
            self.browser.find_element_by_id('id_auto_unpause').send_keys(auto_unpause)
            self.browser.find_element_by_id('id_auto_attend_inbound').click()
            self.browser.find_element_by_id('id_auto_attend_dialer').click()
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(group_name))
            print('--Se pudo crear un grupo con autounpause.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un grupo con autounpause.--\n{0}'.format(e))
            raise e
        # Editar Grupo
        try:
            group_list = '//a[contains(@href,"/grupo/list/")]'
            self.get_href(group_list)
            link_edit = "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/update')]".format(
                group_name)
            self.get_href(link_edit)
            nuevo_groupname = 'grupo' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').clear()
            sleep(1)
            self.browser.find_element_by_id('id_nombre').send_keys(nuevo_groupname)
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                nuevo_groupname))
            print('--Se pudo editar un grupo.')
        except Exception as e:
            print('--ERROR: No se pudo editar un grupo.--\n{0}'.format(e))
            raise e

    def test_crear_eliminar_grupo_sin_Autounpause(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            group_name = 'grupo' + uuid.uuid4().hex[:5]
            self.crear_grupo(group_name)
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(group_name))
            print('--Se pudo crear un grupo sin autounpause.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un grupo sin autounpause.--\n{0}'.format(e))
            raise e
        # Eliminar grupo
        try:
            group_list = '//a[contains(@href,"/grupo/list/")]'
            self.get_href(group_list)
            link_delete = "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/delete')]".format(
                group_name)
            self.get_href(link_delete)
            self.browser.find_element_by_xpath((
                "//button[@type='submit']")).click()
            sleep(1)
            self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                group_name)))
            print('--Se pudo eliminar un grupo.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un grupo.--\n{0}'.format(e))
            raise e

    # Acceso Web Administrador
    def test_acceso_web_administrador_acceso_exitoso(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//div/a[contains(@href, "/accounts/logout/")]'))
            print('--Acceso web administrador: Acceso exitoso.--')
        except Exception as e:
            print('--ERROR: Acceso web administrador: Acceso NO exitoso.--\n{0}'.format(e))
            raise e

    def test_acceso_web_administrador_acceso_denegado(self):
        try:
            clave_erronea = "test"
            self._login(ADMIN_USERNAME, clave_erronea)
            self.assertEqual(self.browser.find_element_by_xpath(
                '//div[@class="alert alert-danger"]/p').text,
                'Invalid Username/Password, please try again')
            print('--Acceso web administrador: Acceso denegado.--')
        except Exception as e:
            print('--ERROR: Acceso web administrador: Acceso NO denegado.--\n{0}'.format(e))
            raise e

    # Acceso web Agente
    def test_acceso_web_agente_acceso_exitoso(self):
        try:
            self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//a[contains(@href, "/agente/logout/")]'))
            print('--Acceso web agente: Acceso exitoso.--')
        except Exception as e:
            print('--ERROR: Acceso web agente: Acceso NO exitoso.--\n{0}'.format(e))
            raise e

    def test_acceso_web_agente_acceso_denegado(self):
        try:
            clave_erronea = "test"
            self._login(AGENTE_USERNAME, clave_erronea)
            self.assertEqual(self.browser.find_element_by_xpath(
                '//div[@class="alert alert-danger"]/p').text,
                'Invalid Username/Password, please try again')
            print('--Acceso web agente: Acceso denegado.--')
        except Exception as e:
            print('--ERROR: Acceso web agente: Acceso NO denegado.--\n{0}'.format(e))
            raise e

    # Acceso web Supervisor
    def test_accesos_web_supervisor_acceso_exitoso(self):
        try:
            supervisor_username = 'supervisor' + uuid.uuid4().hex[:5]
            supervisor_password = '098098ZZZ'
            self.crear_supervisor(supervisor_username, supervisor_password)
            self.crear_supervisor_tipo_gerente()
            # Deslogueo como admin
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            self.get_href(deslogueo)
            # Logueo como supervisor
            self._login(supervisor_username, supervisor_password)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//a[contains(@href, "/accounts/logout/")]'))
            print('--Acceso web supervisor: Acceso exitoso.--')
        except Exception as e:
            print('--ERROR: Acceso web supervisor: Acceso NO exitoso.--\n{0}'.format(e))
            raise e

    def test_acceso_web_supervisor_acceso_denegado(self):
        try:
            # Creación supervisor que vamos a usar para simular un acceso denegado
            supervisor_username = 'supervisor' + uuid.uuid4().hex[:5]
            supervisor_password = '098098ZZZ'
            self.crear_supervisor(supervisor_username, supervisor_password)
            clave_erronea = 'test'
            # Deslogueo como admin
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            self.get_href(deslogueo)
            # Logueo como supervisor
            self._login(supervisor_username, clave_erronea)
            self.assertEqual(self.browser.find_element_by_xpath(
                '//div[@class="alert alert-danger"]/p').text,
                'Invalid Username/Password, please try again')
            print('--Acceso web supervisor: Acceso denegado.--')
        except Exception as e:
            print('--ERROR: Acceso web supervisor: Acceso NO denegado.--\n{0}'.format(e))
            raise e

    # Acceso web Customer
    def test_acceso_web_cliente_acceso_exitoso(self):
        try:
            # Creación supervisor que vamos a usar para simular un acceso exitoso
            customer_username = 'cliente' + uuid.uuid4().hex[:5]
            customer_password = '098098ZZZ'
            self.crear_supervisor(customer_username, customer_password)
            self.crear_supervisor_tipo_customer()
            # Deslogue como admin
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            self.get_href(deslogueo)
            # Logueo como cliente
            self._login(customer_username, customer_password)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//div/a[contains(@href, "/accounts/logout/")]'))
            print('--Acceso web cliente: Acceso exitoso.--')
        except Exception as e:
            print('--ERROR: Acceso web cliente: Acceso NO exitoso.--\n{0}'.format(e))
            raise e

    def test_acceso_web_cliente_acceso_denegado(self):
        try:
            # Creación supervisor que vamos a usar para simular un acceso denegado
            customer_username = 'cliente' + uuid.uuid4().hex[:5]
            customer_password = '098098ZZZ'
            self.crear_supervisor(customer_username, customer_password)
            self.crear_supervisor_tipo_customer()
            clave_erronea = 'test'
            # Deslogue como admin
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            self.get_href(deslogueo)
            # Logueo como cliente
            self._login(customer_username, clave_erronea)
            self.assertEqual(self.browser.find_element_by_xpath(
                '//div[@class="alert alert-danger"]/p').text,
                'Invalid Username/Password, please try again')
            print('--Acceso web cliente: Acceso denegado.--')
        except Exception as e:
            print('--ERROR: Acceso web cliente: Acceso NO denegado.--\n{0}'.format(e))
            raise e

    def test_bloqueo_y_desbloqueo_de_un_usuario(self):
        try:
            clave_erronea = 'test'
            # Intento loguearme 12 veces para bloquear la cuenta del usuario
            intentos = LOGIN_FAILURE_LIMIT + 2
            for i in range(intentos):
                self._login(AGENTE_USERNAME, clave_erronea)
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
            self.browser.find_element_by_name('password').send_keys(ADMIN_PASSWORD)
            self.browser.find_element_by_xpath('//div/input[@type="submit"]').click()
            sleep(2)
            defender = '//a[contains(@href, "/admin/defender/")]'
            self.get_href(defender)
            bloqued_user = '//a[contains(@href, "/admin/defender/blocks/")]'
            self.get_href(bloqued_user)
            self.browser.find_element_by_xpath(
                '//form[@action="/admin/defender/blocks/username/{0}/unblock"]/'
                'input[@type="submit"]'.format(AGENTE_USERNAME)).click()
            sleep(2)
            # Deslogueo como admin
            self.browser.get('https://{0}/'.format(TESTS_INTEGRACION_HOSTNAME))
            deslogueo = '//a[contains(@href, "/accounts/logout/")]'
            self.get_href(deslogueo)
            # Compruebo que el usuario esta desbloqueado
            self._login(AGENTE_USERNAME, AGENTE_PASSWORD)
            self.assertTrue(self.browser.find_element_by_xpath(
                '//div/a[contains(@href, "/agente/logout/")]'))
            print('--Se pudo desbloquear con exito un usuario.--')
        except Exception as e:
            print('--ERROR: No se pudo desbloquear con exito un usuario.--\n{0}'.format(e))
            raise e

    def test_crear_modificar_eliminar_audio(self):
        try:
            # Crear audio
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            audio_list = '//a[contains(@href,"/audios/")]'
            self.get_href(audio_list)
            audio_create = '//a[contains(@href,"/audios/create/")]'
            self.get_href(audio_create)
            descripcion_audio = 'audio' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_descripcion').send_keys(descripcion_audio)
            wav_path = "/home/{0}/ominicontacto/test/wavs/8k16bitpcm.wav". format(USER)
            self.browser.find_element_by_id('id_audio_original').send_keys(wav_path)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.find_elements_by_xpath('//tr[text()=\'{0}\']'.format(
                descripcion_audio))
            print('--Se pudo crear un audio.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un audio.--\n{0}'.format(e))
            raise e
        # Modificar Audio
        try:
            duracion_wav_path = 13
            duracion_nuevo_wav = 35
            self.browser.find_element_by_xpath(
                '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                    descripcion_audio)).click()
            nuevo_wav = "/home/{0}/ominicontacto/test/wavs/audio1.wav".format(USER)
            self.browser.find_element_by_id('id_audio_original').send_keys(nuevo_wav)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.find_element_by_xpath(
                '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                    descripcion_audio)).click()
            self.browser.find_element_by_id('id_audio_original').send_keys(nuevo_wav)
            self.assertNotEqual(self.browser.find_element_by_xpath(
                "//input[text()=\'{0}\']".format(duracion_nuevo_wav)), duracion_wav_path)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            print('--Se pudo modificar un audio.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar un audio.--\n{0}'.format(e))
            raise e
        # Eliminar Audio
        try:
            self.browser.find_element_by_xpath(
                '//tr[@id=\'{0}\']//a[contains(@href, "/eliminar/")]'.format(
                    descripcion_audio)).click()
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[text()=\'{0}\']'
                             .format(nuevo_wav)))
            print('--Se pudo eliminar un audio.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un audio.--\n{0}'.format(e))
            raise e

    def test_subir_audio_erroneo(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            audio_list = '//a[contains(@href,"/audios/")]'
            self.get_href(audio_list)
            audio_create = '//a[contains(@href,"/audios/create/")]'
            self.get_href(audio_create)
            descripcion_audio = 'audio' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_descripcion').send_keys(descripcion_audio)
            wav_path = "/home/{0}/ominicontacto/test/wavs/error_audio.mp3".format(USER)
            self.browser.find_element_by_id('id_audio_original').send_keys(wav_path)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.find_elements_by_xpath('//ul/li[text()="Allowed files: .wav"]')
            print('--No se permitio subir un audio erroneo.--')
        except Exception as e:
            print('--ERROR: Permitio subir un audio erroneo.--\n{0}'.format(e))
            raise e

    def test_pausa_productiva(self):
        try:
            # crear pausa productiva
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_pausa = '//a[contains(@href,"/pausa/nuevo")]'
            self.get_href(link_create_pausa)
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
            self.get_href(link_edit)
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
            self.get_href(link_delete)
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
            self.get_href(link_reactivate)
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
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_pausa = '//a[contains(@href,"/pausa/nuevo")]'
            self.get_href(link_create_pausa)
            pausa_nueva = 'pausa_rec' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').send_keys(pausa_nueva)
            self.browser.find_element_by_xpath("//select/option[@value = 'R']").click()
            sleep(1)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_nueva)))
            print('--Se pudo crear una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo crear una pausa recreativa.--\n{0}'.format(e))
            raise e
        # modificar pausa recreativa
        try:
            link_edit = '//tr[@id=\'{0}\']//a[contains(@href, "/pausa/update/")]'.format(
                pausa_nueva)
            self.get_href(link_edit)
            pausa_productiva = 'pausa_pro' + uuid.uuid4().hex[:5]
            self.browser.find_element_by_id('id_nombre').clear()
            sleep(1)
            self.browser.find_element_by_id('id_nombre').send_keys(pausa_productiva)
            self.browser.find_element_by_xpath("//select/option[@value = 'P']").click()
            sleep(1)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_productiva)))
            print('--Se pudo modificar una pausa recreativa.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar una pausa recreativa.--\n{0}'.format(e))
            raise e
        # eliminar pausa productiva
        try:
            link_delete = "//tr[@id=\'{0}\']//a[contains(@href, '/pausa/delete/')]".format(
                pausa_productiva)
            self.get_href(link_delete)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath(
                "//tr[@id='pausa_eliminada']//td[contains(text(), \'{0}\')]".format(
                    pausa_productiva)))
            print('--Se pudo eliminar una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar una pausa productiva.--\n{0}'.format(e))
            raise e
        # reactivar pausa productiva
        try:
            link_reactivate = "//tr[@id='pausa_eliminada']//td[@id=\'{0}\']//"\
                "a[contains(@href, '/pausa/delete/')]".format(pausa_productiva)
            self.get_href(link_reactivate)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                pausa_productiva)))
            print('--Se pudo reactivar una pausa productiva.--')
        except Exception as e:
            print('--ERROR: No se pudo reactivar una pausa productiva.--\n{0}'.format(e))
            raise e

        # Base de datos de contactos
    def test_crear_ocultar_base_de_datos(self):
        # Crear nueva base de datos
        try:
            csv_path = "/home/{0}/ominicontacto/ominicontacto_app/static/ominicontacto"\
                "/oml-example-db.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = False
            self.crear_BD(csv_path, BD_nueva, multinum)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                BD_nueva)))
            print('--Se pudo crear una BD.--')
        except Exception as e:
            print('--ERROR: No se pudo crear una BD.--\n{0}'.format(e))
            raise e
        # Ocultar Base de datos
        try:
            lista_BD = '//a[contains(@href,"/base_datos_contacto/")]'
            self.get_href(lista_BD)
            ocultar_BD = '//tr[@id=\'{0}\']//td//a[contains(@href, "/ocultar/")]'.format(
                BD_nueva)
            self.get_href(ocultar_BD)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                BD_nueva)))
            self.browser.find_element_by_xpath('//a[@onclick]').click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            desocultar = '//tr[@id=\'{0}\']//td//a[contains(@href, "/desocultar/")]'.format(
                BD_nueva)
            self.get_href(desocultar)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                BD_nueva)))
            print('--Se oculto y desoculto con exito una base de datos.--')
        except Exception as e:
            print('--ERROR: No se pudo ocultar y desocultar una base de datos.--\n{0}'.format(e))
            raise e

    def test_editar_eliminar_lista_contacto_base(self):
        # Editar Lista de Contacto
        try:
            csv_path = "/home/{0}/ominicontacto/ominicontacto_app/static/ominicontacto"\
                "/oml-example-db.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = False
            self.crear_BD(csv_path, BD_nueva, multinum)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            self.get_href(lista_contacto)
            contacto = '4553101'
            editar_contacto = '//tr[@id=\'{0}\']//td//a[contains(@href, "/update/")]'.format(
                contacto)
            self.get_href(editar_contacto)
            self.browser.find_element_by_id('id_telefono').clear()
            sleep(1)
            nuevo_telefono = '4789032'
            self.browser.find_element_by_id('id_telefono').send_keys(nuevo_telefono)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                nuevo_telefono)))
            print('--Se pudo editar un contacto en la BD.--')
        except Exception as e:
            print('--ERROR: No se pudo editar un contacto en la BD.--\n{0}'.format(e))
            raise e
        # Eliminar lista de contacto
        try:
            lista_BD = '//a[contains(@href,"/base_datos_contacto/")]'
            self.get_href(lista_BD)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            self.get_href(lista_contacto)
            eliminar_contacto = '//tr[@id=\'{0}\']//td//a[contains(@href, "/eliminar/")]'.format(
                nuevo_telefono)
            self.get_href(eliminar_contacto)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                nuevo_telefono)))
            print('--Se pudo eliminar un contacto en la BD.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un contacto en la BD.--\n{0}'.format(e))
            raise e

    def test_crear_agregar_contacto_base_multinum(self):
        # Crear Base Multinum
        try:
            csv_path = "/home/{0}/ominicontacto/test/base_prueba_multinum.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = True
            self.crear_BD(csv_path, BD_nueva, multinum)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                BD_nueva)))
            print('--Se pudo crear una BD Multinum.--')
        except Exception as e:
            print('--ERROR: No se pudo crear una BD Multinum.--\n{0}'.format(e))
            raise e
        # Agregar un Contacto
        try:
            agregar_contacto = '//tr[@id=\'{0}\']//td//a[contains'\
                               '(@href, "/agregar_contacto/")]'.format(BD_nueva)
            self.get_href(agregar_contacto)
            telefono = '3456789'
            cell = '154352879'
            self.browser.find_element_by_id('id_telefono').send_keys(telefono)
            self.browser.find_element_by_id('id_cell').send_keys(cell)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            self.get_href(lista_contacto)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                telefono)))
            print('--Se pudo agregar un solo contacto a la BD.--')
        except Exception as e:
            print('--ERROR: No se pudo agregar un solo contacto a la BD.--\n{0}'.format(e))
            raise e

    def test_crear_agregar_csv_base_multinum(self):
        # Agregar un CSV
        try:
            csv_path = "/home/{0}/ominicontacto/test/base_prueba_multinum.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = True
            self.crear_BD(csv_path, BD_nueva, multinum)
            nuevo_path = "/home/{0}/ominicontacto/test/base_prueba_multinum2.csv".format(USER)
            lista_BD = '//a[contains(@href,"/base_datos_contacto/")]'
            self.get_href(lista_BD)
            agregar_csv = '//tr[@id=\'{0}\']//td//a[contains(@href, "/actualizar/")]'.format(
                BD_nueva)
            self.get_href(agregar_csv)
            self.browser.find_element_by_id('id_archivo_importacion').send_keys(nuevo_path)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            numero = '351351319'
            self.get_href(lista_BD)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            self.get_href(lista_contacto)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                numero)))
            print('--Se puede agregar contactos a la BD a traves de un .CSV--')
        except Exception as e:
            print('--ERROR: No se pudo agregar contactos a la BD a'
                  'traves de un CSV.--\n{0}'.format(e))
            raise e

    def test_crear_blacklist(self):
        try:
            # Crear nueva blacklist
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            blacklist = 'blacklist' + uuid.uuid4().hex[:5]
            csv_path = "/home/{0}/ominicontacto/test/planilla-ejemplo-0.csv".format(USER)
            self.crear_blacklist(csv_path, blacklist)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                            .format(blacklist)))
            print('--Se pudo crear un Blacklist.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Blacklist.--\n{0}'.format(e))
            raise e
        # Verificación que solo muestra la ultima Blacklist subida
        try:
            nueva_blacklist = 'blacklist' + uuid.uuid4().hex[:5]
            csv_nueva = "/home/{0}/ominicontacto/test/planilla-ejemplo-0.csv".format(USER)
            self.crear_blacklist(csv_nueva, nueva_blacklist)
            self.assertFalse(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                             .format(blacklist)))
            self.assertTrue(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                            .format(nueva_blacklist)))
            print('--Se verifico que solo muestra la ultima Blacklist.--')
        except Exception as e:
            print('--ERROR: No se pudo verificar que solo se'
                  'muestra la ultima Blacklist.--\n{0}'.format(e))
            raise e

    def test_crear_update_calificaciones(self):
        # Crear 7 nuevas calificaciones.
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            lista_calificaciones = ['Venta', 'No Venta', 'No Interesado',
                                    'No conoce', 'Ya Tiene', 'Es jubilado']
            self.crear_calificacion(lista_calificaciones)
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
        # Eliminar la calificación: "No se encuentra".
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            calificacion = 'No se encuentra'
            lista_calificaciones = [calificacion]
            self.crear_calificacion(lista_calificaciones)
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

    def test_crear_formularios(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            nuevo_formulario = '//a[contains(@href, "/formulario/nuevo")]'
            self.get_href(nuevo_formulario)
            nombre_form = 'form' + uuid.uuid4().hex[:5]
            descripcion = 'Este form fue generado para tests'
            self.browser.find_element_by_id('id_nombre').send_keys(nombre_form)
            self.browser.find_element_by_id('id_descripcion').send_keys(descripcion)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            nombre_campos = ['Nombre', 'Fecha nacimiento', 'Opciones', 'Comentarios']
            self.crear_campos_formulario(nombre_campos)
            continuar = '//a[contains(@href, "/vista_previa/")]'
            self.get_href(continuar)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element_by_xpath("//button[@id='finalizar']").click()
            sleep(1)
            lista_form = '//a[contains(@href, "/formulario/list/")]'
            self.get_href(lista_form)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            vista_previa = '//tr[@id = \'{0}\']//a[contains(@href, "/vista/")]'.format(
                nombre_form)
            self.get_href(vista_previa)
            id_campos = ['id_Nombre', 'id_Fecha nacimiento', 'id_Opciones', 'id_Comentarios']
            for items in id_campos:
                self.assertTrue(self.browser.find_elements_by_id(items))
            print('--Se pudo crear un Formulario.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Formulario.-- \n{0}' .format(e))
            raise e
        # Ocultar y Mostrar Formulario.
        try:
            self.get_href(lista_form)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_element_by_xpath(
                '//tr[@id=\'{0}\']//span[@id="ocultar"]'.format(nombre_form)).click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath(
                '//tr[@id=\'{0}\']'.format(nombre_form)))
            mostrar_ocultos = '//a[contains(@href, "formulario/list/mostrar_ocultos/")]'
            self.get_href(mostrar_ocultos)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_elements_by_xpath(
                '//tr[@id=\'{0}\']'.format(nombre_form)))
        except Exception as e:
            print('--ERROR: No se pudo ocultar y mostrar un formulario.-- \n{0}'.format(e))
            raise e

    def test_sistema_externo(self):
        # Crear Sistema Externo
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            nuevo_sistema = '//a[contains(@href, "/sistema_externo/nuevo/")]'
            self.get_href(nuevo_sistema)
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
            update_sistema = '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                sistema_externo)
            self.get_href(update_sistema)
            nuevo_id = 'id' + uuid.uuid4().hex[:5]
            self.browser.find_elements_by_xpath(
                '//select[@id=\'id_agente_en_sistema-1-agente\']/option')[2].click()
            self.browser.find_element_by_id(
                'id_agente_en_sistema-1-id_externo_agente').send_keys(nuevo_id)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.get_href(update_sistema)
            self.assertTrue(self.browser.find_elements_by_xpath(
                '//input[@value=\'{0}\']'.format(nuevo_id)))
            print('--Se pudo modificar un Sistema Externo.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar el Sistema Externo--\n{0}'.format(e))
            raise e

    def test_crear_delete_sitio_externo_agente_get(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            sitio_get = 'sitio' + uuid.uuid4().hex[:5]
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Get
            self.sitio_externo(sitio_get, url)
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
            self.get_href(delete_sitio)
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
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            formato = ['multipart', 'urlencoded', 'text', 'json']
            for items in formato:
                sitio_externo = 'sitio' + uuid.uuid4().hex[:5]
                self.sitio_externo(sitio_externo, url)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[0].click()
                self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[1].click()
                self.formato_sitio(items)
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                self.assertTrue(self.browser.find_element_by_xpath('//tr[@id=\'{0}\']'.format(
                    sitio_externo)))
                # Modificar a Disparador Servidor
                update_servidor = '//tr[@id=\'{0}\']//a[contains(@href, "/update/")]'.format(
                    sitio_externo)
                self.get_href(update_servidor)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[2].click()
                self.browser.find_element_by_xpath("//button[@type='submit']").click()
                sleep(1)
                self.assertTrue(self.browser.find_elements_by_xpath(
                    '//tr[@id=\'{0}\']//td[@id = "Server"]'.format(sitio_externo)))
            print('--Se pudo crear un Sitio externo para el disparador agente, metodo POST.--')
            print('--Se pudo modificar el sitio Externo a disparador servidor.--')
        except Exception as e:
            print('--ERROR: No se pudo crear Sitio Externo con disparador Agente, '
                  'metodo POST y luego modificarlos a disparador Servidor.--\n{0}'.format(e))
            raise e

    def test_crear_update_sitio_externo_automatico_get(self):
        try:
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            sitio_get = 'sitio' + uuid.uuid4().hex[:5]
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Get
            self.sitio_externo(sitio_get, url)
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
            self.get_href(update_servidor)
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
            self._login(ADMIN_USERNAME, ADMIN_PASSWORD)
            url = 'www.test' + uuid.uuid4().hex[:5] + '.com'
            # Metodo Post
            formato = ['multipart', 'urlencoded', 'text', 'json']
            for items in formato:
                sitio_externo = 'sitio' + uuid.uuid4().hex[:5]
                self.sitio_externo(sitio_externo, url)
                self.browser.find_elements_by_xpath(
                    '//select[@id=\'id_disparador\']/option')[1].click()
                self.browser.find_elements_by_xpath('//select[@id=\'id_metodo\']/option')[1].click()
                self.formato_sitio(items)
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                self.assertTrue(self.browser.find_element_by_xpath('//tr[@id=\'{0}\']'.format(
                    sitio_externo)))
            print('--Se pudo crear un Sitio externo para el disparador Automatico, metodo POST--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Sitio '
                  'Externo con disparador automatico, metodo POST--\n{0}'.format(e))
            raise e
        try:
            # Ocultar y mostrar Sitio Externo
            ocultar_sitio = '//tr[@id=\'{0}\']//a[contains(@href, "/ocultar/")]'.format(
                sitio_externo)
            self.get_href(ocultar_sitio)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_externo)))
            self.browser.find_element_by_xpath('//a[@onclick]').click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            desocultar = '//tr[@id=\'{0}\']//td//a[contains(@href, "/desocultar/")]'.format(
                sitio_externo)
            self.get_href(desocultar)
            self.assertTrue(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                sitio_externo)))
            print('--Se pudo ocultar y mostrar un Sitio externo.--')
        except Exception as e:
            print('--ERROR: No se pudo ocultar y mostrar un Sitio externo.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
