
from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


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
    #
    # def test_python_site(self):
    #     driver = webdriver.Chrome()
    #     driver.get("http://www.python.org")
    #     assert "Python" in driver.title
    #     elem = driver.find_element_by_name("q")
    #     elem.clear()
    #     elem.send_keys("pycon")
    #     elem.send_keys(Keys.RETURN)
    #     assert "No results found." not in driver.page_source
    #     driver.close()