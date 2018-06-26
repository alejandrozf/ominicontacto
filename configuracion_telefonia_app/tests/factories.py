# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import faker

from factory import DjangoModelFactory, lazy_attribute, SubFactory, Sequence

from configuracion_telefonia_app.models import (
    TroncalSIP, RutaSaliente, PatronDeDiscado, OrdenTroncal
)

faker = faker.Factory.create()


class TroncalSIPFactory(DjangoModelFactory):
    class Meta:
        model = TroncalSIP

    nombre = Sequence(lambda n: "TroncalSIP{0}".format(n))
    canales_maximos = lazy_attribute(lambda a: faker.random_int(1, 10))
    caller_id = Sequence(lambda n: "CallID{0}".format(n))
    register_string = Sequence(lambda n: "Register{0}@localhost:11443".format(n))
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
