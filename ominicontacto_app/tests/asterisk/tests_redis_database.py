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
#

"""
Tests para Families en 'ominicontacto_app.services.asterisk.redis_database'
"""

from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.services.asterisk.redis_database import (
    IVRFamily, ValidacionFechaHoraFamily, GrupoHorarioFamily, IdentificadorClienteFamily,
)

from configuracion_telefonia_app.models import DestinoEntrante, OpcionDestino, IVR
from configuracion_telefonia_app.tests.factories import (
    IVRFactory, ArchivoDeAudioFactory, ValidacionFechaHoraFactory, GrupoHorarioFactory,
    IdentificadorClienteFactory, ValidacionTiempoFactory)


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
