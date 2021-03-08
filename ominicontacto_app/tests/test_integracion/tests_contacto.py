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
     ominicontacto_app/tests/test_integracion/tests_contacto.py" """

from __future__ import unicode_literals

import unittest
import uuid
import os

from time import sleep

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from integracion_metodos import (login, get_href, crear_BD, crear_blacklist, ADMIN_USERNAME,
                                     ADMIN_PASSWORD, USER)
except ImportError:
    pass

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class ContactoTests(unittest.TestCase):

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

    # Base de datos de contactos
    def test_crear_ocultar_base_de_datos(self):
        # Crear nueva base de datos
        try:
            csv_path = "/home/{0}/ominicontacto/ominicontacto_app/static/ominicontacto"\
                "/example-db.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = False
            crear_BD(self.browser, csv_path, BD_nueva, multinum)
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
            get_href(self.browser, lista_BD)
            ocultar_BD = '//tr[@id=\'{0}\']//td//a[contains(@href, "/ocultar/")]'.format(
                BD_nueva)
            get_href(self.browser, ocultar_BD)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            self.assertFalse(self.browser.find_elements_by_xpath('//tr[@id=\'{0}\']'.format(
                BD_nueva)))
            self.browser.find_element_by_xpath('//a[@onclick]').click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            desocultar = '//tr[@id=\'{0}\']//td//a[4]'.format(BD_nueva)
            get_href(self.browser, desocultar)
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
                "/example-db.csv".format(USER)
            BD_nueva = 'BD' + uuid.uuid4().hex[:5]
            multinum = False
            crear_BD(self.browser, csv_path, BD_nueva, multinum)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            get_href(self.browser, lista_contacto)
            contacto = '4553101'
            editar_contacto = '//tr[@id=\'{0}\']//td//a[contains(@href, "/update/")]'.format(
                contacto)
            get_href(self.browser, editar_contacto)
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
            get_href(self.browser, lista_BD)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            get_href(self.browser, lista_contacto)
            eliminar_contacto = '//tr[@id=\'{0}\']//td//a[contains(@href, "/eliminar/")]'.format(
                nuevo_telefono)
            get_href(self.browser, eliminar_contacto)
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
            crear_BD(self.browser, csv_path, BD_nueva, multinum)
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
            get_href(self.browser, agregar_contacto)
            telefono = '3456789'
            cell = '154352879'
            self.browser.find_element_by_id('id_telefono').send_keys(telefono)
            self.browser.find_element_by_id('id_cell').send_keys(cell)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            get_href(self.browser, lista_contacto)
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
            crear_BD(self.browser, csv_path, BD_nueva, multinum)
            nuevo_path = "/home/{0}/ominicontacto/test/base_prueba_multinum2.csv".format(USER)
            lista_BD = '//a[contains(@href,"/base_datos_contacto/")]'
            get_href(self.browser, lista_BD)
            agregar_csv = '//tr[@id=\'{0}\']//td//a[contains(@href, "/actualizar/")]'.format(
                BD_nueva)
            get_href(self.browser, agregar_csv)
            self.browser.find_element_by_id('id_archivo_importacion').send_keys(nuevo_path)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            self.browser.find_element_by_xpath("//button[@type='submit']").click()
            sleep(1)
            numero = '351351319'
            get_href(self.browser, lista_BD)
            lista_contacto = '//tr[@id=\'{0}\']//a[contains(@href, "/list_contacto/")]'.format(
                BD_nueva)
            get_href(self.browser, lista_contacto)
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
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            blacklist = 'blacklist' + uuid.uuid4().hex[:5]
            csv_path = "/home/{0}/ominicontacto/test/planilla-ejemplo-0.csv".format(USER)
            crear_blacklist(self.browser, csv_path, blacklist)
            self.assertTrue(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                            .format(blacklist)))
            print('--Se pudo crear un Blacklist.--')
        except Exception as e:
            print('--ERROR: No se pudo crear un Blacklist.--\n{0}'.format(e))
            raise e
        # Verificacion que solo muestra la ultima Blacklist subida
        try:
            nueva_blacklist = 'blacklist' + uuid.uuid4().hex[:5]
            csv_nueva = "/home/{0}/ominicontacto/test/planilla-ejemplo-0.csv".format(USER)
            crear_blacklist(self.browser, csv_nueva, nueva_blacklist)
            self.assertFalse(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                             .format(blacklist)))
            self.assertTrue(self.browser.find_elements_by_xpath('//td[contains(text(), \'{0}\')]'
                            .format(nueva_blacklist)))
            print('--Se verifico que solo muestra la ultima Blacklist.--')
        except Exception as e:
            print('--ERROR: No se pudo verificar que solo se'
                  'muestra la ultima Blacklist.--\n{0}'.format(e))
            raise e


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
