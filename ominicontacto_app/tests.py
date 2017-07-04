import time

from django.test import TestCase
from selenium import webdriver


class SimpleSeleniumTest(TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1366, 760)
        self.driver.get("https://172.16.20.90/accounts/login")
        self.driver.find_element_by_name("username").send_keys("usuariodeSuper1")
        self.driver.find_element_by_name("password").send_keys("098098zzz")
        self.driver.find_element_by_css_selector("button.btn.btn-success").click()

    # def test_pagina_principal_carga_ok(self):
    #     driver = webdriver.Chrome()
    #     driver.get("https://172.16.20.90/accounts/login")
    #     self.assertEquals(driver.title, "Logueo Usuario")
    #     driver.close()

    # def test_login_agente_ok(self):
    #     driver = webdriver.Chrome()
    #     driver.get("https://172.16.20.90/accounts/login")
    #     driver.find_element_by_name("username").send_keys("usuariodeSuper1")
    #     driver.find_element_by_name("password").send_keys("098098zzz")
    #     driver.find_element_by_css_selector("button.btn.btn-success").click()
    #     self.assertEquals(driver.current_url, "https://172.16.20.90/node/")
    #     driver.close()

    def test_login_agente_webphone_abierto_al_inicio(self):

        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.close()

    def test_login_agente_cerrar_webphone(self):

        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()

        for _ in range(10):
            if not self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertFalse(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.close()

    def test_online_agente(self):

        for _ in range(10):
            if self.driver.find_element_by_id("UserStatus").text == "Online":
                break
            time.sleep(1)

        self.assertEqual(self.driver.find_element_by_id("UserStatus").text, "Online")
        self.driver.close()

    def test_abrir_modal_pausa(self):

        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()

        for _ in range(10):
            if not self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertFalse(self.driver.find_element_by_id("modalWebCall").is_displayed())

        self.driver.find_element_by_id("Pause").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalPause").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalPause").is_displayed())
        self.driver.close()

    def test_cerrar_modal_pausa(self):
        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())

        self.driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()
        for _ in range(10):
            if not self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertFalse(self.driver.find_element_by_id("modalWebCall").is_displayed())

        self.driver.find_element_by_id("Pause").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalPause").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalPause").is_displayed())

        self.driver.find_element_by_id("modalPause").find_element_by_class_name("close").click()
        for _ in range(10):
            if not self.driver.find_element_by_id("modalPause").is_displayed():
                break
            time.sleep(1)
        self.assertFalse(self.driver.find_element_by_id("modalPause").is_displayed())
        self.driver.close()

    def test_pausar_agente(self):
        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())

        self.driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()
        for _ in range(10):
            if not self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertFalse(self.driver.find_element_by_id("modalWebCall").is_displayed())

        self.driver.find_element_by_id("Pause").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalPause").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalPause").is_displayed())

        self.driver.find_element_by_id("setPause").click()
        self.assertEquals(self.driver.find_element_by_id("UserStatus").text, "Gestion")
        self.driver.close()