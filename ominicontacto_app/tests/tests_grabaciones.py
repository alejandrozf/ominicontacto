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

from ominicontacto_app.models import Grabacion, GrabacionMarca, OpcionCalificacion, Campana, User

from ominicontacto_app.tests.factories import (GrabacionFactory, GrabacionMarcaFactory,
                                               CalificacionClienteFactory, CampanaFactory,
                                               OpcionCalificacionFactory, QueueFactory,
                                               QueueMemberFactory, ContactoFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest

from ominicontacto_app.utiles import fecha_hora_local


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
        self.grabacion1 = GrabacionFactory.create(
            duracion=1, agente=self.agente1, callid=self.calificacion.callid,
            campana=self.campana1, id_cliente='-1')
        self.grabacion2 = GrabacionFactory(
            duracion=1, agente=self.agente1, campana=self.campana1)
        self.grabacion3 = GrabacionFactory(
            duracion=1, agente=self.agente1, campana=self.campana1)
        self.marca_campana1 = GrabacionMarcaFactory(callid=self.grabacion1.callid)
        self.marca_campana2 = GrabacionMarcaFactory(callid=self.grabacion2.callid)

        self.grabacion2_1 = GrabacionFactory.create(
            duracion=1, agente=self.agente2, campana=self.campana2)
        self.marca_campana2_1 = GrabacionMarcaFactory(callid=self.grabacion2_1.callid)

        self.grabacion3_1 = GrabacionFactory.create(
            tel_cliente=self.contacto.telefono, agente=self.agente2, campana=self.campana3)


class GrabacionesTests(BaseGrabacionesTests):

    def setUp(self):
        super(GrabacionesTests, self).setUp()
        self.client.login(username=self.supervisor1.user, password=self.DEFAULT_PASSWORD)

    def test_vista_creacion_grabaciones_marcadas(self):
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'callid': self.grabacion3.callid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)

        self.assertTrue(GrabacionMarca.objects.filter(
            callid=self.grabacion3.callid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_vista_creacion_grabaciones_marcadas(self):
        self.client.logout()
        url = reverse('grabacion_marcar')
        descripcion = 'descripcion de prueba'
        post_data = {'callid': self.grabacion3.callid,
                     'descripcion': descripcion}
        self.client.post(url, post_data)
        self.assertFalse(GrabacionMarca.objects.filter(
            callid=self.grabacion3.callid, descripcion=descripcion).exists())

    def test_usuarios_no_logueados_no_acceden_a_obtener_descripciones_grabaciones(self):
        self.client.logout()
        url = reverse('grabacion_descripcion', kwargs={'callid': self.grabacion1.callid})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.template_name, 'registration/login.html')

    def test_respuesta_api_descripciones_grabaciones_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'callid': self.grabacion2.callid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'Descripción')

    def test_respuesta_api_descripciones_grabaciones_no_marcadas(self):
        url = reverse('grabacion_descripcion', kwargs={'callid': self.grabacion3.callid})
        response = self.client.get(url, follow=True)
        data_response = json.loads(response.content)
        self.assertEqual(data_response['result'], 'No encontrada')

    def test_url_de_grabacion_segun_fecha(self):
        hoy = now()
        hace_mucho = hoy - timedelta(days=3)
        self.grabacion2.fecha = hace_mucho
        self.grabacion1.fecha = hoy
        self.assertTrue(self.grabacion2.url.endswith(settings.MONITORFORMAT))
        self.assertTrue(self.grabacion1.url.endswith('.wav'))


class FiltrosBusquedaGrabacionesSupervisorTests(BaseGrabacionesTests):

    def setUp(self):
        super(FiltrosBusquedaGrabacionesSupervisorTests, self).setUp()
        self.client.login(username=self.supervisor1.user, password=self.DEFAULT_PASSWORD)

    def test_filtro_grabaciones_marcadas(self):
        self.assertEqual(Grabacion.objects.marcadas().count(), 3)

    def test_buscar_grabaciones_por_duracion(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '1'}

        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertContains(response, self.grabacion2.tel_cliente)
        self.assertContains(response, self.grabacion3.tel_cliente)
        # Aseguro que no traiga la grabacion de una campaña que no tiene asignada.
        self.assertNotContains(response, self.grabacion2_1.tel_cliente)

        Grabacion.objects.filter(id=self.grabacion2.id).update(duracion=15, tel_cliente='42222222')
        Grabacion.objects.filter(id=self.grabacion1.id).update(duracion=15, tel_cliente='41111111')
        Grabacion.objects.filter(id=self.grabacion3.id).update(duracion=12, tel_cliente='43333333')

        post_data['duracion'] = 12
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, '41111111')
        self.assertContains(response, '42222222')
        self.assertContains(response, '43333333')
        self.assertNotContains(response, self.grabacion2_1.tel_cliente)

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
        Grabacion.objects.filter(id=self.grabacion2.id).update(fecha=hace_mucho,
                                                               tel_cliente='42222222')
        Grabacion.objects.filter(id=self.grabacion1.id).update(fecha=hoy, tel_cliente='41111111')
        Grabacion.objects.filter(id=self.grabacion3.id).update(fecha=hoy, tel_cliente='43333333')
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
        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertContains(response, self.opcion_calificacion.nombre)
        self.assertNotContains(response, self.grabacion2.tel_cliente)
        self.assertNotContains(response, self.grabacion3.tel_cliente)

    def test_filtro_grabaciones_calificadas_gestion_excluye_no_gestionadas(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '0', 'gestion': False}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertContains(response, self.grabacion2.tel_cliente)
        self.assertContains(response, self.grabacion3.tel_cliente)

    def test_buscar_grabaciones_por_callid(self):
        Grabacion.objects.filter(id=self.grabacion1.id).update(callid='1')
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '', 'callid': '1'}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertNotContains(response, self.grabacion2.tel_cliente)
        self.assertNotContains(response, self.grabacion3.tel_cliente)

    def test_buscar_grabaciones_por_id_contacto_externo(self):
        url = reverse('grabacion_buscar', kwargs={'pagina': 1})
        post_data = {'fecha': '', 'tipo_llamada': '', 'tel_cliente': '', 'agente': '',
                     'campana': '', 'marcadas': '', 'duracion': '', 'id_contacto_externo': 'id_ext'}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, self.grabacion3_1.tel_cliente)
        self.assertNotContains(response, self.grabacion1.tel_cliente)
        self.assertNotContains(response, self.grabacion3.tel_cliente)


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
        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertContains(response, self.grabacion2.tel_cliente)
        self.assertContains(response, self.grabacion3.tel_cliente)
        self.assertNotContains(response, self.grabacion2_1.tel_cliente)

    def test_ve_solamente_grabaciones_propias_antes_de_filtrar(self):
        agente3 = self.crear_agente_profile()
        QueueMemberFactory(member=agente3, queue_name=self.queue_campana_1)
        grabacion3_3 = GrabacionFactory.create(
            duracion=1, agente=agente3, campana=self.campana1)

        url = reverse('grabacion_agente_buscar', kwargs={'pagina': 1})
        response = self.client.get(url, follow=True)

        self.assertContains(response, self.grabacion1.tel_cliente)
        self.assertContains(response, self.grabacion2.tel_cliente)
        self.assertContains(response, self.grabacion3.tel_cliente)
        self.assertNotContains(response, grabacion3_3.tel_cliente)
