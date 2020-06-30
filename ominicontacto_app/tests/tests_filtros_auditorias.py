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
Tests relacionados con las auditorías
"""

from django.urls import reverse
from django.utils.timezone import now, timedelta

from ominicontacto_app.models import User, Campana, OpcionCalificacion, AuditoriaCalificacion
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.tests.factories import (
    CampanaFactory, CalificacionClienteFactory, AuditoriaCalificacionFactory,
    OpcionCalificacionFactory, QueueFactory, QueueMemberFactory)


class AuditoriasCalificacionesTests(OMLBaseTest):

    def setUp(self):
        super(AuditoriasCalificacionesTests, self).setUp()

        self.campana1 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)
        self.campana2 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)
        self.campana3 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)

        self.supervisor1 = self.crear_supervisor_profile(rol=User.GERENTE)
        self.supervisor2 = self.crear_supervisor_profile(rol=User.GERENTE)
        self.supervisor3 = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.supervisor4 = self.crear_supervisor_profile(rol=User.REFERENTE)

        # calificaciones y auditorias de gestion para campana1
        opcion_calificacion11 = OpcionCalificacionFactory(
            campana=self.campana1, tipo=OpcionCalificacion.GESTION)
        self.calificacion11 = CalificacionClienteFactory(opcion_calificacion=opcion_calificacion11)

        # calificacion de gestion para campana2
        opcion_calificacion21_gestion = OpcionCalificacionFactory(
            campana=self.campana2, tipo=OpcionCalificacion.GESTION)
        opcion_calificacion21_no_accion = OpcionCalificacionFactory(
            campana=self.campana2, tipo=OpcionCalificacion.NO_ACCION)
        self.calificacion21 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion21_no_accion)
        self.calificacion22 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion21_gestion)
        self.calificacion23 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion21_gestion)
        self.calificacion24 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion21_gestion)
        self.calificacion25 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion21_gestion)
        self.queue_campana_2 = QueueFactory(campana=self.campana2)
        QueueMemberFactory(member=self.calificacion25.agente, queue_name=self.queue_campana_2)

        self.auditoria_aprobada = AuditoriaCalificacionFactory(
            calificacion=self.calificacion23, resultado=AuditoriaCalificacion.APROBADA)
        self.auditoria_rechazada = AuditoriaCalificacionFactory(
            calificacion=self.calificacion24, resultado=AuditoriaCalificacion.RECHAZADA)
        self.auditoria_rechazada = AuditoriaCalificacionFactory(
            calificacion=self.calificacion25, resultado=AuditoriaCalificacion.OBSERVADA)

        self.campana2.supervisors.add(self.supervisor2.user)
        self.campana3.supervisors.add(self.supervisor2.user)

        # calificacion de gestion para campana2
        opcion_calificacion31_gestion = OpcionCalificacionFactory(
            campana=self.campana3, tipo=OpcionCalificacion.GESTION)
        self.calificacion31 = CalificacionClienteFactory(
            opcion_calificacion=opcion_calificacion31_gestion)

        self.client.login(username=self.supervisor2.user, password=self.DEFAULT_PASSWORD)

    def test_supervisor_simple_no_tiene_accesso_vista_gestion(self):
        self.client.logout()
        self.client.login(username=self.supervisor3.user, password=self.DEFAULT_PASSWORD)
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '', 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_supervisor_referente_no_tiene_accesso_vista_gestion(self):
        self.client.logout()
        self.client.login(username=self.supervisor4.user, password=self.DEFAULT_PASSWORD)
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '', 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_solo_muestra_las_calificaciones_gestion_campanas_asignadas_al_supervisor(self):
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '', 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertFalse(calificaciones.filter(opcion_calificacion__campana=self.campana1).exists())

    def test_inicialmente_se_muestran_calificaciones_auditadas_o_gestion(self):
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '', 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 5)
        self.assertFalse(calificaciones.filter(
            opcion_calificacion__tipo=OpcionCalificacion.NO_ACCION,
            auditoriacalificacion__isnull=True).exists())

    def test_filtro_telefono_se_muestra_correctamente(self):
        telefono = self.calificacion22.contacto.telefono
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': telefono, 'callid': '', 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(
            list(calificaciones.values_list('contacto__telefono', flat=True)), [telefono])

    def test_filtro_callid_se_muestra_correctamente(self):
        callid = self.calificacion23.callid
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': callid, 'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(
            list(calificaciones.values_list('callid', flat=True)), [callid])

    def test_filtro_tipo_auditoria_se_muestra_correctamente(self):
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '',
                     'status_auditoria': AuditoriaCalificacion.APROBADA}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().auditoriacalificacion.resultado,
                         AuditoriaCalificacion.APROBADA)

    def test_filtro_id_contacto_se_muestra_correctamente(self):
        id_contacto = self.calificacion24.contacto.pk
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': id_contacto, 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().contacto.pk, id_contacto)

    def test_filtro_id_externo_se_muestra_correctamente(self):
        id_contacto_externo = "an-external-id23"
        contacto = self.calificacion24.contacto
        contacto.id_externo = id_contacto_externo
        contacto.save()

        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto_externo': id_contacto_externo, 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().contacto.pk, contacto.pk)

    def test_filtro_campana_se_muestra_correctamente(self):
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': self.campana3.pk, 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().opcion_calificacion.campana, self.campana3)

    def test_filtro_agente_se_muestra_correctamente(self):
        agente = self.calificacion25.agente
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': agente.pk, 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().agente, agente)

    def test_filtro_fecha_se_muestra_correctamente(self):
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': '',
                     'id_contacto': '', 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        tomorrow = now() + timedelta(days=1)
        rango_tomorrow = tomorrow.date().strftime('%d/%m/%Y') + ' - ' + tomorrow.date().strftime(
            '%d/%m/%Y')
        post_data['fecha'] = rango_tomorrow
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        # no deberíamos tener calificaciones ya que el filtro es para mañana
        # y las calificaciones fueron creadas hoy
        self.assertFalse(calificaciones.exists())

    def test_filtro_grupo_agentes_se_muestra_correctamente(self):
        grupo_id = self.calificacion25.agente.grupo.pk
        url = reverse('buscar_auditorias_gestion', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'agente': '', 'campana': '', 'grupo_agente': grupo_id,
                     'id_contacto': '', 'telefono': '', 'callid': '',
                     'status_auditoria': ''}
        response = self.client.post(url, post_data, follow=True)
        calificaciones = response.context_data['listado_de_calificaciones']
        # no deberíamos tener calificaciones ya que el filtro es para mañana
        # y las calificaciones fueron creadas hoy
        self.assertEqual(calificaciones.count(), 1)
        self.assertEqual(calificaciones.first().pk, self.calificacion25.pk)
