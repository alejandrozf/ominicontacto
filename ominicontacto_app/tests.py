
from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class SimpleSeleniumTest(TestCase):

    def test_python_site(self):
        driver = webdriver.Chrome()
        driver.get("http://www.python.org")
        assert "Python" in driver.title
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source
        driver.close()