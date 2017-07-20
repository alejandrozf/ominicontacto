import time

from django.test import TestCase
from selenium import webdriver


class SimpleSeleniumTest(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1366, 760)
        self.driver.get("https://172.16.20.90/accounts/login")
        self.driver.find_element_by_name("username").send_keys("fulano")
        self.driver.find_element_by_name("password").send_keys("098098ZZZ")
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

    def test_webphone_abierto_al_inicio(self):

        for _ in range(10):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)

        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.close()

    def test_cerrar_webphone(self):
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
    # def test_sip_oncall_agente(self):
    # def test_sip_acw_agente(self):

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

    def test_quitar_pausa_agente(self):
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

        for _ in range(9):
            if self.driver.find_element_by_id("Resume").get_attribute("enabled"):
                break
            time.sleep(1)
        self.driver.find_element_by_id("Resume").click()
        self.assertEquals(self.driver.find_element_by_id("UserStatus").text, "Online")
        self.driver.close()

    def test_dial_status_idle(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(10):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.close()

    def test_dial_status_calling(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("numberToCall").send_keys("1234")
        self.driver.find_element_by_id("call").click()
        for _ in range(9):
            if self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        self.driver.find_element_by_id("SelectCamp").click()
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status").text == "Calling.... 1234":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Calling.... 1234")
        self.driver.close()

    def test_dial_status_connected(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(19):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("numberToCall").send_keys("1234")
        self.driver.find_element_by_id("call").click()
        for _ in range(9):
            if self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        self.driver.find_element_by_id("SelectCamp").click()
        for _ in range(14):
            if self.driver.find_element_by_id("dial_status").text == "Calling.... 1234":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Calling.... 1234")
        for _ in range(19):
            if self.driver.find_element_by_id("dial_status").text == "Connected":
                break
            time.sleep(1)

        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Connected")
        self.driver.close()

    def test_abre_modal_select_camp_manual_call(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(19):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(10):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("numberToCall").send_keys("1234")
        self.driver.find_element_by_id("call").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        self.driver.close()

    def test_cierra_modal_select_camp_manual_call(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(10):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("numberToCall").send_keys("1234")
        self.driver.find_element_by_id("call").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        self.driver.find_element_by_id("modalSelectCmp").find_element_by_class_name("close").click()
        for _ in range(10):
            if not self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertFalse(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        self.driver.close()

    def test_navegar_a_agenda(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(10):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("modalWebCall").find_element_by_class_name("close").click()
        for _ in range(10):
            if not self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertFalse(self.driver.find_element_by_id("modalWebCall").is_displayed())
        self.driver.find_element_by_link_text("Agenda").click()
        time.sleep(8)
        self.assertEquals(self.driver.find_element_by_id("dataView").get_attribute("src"), "https://172.16.20.90/agenda/agente_list/")

        # def test_sip_status_registered(self):
        # def test_sip_status_registration_failed(self):
        # def test_sip_status_no_account(self):

    def test_elegir_camp_llam_manual(self):
        for _ in range(9):
            if self.driver.find_element_by_id("modalWebCall").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalWebCall").is_displayed())
        for _ in range(9):
            if self.driver.find_element_by_id("CallStatus"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("CallStatus"))
        time.sleep(9)
        for _ in range(9):
            if self.driver.find_element_by_id("dial_status"):
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("dial_status"))
        for _ in range(10):
            if self.driver.find_element_by_id("dial_status").text == "Idle":
                break
            time.sleep(1)
        self.assertEquals(self.driver.find_element_by_id("dial_status").text, "Idle")
        self.driver.find_element_by_id("numberToCall").send_keys("1234")
        self.driver.find_element_by_id("call").click()
        for _ in range(10):
            if self.driver.find_element_by_id("modalSelectCmp").is_displayed():
                break
            time.sleep(1)
        self.assertTrue(self.driver.find_element_by_id("modalSelectCmp").is_displayed())
        for _ in range(10):
            if self.driver.find_element_by_id("cmpList").get_attribute("value") == 36:
                break
            time.sleep(1)
        self.assertEquals('36', self.driver.find_element_by_id("cmpList").get_attribute("value"))