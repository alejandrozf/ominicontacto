
from django.test import TestCase
from selenium import webdriver

class SimpleSeleniumTest(TestCase):

    def test_pagina_principal_carga_ok(self):
        driver = webdriver.Chrome()
        driver.get("https://172.16.20.90/accounts/login")
        self.assertEquals(driver.title, "Logueo Usuario")
        driver.close()

    def test_login_agente_ok(self):
        driver = webdriver.Chrome()
        driver.get("https://172.16.20.90/accounts/login")
        driver.find_element_by_name("username").send_keys("usuariodeSuper1")
        driver.find_element_by_name("password").send_keys("098098zzz")
        driver.find_element_by_css_selector("button.btn.btn-success").click()
        self.assertEquals(driver.current_url, "https://172.16.20.90/node/")
        driver.close()

    def test_login_agente_webphone_abierto_al_inicio(self):
        driver = webdriver.Chrome()
        driver.get("https://172.16.20.90/accounts/login")
        driver.find_element_by_name("username").send_keys("usuariodeSuper1")
        driver.find_element_by_name("password").send_keys("098098zzz")
        driver.find_element_by_css_selector("button.btn.btn-success").click()

        for _ in range(10):
            if driver.find_element_by_id("modalWebCall").is_displayed():
                break
            import time
            time.sleep(1)

        self.assertTrue(driver.find_element_by_id("modalWebCall").is_displayed())
        driver.close()

    def test_login_agente_cerrar_webphone(self):
        driver = webdriver.Chrome()
        driver.set_window_size(1366, 760)
        driver.get("https://172.16.20.90/accounts/login")
        driver.find_element_by_name("username").send_keys("usuariodeSuper1")
        driver.find_element_by_name("password").send_keys("098098zzz")
        driver.find_element_by_css_selector("button.btn.btn-success").click()

        for _ in range(10):
            if driver.find_element_by_id("modalWebCall").is_displayed():
                break
            import time
            time.sleep(1)

        self.assertTrue(driver.find_element_by_id("modalWebCall").is_displayed())
        driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()

        for _ in range(10):
            if not driver.find_element_by_id("modalWebCall").is_displayed():
                break
            import time
            time.sleep(1)

        self.assertFalse(driver.find_element_by_id("modalWebCall").is_displayed())
        driver.close()

    def test_online_agente(self):
        driver = webdriver.Chrome()
        driver.get("https://172.16.20.90/accounts/login")
        driver.find_element_by_name("username").send_keys("usuariodeSuper1")
        driver.find_element_by_name("password").send_keys("098098zzz")
        driver.find_element_by_css_selector("button.btn.btn-success").click()

        for _ in range(10):
            if driver.find_element_by_id("UserStatus").text == "Online":
                break
            import time
            time.sleep(1)

        self.assertEqual(driver.find_element_by_id("UserStatus").text, "Online")
        driver.close()

    # def test_pausar_agente(self):
    #     driver = webdriver.Chrome()
    #     driver.get("https://172.16.20.90/accounts/login")
    #     elem = driver.find_element_by_id("Pause")
    #     elem.click()
    #     self.assertEqual("")
    #     elem.send_keys("pycon")
    #     elem.send_keys(Keys.RETURN)
    #     assert "No results found." not in driver.page_source
    #     driver.close()