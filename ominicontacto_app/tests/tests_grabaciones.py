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
Tests relacionados con las grabaciones
"""

from __future__ import unicode_literals

import json

from urllib.parse import urlencode
from unittest.mock import patch
from channels.db import database_sync_to_async
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import Group
from django.test import TransactionTestCase

from simple_history.utils import update_change_reason

from ominicontacto_app.models import GrabacionMarca, OpcionCalificacion, Campana, User

from ominicontacto_app.tests.factories import CalificacionClienteFactory, CampanaFactory, \
    ContactoFactory, GrabacionMarcaFactory, LlamadaLogFactory, \
    OpcionCalificacionFactory, QueueFactory, QueueMemberFactory
from ominicontacto_app.tests.utiles import OMLTestUtilsMixin

from ominicontacto_app.utiles import fecha_hora_local
from reportes_app.models import LlamadaLog

from ominicontacto.asgi import application
from channels.testing import WebsocketCommunicator
from channels.testing import ApplicationCommunicator


class BaseGrabacionesTests(TransactionTestCase, OMLTestUtilsMixin):

    databases = {'default', 'replica'}

    def setUp(self):
        super(BaseGrabacionesTests, self).setUp()
        Group.objects.get_or_create(name=User.SUPERVISOR)
        Group.objects.get_or_create(name=User.AGENTE)

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
                                                     contacto_id='-1', event='COMPLETEAGENT')
        self.llamada_log2 = LlamadaLogFactory.create(duracion_llamada=1, agente_id=self.agente1.id,
                                                     campana_id=self.campana1.id,
                                                     event='COMPLETEAGENT')
        self.llamada_log3 = LlamadaLogFactory.create(duracion_llamada=1, agente_id=self.agente1.id,
                                                     campana_id=self.campana1.id,
                                                     event='COMPLETEAGENT')
        self.marca_campana1 = GrabacionMarcaFactory(callid=self.llamada_log1.callid)
        self.marca_campana2 = GrabacionMarcaFactory(callid=self.llamada_log2.callid)

        self.llamada_log2_1 = LlamadaLogFactory.create(duracion_llamada=1,
                                                       agente_id=self.agente2.id,
                                                       campana_id=self.campana2.id,
                                                       event='COMPLETEAGENT')
        self.marca_campana2_1 = GrabacionMarcaFactory(callid=self.llamada_log2_1.callid)

        self.llamada_log3_1 = LlamadaLogFactory.create(numero_marcado=self.contacto.telefono,
                                                       agente_id=self.agente2.id,
                                                       campana_id=self.campana3.id,
                                                       event='COMPLETEAGENT')

        (_, hace_mucho, ahora) = self._obtener_fechas()
        self.rango_hace_mucho = hace_mucho.date().strftime('%d/%m/%Y') + ' - ' + \
            ahora.date().strftime('%d/%m/%Y')

    def _obtener_fechas(self):
        hoy = fecha_hora_local(now())
        hace_mucho = hoy - timedelta(days=3)
        ahora = fecha_hora_local(now())
        return (hoy, hace_mucho, ahora)

    async def _search_recordings_request(self, formdata):
        ws_communicator = WebsocketCommunicator(
            application=application,
            path="channels/background-tasks",
            headers=[
                (b"cookie", self.client.cookies.output(header="")[1:].encode()),
            ],
        )
        ws_communicator_connected, _ = await ws_communicator.connect(timeout=1)
        self.assertTrue(ws_communicator_connected)
        CHANNEL_LAYER_BACKEND = settings.CHANNEL_LAYERS['default']['BACKEND']
        with (
            patch(f"{CHANNEL_LAYER_BACKEND}.send") as channel_layer_send,
            patch(f"{CHANNEL_LAYER_BACKEND}.group_send") as channel_layer_group_send,
        ):
            formdata.setdefault("pagina", "1")
            formdata.setdefault("grabaciones_x_pagina", "10")
            formdata.setdefault("BASE_URL", "/")
            formdata.setdefault("LANG_CODE", "en")
            request_message = {
                "type": "search_recordings.request",
                "data": urlencode(formdata)
            }
            await ws_communicator.send_json_to(request_message)
            self.assertTrue(await ws_communicator.receive_nothing(timeout=1))
            enqueue_message_channel, enqueue_message = channel_layer_send.call_args[0]
            self.assertEqual(enqueue_message_channel, "background-tasks")
            self.assertEqual(enqueue_message["type"], "search_recordings.enqueue")

            worker_communicator = ApplicationCommunicator(
                application=application,
                scope={
                    "type": "channel",
                    "channel": enqueue_message_channel
                },
            )
            await worker_communicator.send_input(enqueue_message)
            await worker_communicator.wait(timeout=2)
            dequeue_message_channel, dequeue_message = channel_layer_group_send.call_args[0]
            self.assertIn("background-tasks.user-", dequeue_message_channel)
            self.assertEqual(dequeue_message["type"], "search_recordings.dequeue")
            await ws_communicator.send_json_to(dequeue_message)
            respond_message = await ws_communicator.receive_json_from(timeout=1)
            self.assertEqual(respond_message["type"], "search_recordings.respond")
            await ws_communicator.disconnect()
            return respond_message["result"]

    @staticmethod
    @database_sync_to_async
    def llamadalog_filter_update(filter_id, **update_attrs):
        LlamadaLog.objects.filter(id=filter_id).update(**update_attrs)


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
        self.assertTrue(self.llamada_log1.url_archivo_grabacion.endswith(settings.MONITORFORMAT))


class FiltrosBusquedaGrabacionesSupervisorTests(BaseGrabacionesTests):

    def setUp(self):
        super(FiltrosBusquedaGrabacionesSupervisorTests, self).setUp()
        self.client.login(username=self.supervisor1.user, password=self.DEFAULT_PASSWORD)

    def test_filtro_grabaciones_marcadas(self):
        self.assertEqual(LlamadaLog.objects.obtener_grabaciones_marcadas().count(), 3)

    async def test_buscar_grabaciones_por_duracion(self):
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log1.numero_marcado, response)
        self.assertIn(self.llamada_log2.numero_marcado, response)
        self.assertIn(self.llamada_log3.numero_marcado, response)
        # Aseguro que no traiga la grabacion de una campaña que no tiene asignada.
        self.assertNotIn(response, self.llamada_log2_1.numero_marcado)

        await self.llamadalog_filter_update(
            self.llamada_log2.id,
            duracion_llamada=15,
            numero_marcado='42222222',
        )
        await self.llamadalog_filter_update(
            self.llamada_log1.id,
            duracion_llamada=15,
            numero_marcado='41111111',
        )
        await self.llamadalog_filter_update(
            self.llamada_log3.id,
            duracion_llamada=12,
            numero_marcado='43333333',
        )

        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "duracion": 12,
        }))["fragments"]["#table-body"]
        self.assertIn('41111111', response)
        self.assertIn('42222222', response)
        self.assertIn('43333333', response)
        self.assertNotIn(self.llamada_log2_1.numero_marcado, response)

        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "duracion": 15,
        }))["fragments"]["#table-body"]
        self.assertIn('41111111', response)
        self.assertIn('42222222', response)
        self.assertNotIn('43333333', response)

        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "duracion": 16,
        }))["fragments"]["#table-body"]
        self.assertNotIn('41111111', response)
        self.assertNotIn('42222222', response)
        self.assertNotIn('43333333', response)

    async def test_buscar_grabaciones_por_fecha(self):
        (hoy, hace_mucho, ahora) = self._obtener_fechas()
        if hoy.date() < ahora.date():
            (hoy, hace_mucho, ahora) = self._obtener_fechas()
        await self.llamadalog_filter_update(
            self.llamada_log2.id,
            time=hace_mucho,
            numero_marcado='42222222',
        )
        await self.llamadalog_filter_update(
            self.llamada_log1.id,
            time=hoy,
            numero_marcado='41111111',
        )
        await self.llamadalog_filter_update(
            self.llamada_log3.id,
            time=hoy,
            numero_marcado='43333333',
        )
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
        }))["fragments"]["#table-body"]
        self.assertIn('41111111', response)
        self.assertIn('42222222', response)
        self.assertIn('43333333', response)

        rango_hoy = ahora.date().strftime('%d/%m/%Y') + ' - ' + ahora.date().strftime('%d/%m/%Y')
        response = (await self._search_recordings_request({
            "fecha": rango_hoy,
        }))["fragments"]["#table-body"]
        self.assertNotIn('42222222', response)
        self.assertIn('41111111', response)
        self.assertIn('43333333', response)

    async def test_filtro_grabaciones_calificadas_gestion_muestra_gestionadas(self):
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "gestion": True,
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log1.numero_marcado, response)
        self.assertNotIn(self.llamada_log2.numero_marcado, response)
        self.assertNotIn(self.llamada_log3.numero_marcado, response)

    async def test_filtro_grabaciones_calificadas_gestion_excluye_no_gestionadas(self):
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "gestion": False,
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log1.numero_marcado, response)
        self.assertIn(self.llamada_log2.numero_marcado, response)
        self.assertIn(self.llamada_log3.numero_marcado, response)

    async def test_buscar_grabaciones_por_callid(self):
        await self.llamadalog_filter_update(self.llamada_log1.id, callid='1')
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "callid": "1",
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log1.numero_marcado, response)
        self.assertNotIn(self.llamada_log2.numero_marcado, response)
        self.assertNotIn(self.llamada_log3.numero_marcado, response)

    async def test_buscar_grabaciones_por_id_contacto_externo(self):
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
            "id_contacto_externo": "id_ext"
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log3_1.numero_marcado, response)
        self.assertNotIn(self.llamada_log1.numero_marcado, response)
        self.assertNotIn(self.llamada_log3.numero_marcado, response)


class FiltrosBusquedaGrabacionesAgenteTests(BaseGrabacionesTests):

    def setUp(self):
        super(FiltrosBusquedaGrabacionesAgenteTests, self).setUp()
        self.client.login(username=self.agente1.user, password=self.DEFAULT_PASSWORD)

    async def test_ve_solamente_grabaciones_propias(self):
        response = (await self._search_recordings_request({
            "fecha": self.rango_hace_mucho,
        }))["fragments"]["#table-body"]
        self.assertIn(self.llamada_log1.numero_marcado, response)
        self.assertIn(self.llamada_log2.numero_marcado, response)
        self.assertIn(self.llamada_log3.numero_marcado, response)
        self.assertNotIn(self.llamada_log2_1.numero_marcado, response)

    async def test_ve_solamente_grabaciones_propias_antes_de_filtrar(self):
        agente3 = await database_sync_to_async(self.crear_agente_profile)()
        await database_sync_to_async(QueueMemberFactory)(
            member=agente3,
            queue_name=self.queue_campana_1
        )
        llamada_log3_3 = await database_sync_to_async(LlamadaLogFactory.create)(
            duracion_llamada=1, agente_id=agente3.id, campana_id=self.campana1.id)

        ahora = self._obtener_fechas()[2]
        rango_hoy = ahora.date().strftime('%d/%m/%Y') + ' - ' + ahora.date().strftime('%d/%m/%Y')
        response = await self._search_recordings_request({
            "fecha": rango_hoy,
        })
        self.assertIn(self.llamada_log1.numero_marcado, response["fragments"]["#table-body"])
        self.assertIn(self.llamada_log2.numero_marcado, response["fragments"]["#table-body"])
        self.assertIn(self.llamada_log3.numero_marcado, response["fragments"]["#table-body"])
        self.assertNotIn(llamada_log3_3.numero_marcado, response["fragments"]["#table-body"])
