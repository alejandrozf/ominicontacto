# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Tests del modulo 'ominicontacto_app.services.asterisk.redis_database'
"""

from __future__ import unicode_literals

from mock import patch

from django.conf import settings
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.services.asterisk.redis_database import (
    AgenteFamily, RutaSalienteFamily, TrunkFamily, CampanaFamily
)
from configuracion_telefonia_app.tests.factories import (
    TroncalSIPFactory, RutaSalienteFactory, PatronDeDiscadoFactory, PlaylistFactory,
)
from ominicontacto_app.tests.factories import ConfiguracionDeAgentesDeCampanaFactory
from ominicontacto_app.services.audio_conversor import ConversorDeAudioService

from django.db import connections


class AsteriskDatabaseTest(OMLBaseTest):

    @patch.object(ConversorDeAudioService, '_convertir_audio')
    def setUp(self, _convertir_audio):
        self.campana_dialer = self.crear_campana_dialer()
        self.campana_entrante = self.crear_campana_entrante()
        user = self.crear_user_agente()
        self.agente = self.crear_agente_profile(user)

        connections['replica']._orig_cursor = connections['replica'].cursor
        connections['replica'].cursor = connections['default'].cursor

    def test_devuelve_correctamente_dict_campana_asterisk(self):
        """
        este test testea el diccionario de la family de la campana
        """
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_entrante)

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
        dict_campana = servicio._create_dict(self.campana_entrante)

        self.assertNotIn('WAITTIME', dict_campana.keys())

        self.assertNotIn('DELAY', dict_campana.keys())

    def test_devuelve_correctamente_values_campana_entrante_asterisk(self):
        """
        este test testea los values del diccionario de la family de la campana
        entrante
        """
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_entrante)

        nombre_campana = self.campana_entrante.get_queue_id_name()
        self.assertEqual(dict_campana['QNAME'], nombre_campana)
        self.assertEqual(dict_campana['TYPE'], self.campana_entrante.type)
        self.assertEqual(dict_campana['REC'], str(
            self.campana_entrante.queue_campana.auto_grabacion))
        self.assertEqual(dict_campana['AMD'],
                         str(self.campana_entrante.queue_campana.detectar_contestadores))
        self.assertEqual(dict_campana['CALLAGENTACTION'], self.campana_entrante.tipo_interaccion)
        self.assertEqual(dict_campana['RINGTIME'], self.campana_entrante.queue_campana.timeout)
        self.assertEqual(dict_campana['QUEUETIME'], self.campana_entrante.queue_campana.wait)
        self.assertEqual(dict_campana['MAXQCALLS'], self.campana_entrante.queue_campana.maxlen)
        self.assertEqual(dict_campana['SL'], self.campana_entrante.queue_campana.servicelevel)
        audio = "{0}{1}".format(
            settings.OML_AUDIO_FOLDER,
            self.campana_entrante.queue_campana.audio_de_ingreso.get_filename_audio_asterisk())
        self.assertEqual(dict_campana['WELCOMEPLAY'], audio)
        self.assertEqual(dict_campana['TC'], "")
        self.assertEqual(dict_campana['IDJSON'], "")
        self.assertEqual(dict_campana['PERMITOCCULT'], "")
        self.assertEqual(dict_campana['MAXCALLS'], "")
        self.assertEqual(dict_campana['FAILOVER'], str(0))
        self.assertNotIn('MOH', dict_campana['FAILOVER'])

    def test_devuelve_correctamente_value_MOH_campana_entrante_asterisk(self):
        playlist = PlaylistFactory()
        self.campana_entrante.queue_campana.musiconhold = playlist
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_entrante)
        self.assertEqual(dict_campana['MOH'], playlist.nombre)

    def test_devuelve_correctamente_values_campana_dialer_asterisk(self):
        """
        este test testea los values del diccionario de la family de la campana
        dialer
        """
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_dialer)

        nombre_campana = self.campana_dialer.get_queue_id_name()
        self.assertEqual(dict_campana['QNAME'], nombre_campana)
        self.assertEqual(dict_campana['TYPE'], self.campana_dialer.type)
        self.assertEqual(dict_campana['REC'], str(self.campana_dialer.queue_campana.auto_grabacion))
        self.assertEqual(dict_campana['AMD'],
                         str(self.campana_dialer.queue_campana.detectar_contestadores))
        self.assertEqual(dict_campana['CALLAGENTACTION'], self.campana_dialer.tipo_interaccion)
        self.assertEqual(dict_campana['RINGTIME'], "")
        self.assertEqual(dict_campana['QUEUETIME'], self.campana_dialer.queue_campana.wait)
        self.assertEqual(dict_campana['MAXQCALLS'], self.campana_dialer.queue_campana.maxlen)
        self.assertEqual(dict_campana['SL'], self.campana_dialer.queue_campana.servicelevel)
        audio = "{0}{1}".format(
            settings.OML_AUDIO_FOLDER,
            self.campana_dialer.queue_campana.audio_para_contestadores.
                get_filename_audio_asterisk())
        self.assertEqual(dict_campana['AMDPLAY'], audio)
        self.assertEqual(dict_campana['TC'], "")
        self.assertEqual(dict_campana['IDJSON'], "")
        self.assertEqual(dict_campana['PERMITOCCULT'], "")
        self.assertEqual(dict_campana['MAXCALLS'], "")
        self.assertEqual(dict_campana['FAILOVER'], str(0))

    def test_values_de_configuraciones_de_agentes_no_seteadas_dialer(self):
        ConfiguracionDeAgentesDeCampanaFactory(
            campana=self.campana_dialer,
            set_auto_attend_inbound=False,
            set_auto_attend_dialer=False,
            set_auto_unpause=False,
            set_obligar_calificacion=False)
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_dialer)
        self.assertNotIn('AUTO_ATTEND_INBOUND', dict_campana)
        self.assertNotIn('AUTO_ATTEND_DIALER', dict_campana)
        self.assertNotIn('FORCE_DISPOSITION', dict_campana)
        self.assertNotIn('AUTO_UNPAUSE', dict_campana)

    def test_values_de_configuraciones_de_agentes_seteadas_dialer(self):
        ConfiguracionDeAgentesDeCampanaFactory(
            campana=self.campana_dialer,
            set_auto_attend_inbound=True,
            auto_attend_inbound=True,
            set_auto_attend_dialer=True,
            auto_attend_dialer=True,
            set_auto_unpause=True,
            auto_unpause=10,
            set_obligar_calificacion=True,
            obligar_calificacion=False,)
        servicio = CampanaFamily()
        dict_campana = servicio._create_dict(self.campana_dialer)
        self.assertNotIn('AUTO_ATTEND_INBOUND', dict_campana)
        self.assertIn('AUTO_ATTEND_DIALER', dict_campana)
        self.assertEqual(dict_campana['AUTO_ATTEND_DIALER'], 'True')
        self.assertIn('FORCE_DISPOSITION', dict_campana)
        self.assertEqual(dict_campana['FORCE_DISPOSITION'], 'False')
        self.assertIn('AUTO_UNPAUSE', dict_campana)
        self.assertEqual(dict_campana['AUTO_UNPAUSE'], 10)

    def test_devuelve_correctamente_dict_agente_asterisk(self):
        """
        este test testea el diccionario de la family del agente
        """
        servicio = AgenteFamily()
        dict_agente = servicio._create_dict(self.agente)

        self.assertEqual(['NAME', 'SIP', 'STATUS', 'TIMESTAMP'], list(dict_agente.keys()))

    def test_falla_dict_agente_asterisk(self):
        """
        este test testea el diccionario de la family del agente
        """
        servicio = AgenteFamily()
        dict_agente = servicio._create_dict(self.agente)

        self.assertNotIn('PASS', dict_agente.keys())

    def test_devuelve_correctamente_values_agente_asterisk(self):
        """
        este test testea los values del diccionario de la family del agente
        """
        servicio = AgenteFamily()
        dict_agente = servicio._create_dict(self.agente)

        self.assertEqual(dict_agente['NAME'], self.agente.user.get_full_name())
        self.assertEqual(dict_agente['SIP'], self.agente.sip_extension)
        self.assertEqual(dict_agente['STATUS'], "")

    def test_devuelve_correctamente_values_ruta(self):
        """
        este test los values del diccionario para la family de la ruta
        """
        ruta = RutaSalienteFactory()
        patron_1_1 = PatronDeDiscadoFactory(ruta_saliente=ruta)
        patron_1_2 = PatronDeDiscadoFactory(ruta_saliente=ruta, prefix='123', prepend='123')

        servicio = RutaSalienteFamily()

        # verifico que genere correctamente el dict de la ruta
        dict_ruta = servicio._create_dict(ruta)

        self.assertEqual(dict_ruta['NAME'], ruta.nombre)
        self.assertEqual(dict_ruta['RINGTIME'], ruta.ring_time)
        self.assertEqual(dict_ruta['OPTIONS'], ruta.dial_options)
        self.assertEqual(dict_ruta['TRUNKS'], len(ruta.secuencia_troncales.all()))

        # verifico que genere correctamente el dict de los patrones de desicado
        if patron_1_1.prefix:
            prefix = len(str(patron_1_1.prefix))
        else:
            prefix = ''
        prepend = patron_1_1.prepend if patron_1_1.prepend is not None else ''
        self.assertEqual(dict_ruta['PREFIX-1'], prefix)
        self.assertEqual(dict_ruta['PREPEND-1'], prepend)
        if patron_1_2.prefix:
            prefix = len(str(patron_1_2.prefix))
        else:
            prefix = ''
        prepend = patron_1_2.prepend if patron_1_2.prepend is not None else ''
        self.assertEqual(dict_ruta['PREFIX-2'], prefix)
        self.assertEqual(dict_ruta['PREPEND-2'], prepend)

    def test_devuelve_correctamente_values_troncales(self):
        """
        este test los values del diccionario para la family de los troncales
        """
        troncal_1 = TroncalSIPFactory()
        troncal_2 = TroncalSIPFactory()

        servicio = TrunkFamily()

        # verifico que genere correctamente el dict de los troncales
        dict_troncal = servicio._create_dict(troncal_1)
        self.assertEqual(dict_troncal['NAME'], troncal_1.nombre)
        self.assertEqual(dict_troncal['CHANNELS'], troncal_1.canales_maximos)
        self.assertEqual(dict_troncal['CALLERID'], troncal_1.caller_id)

        dict_troncal = servicio._create_dict(troncal_2)
        self.assertEqual(dict_troncal['NAME'], troncal_2.nombre)
        self.assertEqual(dict_troncal['CHANNELS'], troncal_2.canales_maximos)
        self.assertEqual(dict_troncal['CALLERID'], troncal_2.caller_id)
