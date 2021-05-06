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
from __future__ import unicode_literals

import faker

from factory import DjangoModelFactory, lazy_attribute, SubFactory, Sequence

from django.utils import timezone

from configuracion_telefonia_app.models import (
    TroncalSIP, RutaSaliente, PatronDeDiscado, OrdenTroncal, RutaEntrante, IVR, ValidacionFechaHora,
    DestinoEntrante, OpcionDestino, ValidacionTiempo, GrupoHorario, IdentificadorCliente,
    DestinoPersonalizado, Playlist
)
from ominicontacto_app.tests.factories import ArchivoDeAudioFactory

faker = faker.Factory.create()


class TroncalSIPFactory(DjangoModelFactory):
    class Meta:
        model = TroncalSIP

    nombre = Sequence(lambda n: "TroncalSIP{0}".format(n))
    canales_maximos = lazy_attribute(lambda a: faker.random_int(1, 10))
    caller_id = Sequence(lambda n: "CallID{0}".format(n))
    tecnologia = lazy_attribute(lambda a: faker.random_int(0, 1))
    text_config = ""


class RutaSalienteFactory(DjangoModelFactory):
    class Meta:
        model = RutaSaliente

    nombre = Sequence(lambda n: "RutaSaliente{0}".format(n))
    ring_time = lazy_attribute(lambda a: faker.random_int(0, 120))
    dial_options = ""


class PatronDeDiscadoFactory(DjangoModelFactory):
    class Meta:
        model = PatronDeDiscado

    ruta_saliente = SubFactory(RutaSalienteFactory)
    prepend = None
    prefix = None
    match_pattern = ""
    orden = Sequence(lambda n: n)


class OrdenTroncalFactory(DjangoModelFactory):
    class Meta:
        model = OrdenTroncal

    ruta_saliente = SubFactory(RutaSalienteFactory)
    orden = Sequence(lambda n: n)
    troncal = SubFactory(TroncalSIPFactory)


class IVRFactory(DjangoModelFactory):

    class Meta:
        model = IVR

    nombre = Sequence(lambda n: "IVR {0}".format(n))
    descripcion = Sequence(lambda n: "Descripcion {0}".format(n))
    audio_principal = SubFactory(ArchivoDeAudioFactory)
    time_out = 20
    time_out_retries = 3
    time_out_audio = SubFactory(ArchivoDeAudioFactory)
    invalid_retries = 4
    invalid_audio = SubFactory(ArchivoDeAudioFactory)


class GrupoHorarioFactory(DjangoModelFactory):

    class Meta:
        model = GrupoHorario

    nombre = Sequence(lambda n: "GrupoHorario {0}".format(n))


class ValidacionTiempoFactory(DjangoModelFactory):

    class Meta:
        model = ValidacionTiempo

    grupo_horario = SubFactory(GrupoHorarioFactory)
    tiempo_inicial = lazy_attribute(lambda a: timezone.now())
    tiempo_final = lazy_attribute(lambda a: timezone.now() + timezone.timedelta(hours=8))
    dia_semana_inicial = 0
    dia_semana_final = 4
    dia_mes_inicio = 1
    dia_mes_final = 24
    mes_inicio = 1
    mes_final = 12


class ValidacionFechaHoraFactory(DjangoModelFactory):

    class Meta:
        model = ValidacionFechaHora

    nombre = Sequence(lambda n: "ValidacionFechaHora {0}".format(n))
    grupo_horario = SubFactory(GrupoHorarioFactory)


class DestinoEntranteFactory(DjangoModelFactory):

    class Meta:
        model = DestinoEntrante

    nombre = Sequence(lambda n: "DestinoEntrante {0}".format(n))
    tipo = 0                    # Ruta entrante
    # 'content_type'y 'object_id' asignarlos en el momento de invocar al factory
    # (en realidad con pasar el content_object sería suficiente)


class OpcionDestinoFactory(DjangoModelFactory):

    class Meta:
        model = OpcionDestino

    valor = Sequence(lambda n: "OpcionDestino {0}".format(n))
    destino_anterior = SubFactory(DestinoEntrante)
    destino_siguiente = SubFactory(DestinoEntrante)


class RutaEntranteFactory(DjangoModelFactory):
    class Meta:
        model = RutaEntrante

    nombre = Sequence(lambda n: "Ruta entrante {0}".format(n))
    telefono = lazy_attribute(lambda a: faker.phone_number())
    prefijo_caller_id = Sequence(lambda n: "Prefijo caller id {0}".format(n))
    idioma = 1
    destino = SubFactory(DestinoEntranteFactory)


class IdentificadorClienteFactory(DjangoModelFactory):
    class Meta:
        model = IdentificadorCliente

    nombre = Sequence(lambda n: "Identificador cliente {0}".format(n))
    url = Sequence(lambda n: "https://url{0}.net".format(n))
    tipo_interaccion = lazy_attribute(lambda a: faker.random_int(1, 3))
    audio = SubFactory(ArchivoDeAudioFactory)
    longitud_id_esperado = lazy_attribute(lambda a: faker.random_int(3, 10))
    timeout = lazy_attribute(lambda a: faker.random_int(3, 7))
    intentos = lazy_attribute(lambda a: faker.random_int(2, 9))


class DestinoPersonalizadoFactory(DjangoModelFactory):

    class Meta:
        model = DestinoPersonalizado

    nombre = Sequence(lambda n: "Destino Personalizado {0}".format(n))
    custom_destination = Sequence(lambda n: "Localización destino {0}".format(n))


class PlaylistFactory(DjangoModelFactory):
    class Meta:
        model = Playlist

    nombre = Sequence(lambda n: "Playlist_{0}".format(n))
