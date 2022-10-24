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
Limitar cantidad de Agendas Personales a Grupos
"""
from django.conf import settings
from django.forms import ValidationError
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import GrupoFactory
from ominicontacto_app.tests.factories import (CampanaFactory,
                                               ContactoFactory,
                                               CalificacionClienteFactory,
                                               OpcionCalificacionFactory,
                                               AgendaContactoFactory)
from ominicontacto_app.models import (AgendaContacto, NombreCalificacion, Campana,
                                      OpcionCalificacion)


class LimitarAgendasPersonalesTests(OMLBaseTest):

    def setUp(self):
        super(LimitarAgendasPersonalesTests, self).setUp()

        self.grupo1 = GrupoFactory(nombre='grupo1', limitar_agendas_personales=True,
                                   cantidad_agendas_personales=1)
        self.grupo2 = GrupoFactory(nombre='grupo2', limitar_agendas_personales=True,
                                   cantidad_agendas_personales=0)
        self.grupo3 = GrupoFactory(nombre='grupo3', limitar_agendas_personales=False,
                                   cantidad_agendas_personales=0)

        self.agente_1 = self.crear_agente_profile()
        self.agente_1.grupo = self.grupo1
        self.agente_1.save()

        self.agente_2 = self.crear_agente_profile()
        self.agente_2.grupo = self.grupo2
        self.agente_2.save()

        self.agente_3 = self.crear_agente_profile()
        self.agente_3.grupo = self.grupo3
        self.agente_3.save()

        self.contacto = ContactoFactory.create()

        self.campana_preview = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                     type=Campana.TYPE_PREVIEW)
        self.campana_dialer = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                    type=Campana.TYPE_DIALER)

        self.nombre_calificacion_agenda = NombreCalificacion.objects.get(
            nombre=settings.CALIFICACION_REAGENDA)

        self.opcion_calificacion_agenda_campana_preview = OpcionCalificacionFactory.create(
            campana=self.campana_preview, nombre=self.nombre_calificacion_agenda.nombre,
            tipo=OpcionCalificacion.AGENDA)
        self.opcion_calificacion_agenda_campana_dialer = OpcionCalificacionFactory.create(
            campana=self.campana_dialer, nombre=self.nombre_calificacion_agenda.nombre,
            tipo=OpcionCalificacion.AGENDA)

    def _assertNotRaises(self, exception, *args, **kwargs):
        try:
            callable_obj, *args = args
            try:
                self.obj_name = callable_obj.__name__
            except AttributeError:
                self.obj_name = str(callable_obj)
            with self:
                callable_obj(*args, **kwargs)
        except Exception as e:
            if isinstance(e, exception):
                raise AssertionError('{}.{} raises {}.'.format(self.obj_name, *args, exception))

    def test_limitar_agendas_grupos(self):
        self.assertTrue(self.agente_1.permite_agenda_personal(self.contacto, self.campana_preview))
        self.assertFalse(self.agente_2.permite_agenda_personal(self.contacto, self.campana_preview))
        self.assertTrue(self.agente_3.permite_agenda_personal(self.contacto, self.campana_preview))

    def test_calificacion_cliente(self):
        def crear_calificacion(opcion_calificacion, agente):
            CalificacionClienteFactory(opcion_calificacion=opcion_calificacion, agente=agente)

        opcion_calificacion = self.opcion_calificacion_agenda_campana_preview
        self.assertRaises(ValidationError, crear_calificacion, opcion_calificacion, self.agente_2)
        self._assertNotRaises(ValidationError, crear_calificacion, opcion_calificacion,
                              self.agente_1)
        opcion_calificacion = self.opcion_calificacion_agenda_campana_dialer
        self._assertNotRaises(ValidationError, crear_calificacion, opcion_calificacion,
                              self.agente_2)

    def test_crear_agenda_agente(self):

        def crear_agenda(tipo_agenda, campana, agente):
            AgendaContactoFactory(tipo_agenda=tipo_agenda, campana=campana, agente=agente)

        tipo_agenda = AgendaContacto.TYPE_PERSONAL
        campana = self.campana_dialer
        self.assertRaises(ValidationError, crear_agenda, tipo_agenda, campana, self.agente_2)

        tipo_agenda = AgendaContacto.TYPE_GLOBAL
        campana = self.campana_dialer
        self._assertNotRaises(ValidationError, crear_agenda, tipo_agenda, campana, self.agente_2)

        tipo_agenda = AgendaContacto.TYPE_PERSONAL
        campana = self.campana_preview
        self.assertRaises(ValidationError, crear_agenda, tipo_agenda, campana, self.agente_2)

        tipo_agenda = AgendaContacto.TYPE_PERSONAL
        campana = self.campana_preview
        self._assertNotRaises(ValidationError, crear_agenda, tipo_agenda, campana, self.agente_1)
