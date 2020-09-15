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
     ominicontacto_app/tests/test_integracion/tests_usuarios.py" """

from __future__ import unicode_literals

import unittest
import uuid
import random
import os

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, crear_grupo, crear_user, get_href, ADMIN_USERNAME,
                                     ADMIN_PASSWORD, AGENTE_PASSWORD)
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class UsuariosTests(unittest.TestCase):

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

    # test de creacion y edicion de usuarios

    def test_crear_usuario_tipo_agente_como_administrador(self):
        # Creacion de un agente
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            agente_username = 'agente' + uuid.uuid4().hex[:5]
            agente_password = AGENTE_PASSWORD
            # rellenar etapa1 del wizard de creacion de usuario (agente)
            tipo_usuario = 'Agente'
            crear_user(self.browser, agente_username, agente_password, tipo_usuario)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                agente_username))
            print('--Se pudo crear un agente.')
        except Exception as e:
            print('--ERROR: No se pudo crear un agente.--\n{0}'.format(e))
            raise e
        # Editar agente
        try:
            user_list = '//a[contains(@href,"/user/list/1/")]'
            get_href(self.browser, user_list)
            link_edit = '//tr[@id=\'{0}\']/td/div//a'\
                        '[contains(@href,"/user/agent/update")]'.format(agente_username)
            get_href(self.browser, link_edit)
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
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            agente_username = 'agente' + uuid.uuid4().hex[:5]
            agente_password = AGENTE_PASSWORD
            tipo_usuario = 'Agente'
            crear_user(self.browser, agente_username, agente_password, tipo_usuario)
            group_name = 'grupo' + uuid.uuid4().hex[:5]
            crear_grupo(self.browser, group_name)
            user_list = '//a[contains(@href,"/user/list/1/")]'
            get_href(self.browser, user_list)
            link_update = "//tr[@id=\'{0}\']/td/a[contains"\
                          "(@href, '/user/agenteprofile/update/')]".format(agente_username)
            get_href(self.browser, link_update)
            self.browser.find_element_by_xpath("//select[@id='id_grupo']/option[text()=\'{0}\']"
                                               .format(group_name)).click()
            sleep(1)
            self.browser.find_element_by_xpath((
                "//button[@type='submit' and @id='id_registrar']")).click()
            sleep(1)
            get_href(self.browser, user_list)
            get_href(self.browser, link_update)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertTrue(self.browser.find_element_by_xpath(
                "//select[@id=\'id_grupo\']/option[text()=\'{0}\']".format(group_name)))
            print('--Se pudo modificar el grupo de un agente.--')
        except Exception as e:
            print('--ERROR: No se pudo modificar el grupo de un agente.--\n{0}'.format(e))
            raise e
        # Eliminar agente
        try:
            get_href(self.browser, user_list)
            link_delete = "//tr[@id=\'{0}\']/td/div//"\
                          "a[contains(@href,'/user/agent/delete')]".format(agente_username)
            get_href(self.browser, link_delete)
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

    def test_crear_editar_usuarios_supervisorprofile(self):
        # Creacion de usuarios con SupervisorProfile
        login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
        tipo_usuario = ['Administrador', 'Gerente', 'Supervisor', 'Referente']
        for usuario in tipo_usuario:
            try:
                user = usuario + uuid.uuid4().hex[:5]
                password = '098098ZZZ'
                crear_user(self.browser, user, password, usuario)
                self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(user))
                print('Se pudo crear un ' + usuario + ' con exito.')
            except Exception as e:
                print('--ERROR: No se pudo crear un ' + usuario + ' .--\n{0}'.format(e))
                raise e
            # modificar a otro perfil
            try:
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                link_update = "//tr[@id=\'{0}\']/td/a[contains(@href, '/supervisor/')]".format(
                    user)
                get_href(self.browser, link_update)
                if usuario == 'Administrador':
                    cambio_perfil = 'Gerente'
                elif usuario == 'Gerente':
                    cambio_perfil = 'Supervisor'
                elif usuario == 'Supervisor':
                    cambio_perfil = 'Referente'
                else:
                    cambio_perfil = 'Administrador'
                self.browser.find_element_by_xpath("//select[@id='id_rol']//option[contains\
                                               (text(), \'{0}\')]".format(cambio_perfil)).click()
                self.browser.find_element_by_xpath((
                    "//button[@type='submit' and @id='id_registrar']")).click()
                sleep(1)
                user_list = '//a[contains(@href,"/user/list/1/")]'
                get_href(self.browser, user_list)
                get_href(self.browser, link_update)
                self.assertTrue(self.browser.find_element_by_xpath("//select[@id='id_rol']//option[contains\
                                               (text(), \'{0}\')]".format(cambio_perfil)))
                print('Se pudo modificar a un Perfil de ' + cambio_perfil)
            except Exception as e:
                print('--ERROR: No se pudo modificar a un perfil de \
                      ' + cambio_perfil + ' .--\n{0}'.format(e))
                raise e

    def test_crear_grupo_con_Autounpause(self):
        try:
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            link_create_group = '//a[contains(@href,"/grupo/nuevo")]'
            get_href(self.browser, link_create_group)
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
            get_href(self.browser, group_list)
            link_edit = "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/update')]".format(
                group_name)
            get_href(self.browser, link_edit)
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
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            group_name = 'grupo' + uuid.uuid4().hex[:5]
            crear_grupo(self.browser, group_name)
            self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(group_name))
            print('--Se pudo crear un grupo sin autounpause.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un grupo sin autounpause.--\n{0}'.format(e))
            raise e
        # Eliminar grupo
        try:
            group_list = '//a[contains(@href,"/grupo/list/")]'
            get_href(self.browser, group_list)
            link_delete = "//tr[@id=\'{0}\']/td/div//a[contains(@href,'/grupo/delete')]".format(
                group_name)
            get_href(self.browser, link_delete)
            self.browser.find_element_by_xpath((
                "//button[@type='submit']")).click()
            sleep(1)
            self.assertFalse(self.browser.find_elements_by_xpath('//td[text()=\'{0}\']'.format(
                group_name)))
            print('--Se pudo eliminar un grupo.--')
        except Exception as e:
            print('--ERROR: No se pudo eliminar un grupo.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
