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
from django.utils.translation import ugettext as _
from django.urls import reverse

from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (
    CampanaFactory, NombreCalificacionFactory, ContactoFactory, CalificacionClienteFactory,
    OpcionCalificacionFactory)
from ominicontacto_app.models import Campana, OpcionCalificacion, AuditoriaCalificacion


class AuditoriaDeGestionTests(OMLBaseTest):
    def setUp(self):
        super(AuditoriaDeGestionTests, self).setUp()

        self.supervisor = self.crear_supervisor_profile()
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)

        self.campana = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        self.campana.supervisors.add(self.supervisor.user)

        self.opcion_calificacion_gestion = OpcionCalificacionFactory.create(
            campana=self.campana, tipo=OpcionCalificacion.GESTION)
        self.opcion_calificacion_no_gestion = OpcionCalificacionFactory.create(
            campana=self.campana, tipo=OpcionCalificacion.NO_ACCION)

        self.contacto_gestion = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto_gestion)
        self.contacto_no_gestion = ContactoFactory.create()
        self.campana.bd_contacto.contactos.add(self.contacto_no_gestion)

        self.agente = self.crear_agente_profile()
        self.calificacion_gestion = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_gestion, agente=self.agente,
            contacto=self.contacto_gestion)
        self.calificacion_no_gestion = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion_no_gestion, agente=self.agente,
            contacto=self.contacto_no_gestion)

    def test_no_permite_auditar_calificaciones_no_gestion(self):
        url = reverse('auditar_calificacion_cliente', args=(self.calificacion_no_gestion.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('buscar_auditorias_gestion', args=(1,)))
        self.assertContains(response, _("Sólo pueden auditarse calificaciones de gestión."))

    def test_no_permite_auditar_en_campanas_no_asignadas(self):
        campana_no_asignada = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        nombre_opcion_no_asignada = NombreCalificacionFactory.create()
        opcion_calificacion_no_asignada = OpcionCalificacionFactory.create(
            campana=campana_no_asignada, nombre=nombre_opcion_no_asignada.nombre)
        contacto_no_asignada = ContactoFactory.create()
        campana_no_asignada.bd_contacto.contactos.add(contacto_no_asignada)
        calificacion_no_asignada = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion_no_asignada, agente=self.agente,
            contacto=contacto_no_asignada)

        url = reverse('auditar_calificacion_cliente', args=(calificacion_no_asignada.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('buscar_auditorias_gestion', args=(1,)))
        self.assertContains(response,
                            _("No tiene permiso para auditar calificaciones de esta campaña."))

    def test_permite_auditar_calificaciones_no_gestion_ya_auditadas(self):
        auditoria = AuditoriaCalificacion(
            calificacion=self.calificacion_no_gestion, resultado=AuditoriaCalificacion.OBSERVADA,
            observaciones='Observaciones sobre la auditoría')
        auditoria.save()
        url = reverse('auditar_calificacion_cliente', args=(self.calificacion_no_gestion.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])

        nueva_observacion = 'Nuevas Observaciones'
        response = self.client.post(
            url, {'resultado': AuditoriaCalificacion.APROBADA, 'observaciones': nueva_observacion},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('buscar_auditorias_gestion', args=(1,)))
        self.assertContains(response, _("Auditoría de calificación guardada."))
        auditoria = AuditoriaCalificacion.objects.get(id=auditoria.id)
        self.assertEqual(auditoria.calificacion, self.calificacion_no_gestion)
        self.assertEqual(auditoria.resultado, AuditoriaCalificacion.APROBADA)
        self.assertEqual(auditoria.observaciones, nueva_observacion)

    def test_auditar_calificaciones_no_auditada(self):
        url = reverse('auditar_calificacion_cliente', args=(self.calificacion_gestion.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])

        nueva_observacion = 'Nuevas Observaciones'
        response = self.client.post(
            url, {'resultado': AuditoriaCalificacion.APROBADA, 'observaciones': nueva_observacion},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('buscar_auditorias_gestion', args=(1,)))
        self.assertContains(response, _("Auditoría de calificación guardada."))
        auditoria = AuditoriaCalificacion.objects.get(calificacion=self.calificacion_gestion)
        self.assertEqual(auditoria.resultado, AuditoriaCalificacion.APROBADA)
        self.assertEqual(auditoria.observaciones, nueva_observacion)
