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

from django.urls import reverse
from django.utils.translation import gettext as _

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import CampanaFactory, ContactoFactory
from ominicontacto_app.models import Campana, Contacto, AgenteEnContacto, User


class AgregarContactoACampanaTest(OMLBaseTest):

    def setUp(self):
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)

        self.client.login(username=self.supervisor.user.username, password=PASSWORD)

        self.campana_preview = CampanaFactory(
            type=Campana.TYPE_PREVIEW, estado=Campana.ESTADO_ACTIVA,
            reported_by=self.supervisor.user)
        self.campana_preview.supervisors.add(self.supervisor.user)
        bd_contacto = self.campana_preview.bd_contacto

        self.campana_manual = CampanaFactory(
            type=Campana.TYPE_MANUAL, estado=Campana.ESTADO_ACTIVA, bd_contacto=bd_contacto)
        self.campana_manual.supervisors.add(self.supervisor.user)

        self.campana_preview_sin_permiso = CampanaFactory(
            type=Campana.TYPE_PREVIEW, estado=Campana.ESTADO_ACTIVA, bd_contacto=bd_contacto)

        self.post_data = {
            'telefono': '1234567',
            'nombre': 'NombreContacto',
            'apellido': 'ApellidoContacto',
            'dni': '20.202.020',
        }

    def test_agregar_contacto_campana_preview_agrega_agente_en_contacto(self):
        url = reverse('agregar_contacto_a_campana', kwargs={'pk_campana': self.campana_preview.id})
        contactos_iniciales = Contacto.objects.count()
        response = self.client.post(url, self.post_data, follow=True)
        self.assertContains(response, _('Contacto creado satisfactoriamente.'))
        self.assertEqual(contactos_iniciales + 1, Contacto.objects.count())
        contacto = self.campana_preview.bd_contacto.contactos.last()
        asignacion = AgenteEnContacto.objects.get(
            campana_id=self.campana_preview.id, contacto_id=contacto.id)
        self.assertEqual(asignacion.agente_id, -1)
        self.assertEqual(asignacion.estado, AgenteEnContacto.ESTADO_INICIAL)

    def test_no_puede_agregar_contacto_campana_sin_permiso(self):
        url = reverse('agregar_contacto_a_campana', kwargs={'pk_campana': self.campana_manual.id})
        contactos_iniciales = Contacto.objects.count()
        asignaciones_iniciales = AgenteEnContacto.objects.count()
        response = self.client.post(url, self.post_data, follow=True)
        self.assertContains(response, _('Contacto creado satisfactoriamente.'))
        self.assertEqual(contactos_iniciales + 1, Contacto.objects.count())
        self.assertEqual(asignaciones_iniciales, AgenteEnContacto.objects.count())

    def test_agregar_contacto_campana_no_preview_no_agrega_agente_en_contacto(self):
        url = reverse('agregar_contacto_a_campana',
                      kwargs={'pk_campana': self.campana_preview_sin_permiso.id})
        contactos_iniciales = Contacto.objects.count()
        asignaciones_iniciales = AgenteEnContacto.objects.count()
        response = self.client.post(url, self.post_data, follow=True)
        self.assertEqual(contactos_iniciales, Contacto.objects.count())
        self.assertEqual(asignaciones_iniciales, AgenteEnContacto.objects.count())
        self.assertContains(response, _('No tiene permiso para agregar contactos a la Campaña.'))

    def test_agregar_contacto_campana_incrementa_contactos_en_db(self):
        campana = CampanaFactory()
        bd_contacto = campana.bd_contacto
        cantidad_contactos_origen = bd_contacto.get_cantidad_contactos()
        ContactoFactory.create(bd_contacto=bd_contacto)
        cantidad_contactos_actual = bd_contacto.get_cantidad_contactos_actual()
        self.assertEqual(cantidad_contactos_actual, cantidad_contactos_origen + 1)
