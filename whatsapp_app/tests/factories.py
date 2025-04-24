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
from __future__ import unicode_literals
import faker
import string
from factory.django import DjangoModelFactory
from factory import (fuzzy, lazy_attribute, Sequence, SubFactory)

from ominicontacto_app.tests.factories import UserFactory
from ominicontacto_app.tests.factories import CampanaFactory
from configuracion_telefonia_app.models import DestinoEntrante
from whatsapp_app.models import (ConfiguracionProveedor, Linea, PlantillaMensaje,
                                 ConversacionWhatsapp, MensajeWhatsapp, MenuInteractivoWhatsapp, )


faker = faker.Factory.create()


class ConfiguracionProveedorFactory(DjangoModelFactory):
    class Meta:
        model = ConfiguracionProveedor
    nombre = Sequence(lambda n: "proveedor_{0}".format(n))
    tipo_proveedor = lazy_attribute(lambda a: faker.random_number(3))
    created_by = SubFactory(UserFactory)
    updated_by = SubFactory(UserFactory)


class DestinoEntranteFactory(DjangoModelFactory):

    class Meta:
        model = DestinoEntrante

    nombre = Sequence(lambda n: "DestinoEntrante {0}".format(n))
    tipo = 0
    content_object = SubFactory(CampanaFactory)


class LineaFactory(DjangoModelFactory):
    class Meta:
        model = Linea
    nombre = Sequence(lambda n: "linea_{0}".format(n))
    proveedor = SubFactory(ConfiguracionProveedorFactory)
    destino = SubFactory(DestinoEntranteFactory)
    numero = fuzzy.FuzzyText(length=12, chars=string.ascii_uppercase + string.digits)
    created_by = SubFactory(UserFactory)
    updated_by = SubFactory(UserFactory)


class PlantillaAgenteFactory(DjangoModelFactory):
    class Meta:
        model = PlantillaMensaje
    nombre = Sequence(lambda n: "plantilla_{0}".format(n))
    tipo = PlantillaMensaje.TIPO_TEXT
    created_by = SubFactory(UserFactory)
    updated_by = SubFactory(UserFactory)


class MenuInteractivoFactory(DjangoModelFactory):
    class Meta:
        model = MenuInteractivoWhatsapp

    menu_header = lazy_attribute(lambda a: faker.text(15))
    menu_body = lazy_attribute(lambda a: faker.text(15))
    menu_footer = lazy_attribute(lambda a: faker.text(15))
    menu_button = lazy_attribute(lambda a: faker.text(15))
    texto_opcion_incorrecta = lazy_attribute(lambda a: faker.text(15))
    texto_derivacion = lazy_attribute(lambda a: faker.text(15))
    timeout = lazy_attribute(lambda a: faker.random_int(5, 60))


class ConversacionFactory(DjangoModelFactory):
    class Meta:
        model = ConversacionWhatsapp
    line = SubFactory(LineaFactory)


class MensajeFactory(DjangoModelFactory):
    class Meta:
        model = MensajeWhatsapp
    conversation = SubFactory(ConversacionFactory)
