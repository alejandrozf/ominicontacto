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
     ominicontacto_app/tests/test_integracion/tests_audio.py" """

from __future__ import unicode_literals

import os
import unittest
import uuid

from time import sleep

from integracion_metodos import (login, get_href)

try:
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
USER = os.getenv('USER')

CAMPANA_MANUAL = os.getenv('CAMPANA_MANUAL')

AGENTE_USERNAME = 'agente' + uuid.uuid4().hex[:5]
AGENTE_PASSWORD = '098098ZZZ'

TESTS_INTEGRACION = os.getenv('TESTS_INTEGRACION')


@unittest.skipIf(TESTS_INTEGRACION != 'True', 'Ignorando tests de integracion')
class AudioTests(unittest.TestCase):

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

    def test_crear_modificar_eliminar_audio(self):
        try:
            # Crear audio
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            audio_list = '//a[contains(@href,"/audios/")]'
            get_href(self.browser, audio_list)
            audio_create = '//a[contains(@href,"/audios/create/")]'
            get_href(self.browser, audio_create)
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
            login(self.browser, ADMIN_USERNAME, ADMIN_PASSWORD)
            audio_list = '//a[contains(@href,"/audios/")]'
            get_href(self.browser, audio_list)
            audio_create = '//a[contains(@href,"/audios/create/")]'
            get_href(self.browser, audio_create)
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


if __name__ == '__main__':
    # para poder ejecutar los tests desde fuera del entorno
    unittest.main()
