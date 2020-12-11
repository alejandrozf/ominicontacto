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
Tests relacionados con las grabaciones
"""

from __future__ import unicode_literals

import json

from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now, timedelta

from simple_history.utils import update_change_reason

from ominicontacto_app.models import GrabacionMarca, OpcionCalificacion, Campana, User

from ominicontacto_app.tests.factories import CalificacionClienteFactory, CampanaFactory, \
    ContactoFactory, GrabacionMarcaFactory, LlamadaLogFactory, \
    OpcionCalificacionFactory, QueueFactory, QueueMemberFactory
from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.utiles import fecha_hora_local
from reportes_app.models import LlamadaLog


class BaseGrabacionesTests(OMLBaseTest):

    def setUp(self):
        self.supervisor1 = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.supervisor2 = self.crear_supervisor_profile(rol=User.SUPERVISOR)

        self.agente1 = self.crear_agente_profile()
        self.agente2 = self.crear_agente_profile()

        self.campana1 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)
        self.queue_campana_1 = QueueFactory(campana=self.campana1)
        QueueMemberFactory(member=self.agente1, queue_name=self.queue_campana_1)
        self.campana1.supervisors.add(self.supervisor1.user)

        self.campana2 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)
        self.queue_campana_2 = QueueFactory(campana=self.campana2)
        QueueMemberFactory(member=self.agente2, queue_name=self.queue_campana_2)
        self.campana2.supervisors.add(self.supervisor2.user)

        self.contacto = ContactoFactory(id_externo='id_ext')
        self.campana3 = CampanaFactory(estado=Campana.ESTADO_ACTIVA)
        self.campana3.bd_contacto.genera_contactos([self.contacto])
        self.campana3.supervisors.add(self.supervisor1.user)

        self.opcion_calificacion = OpcionCalificacionFactory(
            campana=self.campana1, tipo=OpcionCalificacion.GESTION)
        self.calificacion = CalificacionClienteFactory(opcion_calificacion=self.opcion_calificacion)
        update_change_reason(self.calificacion, 'calificacion')

        self.llamada_log1 = LlamadaLogFactory.create(duracion_llamada=1, agente_id=self.agente1.id,
                                                     callid=self.calificacion.callid,
                                                     campana_id=self.campana1.id,
                                                     contacto_id='-1')
        self.llamada_log2 = LlamadaLogFactory.create(duracion_llamada=1, agente_id=self.agente1.id,
                                                     campana_id=self.campana1.id)
        self.llamada_log3 = LlamadaLogFactory.create(duracion_llamada=1, agente_id=self.agente1.id,
                                                     campana_id=self.campana1.id)
        self.marca_campana1 = GrabacionMarcaFactory(callid=self.llamada_log1.callid)
        self.marca_campana2 = GrabacionMarcaFactory(callid=self.llamada_log2.callid)

        self.llamada_log2_1 = LlamadaLogFactory.create(duracion_llamada=1,
                                                       agente_id=self.agente2.id,
                                                       campana_id=self.campana2.id)
        self.marca_campana2_1 = GrabacionMarcaFactory(callid=self.llamada_log2_1.callid)

        self.llamada_log3_1 = LlamadaLogFactory.create(numero_marcado=self.contacto.telefono,
                                                       agente_id=self.agente2.id,
                                                       campana_id=self.campana3.id)


class GrabacionesTests(BaseGrabacionesTests):

    def setUp(self):
        super(GrabacionesTests, self).setUp()
        self.client.login(username=self.supervisor1.user, password=self.DEFAULT_PASSWORD)

    def test_vista_creacion_grabaciones_marcadas(self):
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'callid': self.llamada_log3.callid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)

        self.assertTrue(GrabacionMarca.objects.filter(
            callid=self.llamada_log3.callid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_vista_creacion_grabaciones_marcadas(self):
        self.client.logout()
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'callid': self.llamada_log3.callid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)
        self.assertFalse(GrabacionMarca.objects.filter(
            callid=self.llamada_log3.callid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_obtener_descripciones_grabaciones(self):
        self.client.logout()
        url = reverse('grabacion_descripcion', kwargs={'callid': self.llamada_log1.callid})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.template_name, 'registration/login.html')

    def test_respuesta_api_descripciones_grabaciones_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'callid': self.llamada_log2.callid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'Descripción')

    def test_respuesta_api_descripciones_grabaciones_no_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'callid': self.llamada_log3.callid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'No encontrada')

    def test_url_de_grabacion_segun_fecha(self):
        hoy = now()
        hace_mucho = hoy - timedelta(days=3)
        self.llamada_log2.time = hace_mucho
        self.llamada_log1.time = hoy
        self.assertTrue(self.llamada_log2.url_archivo_grabacion.endswith(settings.MONITORFORMAT))
        self.assertTrue(self.llamada_log1.url_archivo_grabacion.endswith('.wav'))


class FiltrosBusquedaGrabacionesSupervisorTests(BaseGrabacionesTests):

    def setUp(self):
        super(FiltrosBusquedaGrabacionesSupervisorTests, self).setUp()
        self.client.login(username=self.supervisor1.user, password=self.DEFAULT_PASSWORD)

    def test_filtro_grabaciones_marcadas(self):
        self.assertEqual(LlamadaLog.objects.obtener_grabaciones_marcadas().count(), 3)

    def test_buscar_grabaciones_por_duracion(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '1'}

        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertContains(response, self.llamada_log2.numero_marcado)
        self.assertContains(response, self.llamada_log3.numero_marcado)
        # Aseguro que no traiga la grabacion de una campaña que no tiene asignada.
        self.assertNotContains(response, self.llamada_log2_1.numero_marcado)

        LlamadaLog.objects.filter(id=self.llamada_log2.id).update(
            duracion_llamada=15, numero_marcado='42222222')
        LlamadaLog.objects.filter(id=self.llamada_log1.id).update(
            duracion_llamada=15, numero_marcado='41111111')
        LlamadaLog.objects.filter(id=self.llamada_log3.id).update(
            duracion_llamada=12, numero_marcado='43333333')

        post_data['duracion'] = 12
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertContains(response, '43333333')
        self.assertNotContains(response, self.llamada_log2_1.numero_marcado)

        post_data['duracion'] = 15
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertNotContains(response, '43333333')

        post_data['duracion'] = 16
        response = self.client.post(url, post_data, follow=True)
        self.assertNotContains(response, '41111111')
        self.assertNotContains(response, '42222222')
        self.assertNotContains(response, '43333333')

    def _obtener_fechas(self):
        hoy = fecha_hora_local(now())
        hace_mucho = hoy - timedelta(days=3)
        ahora = fecha_hora_local(now())
        return (hoy, hace_mucho, ahora)

    def test_buscar_grabaciones_por_fecha(self):
        (hoy, hace_mucho, ahora) = self._obtener_fechas()
        if hoy.date() < ahora.date():
            (hoy, hace_mucho, ahora) = self._obtener_fechas()
        LlamadaLog.objects.filter(id=self.llamada_log2.id).update(time=hace_mucho,
                                                                  numero_marcado='42222222')
        LlamadaLog.objects.filter(id=self.llamada_log1.id).update(
            time=hoy, numero_marcado='41111111')
        LlamadaLog.objects.filter(id=self.llamada_log3.id).update(
            time=hoy, numero_marcado='43333333')
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0'}

        rango_hace_mucho = hace_mucho.date().strftime('%d/%m/%Y') + ' - ' + \
            ahora.date().strftime('%d/%m/%Y')
        post_data['fecha'] = rango_hace_mucho
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertContains(response, '43333333')

        rango_hoy = ahora.date().strftime('%d/%m/%Y') + ' - ' + ahora.date().strftime('%d/%m/%Y')
        post_data['fecha'] = rango_hoy
        response = self.client.post(url, post_data, follow=True)
        self.assertNotContains(response, '42222222')
        self.assertContains(response, '41111111')
        self.assertContains(response, '43333333')

    def test_filtro_grabaciones_calificadas_gestion_muestra_gestionadas(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0', 'gestion': True}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertNotContains(response, self.llamada_log2.numero_marcado)
        self.assertNotContains(response, self.llamada_log3.numero_marcado)

    def test_filtro_grabaciones_calificadas_gestion_excluye_no_gestionadas(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0', 'gestion': False}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertContains(response, self.llamada_log2.numero_marcado)
        self.assertContains(response, self.llamada_log3.numero_marcado)

    def test_buscar_grabaciones_por_callid(self):
        LlamadaLog.objects.filter(id=self.llamada_log1.id).update(callid='1')
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '', 'callid': '1'}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertNotContains(response, self.llamada_log2.numero_marcado)
        self.assertNotContains(response, self.llamada_log3.numero_marcado)

    def test_buscar_grabaciones_por_id_contacto_externo(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '', 'id_contacto_externo': 'id_ext'}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log3_1.numero_marcado)
        self.assertNotContains(response, self.llamada_log1.numero_marcado)
        self.assertNotContains(response, self.llamada_log3.numero_marcado)


class FiltrosBusquedaGrabacionesAgenteTests(BaseGrabacionesTests):

    def setUp(self):
        super(FiltrosBusquedaGrabacionesAgenteTests, self).setUp()
        self.client.login(username=self.agente1.user, password=self.DEFAULT_PASSWORD)

    def test_ve_solamente_grabaciones_propias(self):
        url = reverse('grabacion_agente_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0'}
        response = self.client.post(url, post_data, follow=True)

        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertContains(response, self.llamada_log2.numero_marcado)
        self.assertContains(response, self.llamada_log3.numero_marcado)
        self.assertNotContains(response, self.llamada_log2_1.numero_marcado)

    def test_ve_solamente_grabaciones_propias_antes_de_filtrar(self):
        agente3 = self.crear_agente_profile()
        QueueMemberFactory(member=agente3, queue_name=self.queue_campana_1)
        llamada_log3_3 = LlamadaLogFactory.create(
            duracion_llamada=1, agente_id=agente3.id, campana_id=self.campana1.id)

        url = reverse('grabacion_agente_buscar', kwargs={'pagina': 1})
        response = self.client.get(url, follow=True)

        self.assertContains(response, self.llamada_log1.numero_marcado)
        self.assertContains(response, self.llamada_log2.numero_marcado)
        self.assertContains(response, self.llamada_log3.numero_marcado)
        self.assertNotContains(response, llamada_log3_3.numero_marcado)
