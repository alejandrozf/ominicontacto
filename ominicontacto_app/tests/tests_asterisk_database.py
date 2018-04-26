# -*- coding: utf-8 -*-

"""
Tests del metodo 'ominicontacto_app.services.asterisk_database'
"""

from __future__ import unicode_literals


from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.services.asterisk_database import CampanaFamily
from ominicontacto_app.utiles import elimina_espacios


class AsteriskDatabaseTest(OMLBaseTest):

    def setUp(self):
        self.campana_dialer = self.crear_campana_dialer()
        self.campana_entrante = self.crear_campana_entrante()

    def test_devuelve_correctamente_dict_campana_asterisk(self):
        """
        este test testea el diccionario de la family de la campana
        """
        servicio = CampanaFamily()
        dict_campana = servicio.create_dict(self.campana_entrante)

        keys_asterisk = ['QNAME', 'TYPE', 'REC', 'AMD', 'CALLAGENTACTION',
                         'RINGTIME', 'QUEUETIME', 'MAXQCALLS', 'SL', 'TC',
                         'IDJSON', 'PERMITOCCULT', 'MAXCALLS', 'FAILOVER']
        for key in keys_asterisk:
            self.assertIn(key, dict_campana.keys())

    def test_falla_key_dict_campana_asterisk(self):
        """
        este test testea el diccionario de la family de la campana y
         no encuentra key
        """
        servicio = CampanaFamily()
        dict_campana = servicio.create_dict(self.campana_entrante)

        self.assertNotIn('WAITTIME', dict_campana.keys())

        self.assertNotIn('DELAY', dict_campana.keys())

    def test_devuelve_correctamente_values_campana_entrante_asterisk(self):
        """
        este test testea los values del diccionario de la family de la campana
        entrante
        """
        servicio = CampanaFamily()
        dict_campana = servicio.create_dict(self.campana_entrante)

        nombre_campana = "{0}_{1}".format(self.campana_entrante.id,
                                          elimina_espacios(self.campana_entrante.nombre))
        self.assertEqual(dict_campana['QNAME'], nombre_campana)
        self.assertEqual(dict_campana['TYPE'], self.campana_entrante.type)
        self.assertEqual(dict_campana['REC'], self.campana_entrante.queue_campana.auto_grabacion)
        self.assertEqual(dict_campana['AMD'],
                         self.campana_entrante.queue_campana.detectar_contestadores)
        self.assertEqual(dict_campana['CALLAGENTACTION'], self.campana_entrante.tipo_interaccion)
        self.assertEqual(dict_campana['RINGTIME'], self.campana_entrante.queue_campana.timeout)
        self.assertEqual(dict_campana['QUEUETIME'], self.campana_entrante.queue_campana.wait)
        self.assertEqual(dict_campana['MAXQCALLS'], self.campana_entrante.queue_campana.maxlen)
        self.assertEqual(dict_campana['SL'], self.campana_entrante.queue_campana.servicelevel)
        audio = "oml/{0}".format(
            self.campana_entrante.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())
        self.assertEqual(dict_campana['WELCOMEPLAY'], audio)
        self.assertEqual(dict_campana['TC'], "")
        self.assertEqual(dict_campana['IDJSON'], "")
        self.assertEqual(dict_campana['PERMITOCCULT'], "")
        self.assertEqual(dict_campana['MAXCALLS'], "")
        self.assertEqual(dict_campana['FAILOVER'], "")

    def test_devuelve_correctamente_values_campana_dialer_asterisk(self):
        """
        este test testea los values del diccionario de la family de la campana
        dialer
        """
        servicio = CampanaFamily()
        dict_campana = servicio.create_dict(self.campana_dialer)

        nombre_campana = "{0}_{1}".format(self.campana_dialer.id,
                                          elimina_espacios(self.campana_dialer.nombre))
        self.assertEqual(dict_campana['QNAME'], nombre_campana)
        self.assertEqual(dict_campana['TYPE'], self.campana_dialer.type)
        self.assertEqual(dict_campana['REC'], self.campana_dialer.queue_campana.auto_grabacion)
        self.assertEqual(dict_campana['AMD'],
                         self.campana_dialer.queue_campana.detectar_contestadores)
        self.assertEqual(dict_campana['CALLAGENTACTION'], self.campana_dialer.tipo_interaccion)
        self.assertEqual(dict_campana['RINGTIME'], self.campana_dialer.queue_campana.timeout)
        self.assertEqual(dict_campana['QUEUETIME'], self.campana_dialer.queue_campana.wait)
        self.assertEqual(dict_campana['MAXQCALLS'], self.campana_dialer.queue_campana.maxlen)
        self.assertEqual(dict_campana['SL'], self.campana_dialer.queue_campana.servicelevel)
        audio = "oml/{0}".format(
            self.campana_dialer.queue_campana.audio_para_contestadores.get_filename_audio_asterisk())
        self.assertEqual(dict_campana['AMDPLAY'], audio)
        self.assertEqual(dict_campana['TC'], "")
        self.assertEqual(dict_campana['IDJSON'], "")
        self.assertEqual(dict_campana['PERMITOCCULT'], "")
        self.assertEqual(dict_campana['MAXCALLS'], "")
        self.assertEqual(dict_campana['FAILOVER'], "")
