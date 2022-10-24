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
Tests para Families en 'ominicontacto_app.services.asterisk.redis_database'
"""

from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.services.asterisk.redis_database import (
    IVRFamily, ValidacionFechaHoraFamily, GrupoHorarioFamily, IdentificadorClienteFamily,
    PausaFamily, RutaEntranteFamily, TrunkFamily, DestinoPersonalizadoFamily, CampanaFamily
)

from configuracion_telefonia_app.models import DestinoEntrante, OpcionDestino, IVR, Campana
from configuracion_telefonia_app.tests.factories import (
    IVRFactory, ArchivoDeAudioFactory, ValidacionFechaHoraFactory, GrupoHorarioFactory,
    IdentificadorClienteFactory, ValidacionTiempoFactory, RutaEntranteFactory, TroncalSIPFactory,
    DestinoPersonalizadoFactory)
from ominicontacto_app.tests.factories import (PausaFactory, CampanaFactory, QueueFactory)


class RedisDatabaseTest(OMLBaseTest):
    def setUp(self):
        super(RedisDatabaseTest, self).setUp()
        audio_1 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_1')
        audio_2 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_2')
        audio_3 = ArchivoDeAudioFactory(audio_asterisk='oml/audio_3')
        self.ivr = IVRFactory(
            nombre='IVR 1', time_out=10, time_out_retries=5, invalid_retries=1,
            audio_principal=audio_1, time_out_audio=audio_2, invalid_audio=audio_3)
        self.nodo_ivr = DestinoEntrante.crear_nodo_ruta_entrante(self.ivr)

        self.grupo_horario = GrupoHorarioFactory()
        self.validacion_tiempo = ValidacionTiempoFactory(grupo_horario=self.grupo_horario)
        self.tc = ValidacionFechaHoraFactory()
        self.nodo_tc = DestinoEntrante.crear_nodo_ruta_entrante(self.tc)

        self.id_cliente = IdentificadorClienteFactory(audio=audio_1)
        self.nodo_id_cliente = DestinoEntrante.crear_nodo_ruta_entrante(self.id_cliente)
        self.pausa = PausaFactory()
        self.inr = RutaEntranteFactory(destino=self.nodo_ivr)
        self.trunk = TroncalSIPFactory()
        self.destino_personalizado = DestinoPersonalizadoFactory()
        self.nodo_destino_personalizado = DestinoEntrante.crear_nodo_ruta_entrante(
            self.destino_personalizado)
        self.campana_entrante = CampanaFactory(type=Campana.TYPE_ENTRANTE)
        QueueFactory(campana=self.campana_entrante)
        self.campana_dialer = CampanaFactory(type=Campana.TYPE_DIALER)
        QueueFactory(campana=self.campana_dialer)
        self.campana_preview = CampanaFactory(type=Campana.TYPE_PREVIEW)
        QueueFactory(campana=self.campana_preview)
        self.campana_manual = CampanaFactory(type=Campana.TYPE_MANUAL)
        QueueFactory(campana=self.campana_manual)


class IVRFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):
        dict = {
            'NAME': 'IVR 1',
            'AUDIO': 'oml/audio_1',
            'TIMEOUT': 10,
            'TORETRY': 5,
            'TOAUDIO': 'oml/audio_2',
            'INVRETRY': 1,
            'INVAUDIO': 'oml/audio_3',
            'OPTIONS': 2,
            'DEFAULTTODST': '5,1',
            'DEFAULTINVDST': '5,1',
            'OPTIONDST-1': '5,1',
            'OPTIONDTMF-1': '1',
            'OPTIONDST-2': '5,1',
            'OPTIONDTMF-2': '2',
        }
        dest_hangup = DestinoEntrante.objects.get(tipo=DestinoEntrante.HANGUP)
        ArchivoDeAudioFactory(audio_asterisk='oml/audio_1')
        ArchivoDeAudioFactory(audio_asterisk='oml/audio_2')
        ArchivoDeAudioFactory(audio_asterisk='oml/audio_3')

        OpcionDestino.crear_opcion_destino(self.nodo_ivr, dest_hangup, IVR.VALOR_TIME_OUT)
        OpcionDestino.crear_opcion_destino(self.nodo_ivr, dest_hangup, IVR.VALOR_DESTINO_INVALIDO)
        OpcionDestino.crear_opcion_destino(self.nodo_ivr, dest_hangup, '1')
        OpcionDestino.crear_opcion_destino(self.nodo_ivr, dest_hangup, '2')

        family = IVRFamily()
        self.assertEqual(dict, family._create_dict(self.ivr))


class GrupoHorarioFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'NAME': self.grupo_horario.nombre,
            'ENTRIES': 1,
            'ENTRYHOURF-1': self.validacion_tiempo.tiempo_inicial.strftime('%H:%M'),
            'ENTRYHOURT-1': self.validacion_tiempo.tiempo_final.strftime('%H:%M'),
            'ENTRYDAYF-1': self.validacion_tiempo.dia_semana_inicial_str,
            'ENTRYDAYT-1': self.validacion_tiempo.dia_semana_final_str,
            'ENTRYDAYNUMF-1': self.validacion_tiempo.dia_mes_inicio_str,
            'ENTRYDAYNUMT-1': self.validacion_tiempo.dia_mes_final_str,
            'ENTRYMONTHF-1': self.validacion_tiempo.mes_inicio_str,
            'ENTRYMONTHT-1': self.validacion_tiempo.mes_final_str,
        }
        family = GrupoHorarioFamily()
        self.assertEqual(dict, family._create_dict(self.grupo_horario))


class ValidacionFechaHoraFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'NAME': self.tc.nombre,
            'TGID': self.tc.grupo_horario.id,
        }
        family = ValidacionFechaHoraFamily()
        self.assertEqual(dict, family._create_dict(self.tc))


class IdentificadorClienteFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'NAME': self.id_cliente.nombre,
            'TYPE': self.id_cliente.tipo_interaccion,
            'EXTERNALURL': self.id_cliente.url,
            'AUDIO': 'oml/audio_1',
            'LENGTH': self.id_cliente.longitud_id_esperado,
            'TIMEOUT': self.id_cliente.timeout,
            'RETRIES': self.id_cliente.intentos,
        }
        family = IdentificadorClienteFamily()
        self.assertEqual(dict, family._create_dict(self.id_cliente))


class PausaFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'NAME': self.pausa.nombre,
        }
        family = PausaFamily()
        self.assertEqual(dict, family._create_dict(self.pausa))


class RutaEntranteFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'NAME': self.inr.nombre,
            "DST": "{0},{1}".format(self.nodo_ivr.tipo, self.nodo_ivr.object_id),
            "ID": self.inr.id,
            "LANG": self.inr.sigla_idioma,
        }
        family = RutaEntranteFamily()
        self.assertEqual(dict, family._create_dict(self.inr))
        self.assertEqual('OML:INR:' + self.inr.telefono, family._get_nombre_family(self.inr))


class TrunkFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        dict = {
            'TECH': self.trunk.tecnologia_astdb,
            'NAME': self.trunk.nombre,
            'CHANNELS': self.trunk.canales_maximos,
            'CALLERID': self.trunk.caller_id,
        }
        family = TrunkFamily()
        self.assertEqual(dict, family._create_dict(self.trunk))


class DestinoPersonalizadoFamilyTest(RedisDatabaseTest):
    def test_devuelve_diccionario_con_datos_correctos(self):

        OpcionDestino.crear_opcion_destino(
            self.nodo_destino_personalizado, self.nodo_ivr, 'failover')
        dict = {
            'NAME': self.destino_personalizado.nombre,
            'DST': self.destino_personalizado.custom_destination,
            'FAILOVER': "{0},{1}".format(self.nodo_ivr.tipo, self.nodo_ivr.object_id)
        }
        family = DestinoPersonalizadoFamily()
        self.assertEqual(dict, family._create_dict(self.destino_personalizado))


class CampanaFamilyTest(RedisDatabaseTest):

    def test_devuelve_diccionario_con_datos_correctos_entrante(self):
        dict = {
            'QNAME': self.campana_entrante.get_queue_id_name(),
            'TYPE': self.campana_entrante.type,
            'REC': str(self.campana_entrante.queue_campana.auto_grabacion),
            'AMD': str(self.campana_entrante.queue_campana.detectar_contestadores),
            'CALLAGENTACTION': self.campana_entrante.tipo_interaccion,
            'RINGTIME': "",
            'QUEUETIME': self.campana_entrante.queue_campana.wait,
            'MAXQCALLS': self.campana_entrante.queue_campana.maxlen,
            'SL': self.campana_entrante.queue_campana.servicelevel,
            'OUTR': "",
            'OUTCID': "",
            'IDEXTERNALURL': "",
            'FAILOVER': "0",
            'TC': "",  # a partir de esta variable no se usan las siguientes variables:
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
            'VIDEOCALL': 'False',
            'SHOWCAMPNAME': self.campana_entrante.nombre,
            'SHOWDID': 'False',
            'SHOWINROUTENAME': 'False',
        }
        family = CampanaFamily()

        self.assertEqual(dict, family._create_dict(self.campana_entrante))

    def test_devuelve_diccionario_con_datos_correctos_dialer(self):
        dict = {
            'QNAME': self.campana_dialer.get_queue_id_name(),
            'TYPE': self.campana_dialer.type,
            'REC': str(self.campana_dialer.queue_campana.auto_grabacion),
            'AMD': str(self.campana_dialer.queue_campana.detectar_contestadores),
            'CALLAGENTACTION': self.campana_dialer.tipo_interaccion,
            'RINGTIME': "",
            'QUEUETIME': self.campana_dialer.queue_campana.wait,
            'MAXQCALLS': self.campana_dialer.queue_campana.maxlen,
            'SL': self.campana_dialer.queue_campana.servicelevel,
            'OUTR': "",
            'OUTCID': "",
            'IDEXTERNALURL': "",
            'FAILOVER': "0",
            'TC': "",  # a partir de esta variable no se usan las siguientes variables:
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
            'VIDEOCALL': 'False',
            'SHOWCAMPNAME': self.campana_dialer.nombre,
            'SHOWDID': 'False',
            'SHOWINROUTENAME': 'False',
        }
        family = CampanaFamily()

        self.assertEqual(dict, family._create_dict(self.campana_dialer))

    def test_devuelve_diccionario_con_datos_correctos_manual(self):
        dict = {
            'QNAME': self.campana_manual.get_queue_id_name(),
            'TYPE': self.campana_manual.type,
            'REC': str(self.campana_manual.queue_campana.auto_grabacion),
            'AMD': str(self.campana_manual.queue_campana.detectar_contestadores),
            'CALLAGENTACTION': self.campana_manual.tipo_interaccion,
            'RINGTIME': "",
            'QUEUETIME': self.campana_manual.queue_campana.wait,
            'MAXQCALLS': self.campana_manual.queue_campana.maxlen,
            'SL': self.campana_manual.queue_campana.servicelevel,
            'OUTR': "",
            'OUTCID': "",
            'IDEXTERNALURL': "",
            'FAILOVER': "0",
            'TC': "",  # a partir de esta variable no se usan las siguientes variables:
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
            'VIDEOCALL': 'False',
            'SHOWCAMPNAME': self.campana_manual.nombre,
            'SHOWDID': 'False',
            'SHOWINROUTENAME': 'False',
        }
        family = CampanaFamily()

        self.assertEqual(dict, family._create_dict(self.campana_manual))

    def test_devuelve_diccionario_con_datos_correctos_preview(self):
        dict = {
            'QNAME': self.campana_preview.get_queue_id_name(),
            'TYPE': self.campana_preview.type,
            'REC': str(self.campana_preview.queue_campana.auto_grabacion),
            'AMD': str(self.campana_preview.queue_campana.detectar_contestadores),
            'CALLAGENTACTION': self.campana_preview.tipo_interaccion,
            'RINGTIME': "",
            'QUEUETIME': self.campana_preview.queue_campana.wait,
            'MAXQCALLS': self.campana_preview.queue_campana.maxlen,
            'SL': self.campana_preview.queue_campana.servicelevel,
            'OUTR': "",
            'OUTCID': "",
            'IDEXTERNALURL': "",
            'FAILOVER': "0",
            'TC': "",  # a partir de esta variable no se usan las siguientes variables:
            'IDJSON': "",
            'PERMITOCCULT': "",
            'MAXCALLS': "",
            'VIDEOCALL': 'False',
            'SHOWCAMPNAME': self.campana_preview.nombre,
            'SHOWDID': 'False',
            'SHOWINROUTENAME': 'False',
        }
        family = CampanaFamily()

        self.assertEqual(dict, family._create_dict(self.campana_preview))
