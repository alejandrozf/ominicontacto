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

import json

from datetime import datetime

from mock import patch

from django.conf import settings
from django.urls import reverse
from django.test import RequestFactory

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_app.views.base import login
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.models import Campana, User, Contacto
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (CampanaFactory, SistemaExternoFactory,
                                               AgenteEnSistemaExternoFactory,
                                               OpcionCalificacionFactory, ContactoFactory,
                                               CalificacionCliente, QueueFactory,
                                               QueueMemberFactory, CalificacionClienteFactory)
from reportes_app.models import ActividadAgenteLog


class APITest(OMLBaseTest):
    """Agrupa demasiados test relacionados con los servicios creados para la API del sistema"""

    def setUp(self):
        super(APITest, self).setUp()
        self.factory = RequestFactory()

        self.supervisor_admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.agente_profile = self.crear_agente_profile()

        self.campana_activa = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                    type=Campana.TYPE_MANUAL,
                                                    nombre='activa uno')
        self.campana_activa_2 = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                      type=Campana.TYPE_PREVIEW,
                                                      nombre='activa dos')
        self.campana_activa_supervisor = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA,
                                                               type=Campana.TYPE_ENTRANTE,
                                                               nombre='activa supervisor uno')
        self.campana_activa_supervisor.supervisors.add(self.supervisor.user)
        self.campana_finalizada = CampanaFactory(estado=Campana.ESTADO_FINALIZADA)
        self.queue = QueueFactory.create(campana=self.campana_activa)
        self.queue1 = QueueFactory.create(campana=self.campana_activa_2)
        self.queue2 = QueueFactory.create(campana=self.campana_activa_supervisor)
        self.queue3 = QueueFactory.create(campana=self.campana_finalizada)
        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)
        self.sistema_externo = SistemaExternoFactory()
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.campana_activa)

        self.contacto = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        self.calificacion_cliente = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion, agente=self.agente_profile,
            contacto=self.contacto)

        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_api_campanas_supervisor_usuario_supervisor_admin_obtiene_todas_campanas_activas(
            self):
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url)
        ids_campanas_esperadas = set(Campana.objects.obtener_activas().values_list('id', flat=True))
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_admin_filtro_nombre(self):
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url, {'name': 'uno'})
        ids_campanas_esperadas = set((self.campana_activa.id, self.campana_activa_supervisor.id))
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_admin_filtro_tipo(self):
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url, {'type': Campana.TYPE_MANUAL})
        ids_campanas_esperadas = set([self.campana_activa.id])
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_admin_filtro_tipos(self):
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url, {'type': str([Campana.TYPE_MANUAL, Campana.TYPE_PREVIEW])})
        ids_campanas_esperadas = set([self.campana_activa.id, self.campana_activa_2.id])
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_admin_filtro_agente(self):
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        QueueMemberFactory.create(member=self.agente_profile,
                                  queue_name=self.campana_activa_supervisor.queue_campana)
        response = self.client.get(url, {'agent': self.agente_profile.id})
        ids_campanas_esperadas = set((self.campana_activa.id, self.campana_activa_supervisor.id))
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_usr_supervisor_no_admin_obtiene_campanas_activas_asignadas(
            self):
        self.actualizar_permisos()
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.campana_activa_supervisor.id)

    def test_servicio_campanas_supervisor_usuario_agente_no_accede_a_servicio(self):
        self.actualizar_permisos()
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_servicio_campanas_supervisor_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('api_campanas_de_supervisor')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_servicio_agentes_activos_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('api_agentes_activos')
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_servicio_opciones_calificaciones_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('api_campana_opciones_calificacion-list', args=[self.campana_activa.pk, 1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_servicio_opciones_calificaciones_usuario_no_agente_no_accede_a_servicio(self):
        self.actualizar_permisos()
        url = reverse('api_campana_opciones_calificacion-list', args=[self.campana_activa.pk, 1])
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_servicio_opciones_calificaciones_usuario_agente_accede_a_servicio(self):
        self.actualizar_permisos()
        id_externo = "id_externo_campana_activa"
        self.sistema_externo.campanas.add(self.campana_activa)
        self.campana_activa.id_externo = id_externo
        self.campana_activa.save()
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        url = reverse(
            'api_campana_opciones_calificacion-list', args=[id_externo, self.sistema_externo.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], self.opcion_calificacion.nombre)

    def test_servicio_opciones_calificaciones_usuario_agente_accede_a_servicio_via_token(self):
        self.actualizar_permisos()
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        id_externo = "id_externo_campana_activa"
        self.sistema_externo.campanas.add(self.campana_activa)
        self.campana_activa.id_externo = id_externo
        self.campana_activa.save()
        url = reverse(
            'api_campana_opciones_calificacion-list', args=[id_externo, self.sistema_externo.pk])
        response = client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], self.opcion_calificacion.nombre)

    def test_api_vista_opciones_calificaciones_no_es_accessible_usando_token_no_agente(self):
        self.actualizar_permisos()
        token_supervisor = Token.objects.get(user=self.supervisor_admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_supervisor)
        url = reverse(
            'api_campana_opciones_calificacion-list', args=[1, self.sistema_externo.pk])
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_api_opciones_calificacion_devuelve_404_si_sistema_externo_no_es_entero(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse(
            'api_campana_opciones_calificacion-list', args=(1, 1))
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_api_opciones_calificacion_sin_sistema_externo_devuelve_404_id_campana_no_entero(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse(
            'api_campana_opciones_calificacion_intern-list', args=("campana_id_str",))
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_api_opciones_calificacion_sin_sistema_externo_usa_id_campana_oml(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse(
            'api_campana_opciones_calificacion_intern-list', args=(self.campana_activa.pk,))

        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], self.opcion_calificacion.nombre)

    def test_api_opciones_calificacion_ocultando_opcion_calificacion(self):
        opcion_calificacion_2 = OpcionCalificacionFactory(campana=self.campana_activa)
        self.opcion_calificacion.oculta = True
        self.opcion_calificacion.save()
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse(
            'api_campana_opciones_calificacion_intern-list', args=(self.campana_activa.pk,))

        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        opcion_data_1 = response.json()[0]
        opcion_data_2 = response.json()[1]
        if response.json()[1]['id'] == self.opcion_calificacion.id:
            opcion_data_1 = response.json()[1]
            opcion_data_2 = response.json()[0]
        self.assertEqual(opcion_data_1['id'], self.opcion_calificacion.id)
        self.assertEqual(opcion_data_2['id'], opcion_calificacion_2.id)
        self.assertEqual(opcion_data_1['name'], self.opcion_calificacion.nombre)
        self.assertEqual(opcion_data_2['name'], opcion_calificacion_2.nombre)
        self.assertTrue(opcion_data_1['hidden'])
        self.assertFalse(opcion_data_2['hidden'])

    def set_redis_mock_return_values(self, redis_mock_class, keys, values):

        redis_fake_dict = dict(zip(keys, values))
        redis_mock_class.return_value.keys.return_value = keys

        def hgetall_fake(key):
            return redis_fake_dict[key]

        redis_mock_class.return_value.hgetall = hgetall_fake

        return redis_mock_class

    @patch('ominicontacto_app.services.asterisk.supervisor_activity.redis.Redis')
    def test_servicio_agentes_activos_funciona_correctamente(
            self, Redis):
        ag1_pk = self.agente_profile.pk
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        key1 = 'OML:AGENT:{0}'.format(ag1_pk)
        key2 = 'OML:AGENT:{0}'.format(ag2.pk)
        key3 = 'OML:SUPERVISOR:{0}'.format(self.supervisor_admin.pk)
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        key1_value = {
            'TIMESTAMP': timestamp,
            'STATUS': 'READY',
            'NAME': self.agente_profile.user.get_full_name(),
            'SIP': self.agente_profile.sip_extension
        }
        key2_value = {
            'TIMESTAMP': timestamp,
            'NAME': ag2.user.get_full_name(),
            'SIP': ag2.sip_extension,
            'STATUS': 'PAUSE',
        }
        key3_value = {
            str(ag1_pk): json.dumps({
                'grupo': self.agente_profile.grupo.nombre,
                'campana': [self.campana_activa.nombre, ]}),
            str(ag2.pk): json.dumps({
                'grupo': ag2.grupo.nombre,
                'campana': [self.campana_activa.nombre, ]}),
        }

        Redis = self.set_redis_mock_return_values(
            Redis, [key1, key2, key3], [key1_value, key2_value, key3_value])

        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        response_json = response.json()
        ag1_value = response_json[0]
        ag2_value = response_json[1]
        self.assertEqual(len(response_json), 2)
        self.assertEqual(ag1_value['id'], ag1_pk)
        self.assertEqual(ag2_value['id'], ag2.pk)

    @patch('ominicontacto_app.services.asterisk.supervisor_activity.redis.Redis')
    def test_servicio_agentes_activos_no_muestra_entradas_status_vacio(
            self, Redis):
        ag1_pk = self.agente_profile.pk
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        key1 = 'OML:AGENT:{0}'.format(ag1_pk)
        key2 = 'OML:AGENT:{0}'.format(ag2.pk)
        key3 = 'OML:SUPERVISOR:{0}'.format(self.supervisor_admin.pk)
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        key1_value = {
            'TIMESTAMP': timestamp,
            'STATUS': 'READY',
            'NAME': self.agente_profile.user.get_full_name(),
            'SIP': self.agente_profile.sip_extension
        }
        key2_value = {
            'TIMESTAMP': timestamp,
            'NAME': ag2.user.get_full_name(),
            'SIP': ag2.sip_extension
        }
        key3_value = {
            str(ag1_pk): json.dumps({
                'grupo': self.agente_profile.grupo.nombre,
                'campana': [self.campana_activa.nombre, ]})
        }
        Redis = self.set_redis_mock_return_values(
            Redis, [key1, key2, key3], [key1_value, key2_value, key3_value])

        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        response_json = response.json()
        ag_value = response_json[0]
        self.assertEqual(len(response_json), 1)
        self.assertEqual(ag_value['id'], ag1_pk)

    @patch('ominicontacto_app.services.asterisk.supervisor_activity.redis.Redis')
    def test_servicio_agentes_activos_no_muestra_entradas_con_menos_campos(
            self, Redis):
        ag1_pk = self.agente_profile.pk
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        key1 = 'OML:AGENT:{0}'.format(ag1_pk)
        key2 = 'OML:AGENT:{0}'.format(ag2.pk)
        key3 = 'OML:SUPERVISOR:{0}'.format(self.supervisor_admin.pk)
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        key1_value = {
            'STATUS': 'READY',
            'NAME': self.agente_profile.user.get_full_name(),
            'SIP': self.agente_profile.sip_extension
        }
        key2_value = {
            'TIMESTAMP': timestamp,
            'NAME': ag2.user.get_full_name(),
            'SIP': ag2.sip_extension
        }
        key3_value = {
            str(ag1_pk): json.dumps({
                'grupo': self.agente_profile.grupo.nombre,
                'campana': [self.campana_activa.nombre, ]})
        }
        Redis = self.set_redis_mock_return_values(
            Redis, [key1, key2, key3], [key1_value, key2_value, key3_value])

        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json), 0)

    def test_api_login_devuelve_token_asociado_al_usuario_password(self):
        url = 'https://{0}{1}'.format(settings.OML_OMNILEADS_HOSTNAME, reverse('api_login'))
        user = self.supervisor_admin.user
        password = PASSWORD
        post_data = {
            'username': user.username,
            'password': password,
        }
        request = self.factory.post(url, data=post_data)
        response = login(request)
        token_obj = Token.objects.get(user=user)
        self.assertEqual(response.data['token'], token_obj.key)

    def test_api_vista_contactos_campanas_es_accessible_usando_token_agente(self):
        self.actualizar_permisos()
        ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        cantidad = self.campana_activa.bd_contacto.contactos.count()
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('api_contactos_campana', args=(self.campana_activa.pk,))
        response = client.get(url, {'search[value]': 1, 'start': 1, 'length': 10, 'draw': 10},
                              format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recordsTotal'], cantidad)

    def test_api_vista_contactos_campanas_no_es_accessible_usando_token_no_agente(self):
        self.actualizar_permisos()
        token_agente = Token.objects.get(user=self.supervisor_admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('api_contactos_campana', args=(self.campana_activa.pk,))
        response = client.get(url, {'search[value]': 1, 'start': 1, 'length': 10, 'draw': 10},
                              format='json')
        self.assertEqual(response.status_code, 403)

    def test_api_adiciona_calificacion_ids_internos(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        observaciones = 'calificacion externa'
        contacto = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        url = reverse('api_disposition-list')
        post_data = {
            'idContact': contacto.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        calificaciones_count = CalificacionCliente.objects.count()
        client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)

    def test_api_adiciona_calificacion_ids_externos(self):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        observaciones = 'calificacion externa'
        id_contacto_externo = 'contacto_externo_1'
        AgenteEnSistemaExternoFactory(
            agente=self.agente_profile, sistema_externo=self.sistema_externo)
        ContactoFactory(bd_contacto=self.campana_activa.bd_contacto,
                        id_externo=id_contacto_externo)
        url = reverse('api_disposition-list')
        post_data = {
            'idExternalSystem': self.sistema_externo.pk,
            'idContact': id_contacto_externo,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        calificaciones_count = CalificacionCliente.objects.count()
        self.client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)

    def test_api_adiciona_calificacion_ids_internos_no_se_accede_credenciales_no_agente(self):
        self.actualizar_permisos()
        observaciones = 'calificacion externa'
        contacto = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        url = reverse('api_disposition-list')
        post_data = {
            'idContact': contacto.pk,
            'idAgent': self.agente_profile.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        token_supervisor = Token.objects.get(user=self.supervisor_admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_supervisor)
        url = reverse('api_disposition-list')
        response = client.post(url, post_data)
        self.assertEqual(response.status_code, 403)

    def test_api_crea_nueva_calificacion_con_nuevo_contacto_metadata_vacia(self):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        observaciones = 'calificacion externa'
        phone = '1232343523'
        id_contacto_externo = 'contacto_externo_1'
        url = reverse('api_disposition_new_contact-list')
        post_data = {
            'phone': phone,
            'idExternalContact': id_contacto_externo,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        calificaciones_count = CalificacionCliente.objects.count()
        contactos_count = Contacto.objects.count()
        self.client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)
        self.assertEqual(Contacto.objects.count(), contactos_count + 1)

    def test_api_crea_nueva_calificacion_con_nuevo_contacto_con_valores_metadata(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        observaciones = 'calificacion externa'
        phone = '1232343523'
        id_contacto_externo = 'contacto_externo_1'
        url = reverse('api_disposition_new_contact-list')
        post_data = {
            'phone': phone,
            'idExternalContact': id_contacto_externo,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones,
        }
        contacto_a_crear = ContactoFactory.build(bd_contacto=self.campana_activa.bd_contacto)
        post_data.update(contacto_a_crear.obtener_datos())
        if 'telefono' in post_data:  # El telefono principal se manda en el campo 'phone' siempre
            post_data.pop('telefono')
        calificaciones_count = CalificacionCliente.objects.count()
        contactos_count = Contacto.objects.count()
        client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)
        self.assertEqual(Contacto.objects.count(), contactos_count + 1)
        self.assertTrue(Contacto.objects.filter(datos=contacto_a_crear.datos).exists())

    def test_api_crear_nueva_calificacion_con_nuevo_contacto_con_opcion_oculta_falla(self):
        self.opcion_calificacion.oculta = True
        self.opcion_calificacion.save()
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        observaciones = 'calificacion externa'
        phone = '1232343523'
        id_contacto_externo = 'contacto_externo_1'
        url = reverse('api_disposition_new_contact-list')
        post_data = {
            'phone': phone,
            'idExternalContact': id_contacto_externo,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        calificaciones_count = CalificacionCliente.objects.count()
        contactos_count = Contacto.objects.count()
        response = self.client.post(url, post_data)
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('idDispositionOption', response_data)
        self.assertEqual(response_data['idDispositionOption'], 'Disposition option id not found')
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count)
        self.assertEqual(Contacto.objects.count(), contactos_count)

    def test_api_crear_calificacion_impide_calificar_mas_de_una_vez_contacto_campana(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        observaciones = 'calificacion externa'
        post_data = {
            'idContact': self.calificacion_cliente.contacto.pk,
            'idAgent': self.agente_profile.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        url = reverse('api_disposition-list')
        response = client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_api_modificar_calificacion_impide_calificar_mas_de_una_vez_contacto_campana(self):
        contacto_nuevo = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion, contacto=contacto_nuevo)
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        observaciones = 'calificacion externa'
        post_data = {
            'id': self.calificacion_cliente.pk,
            'idContact': contacto_nuevo.pk,
            'idAgent': self.agente_profile.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        url = reverse('api_disposition-detail', args=(self.calificacion_cliente.pk,))
        response = client.put(url, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['status']), 'ERROR')

    def test_api_modificar_calificacion_permite_modificarla_con_opcion_calificacion_oculta(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        self.opcion_calificacion.oculta = True
        self.opcion_calificacion.save()
        observaciones = 'Nuevas observaciones'
        post_data = {
            'idContact': self.calificacion_cliente.contacto.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        url = reverse('api_disposition-detail', args=(self.calificacion_cliente.pk,))
        response = client.put(url, post_data)
        self.assertEqual(response.status_code, 200)
        expected_result = {
            "id": self.calificacion_cliente.id,
            "idContact": self.calificacion_cliente.contacto.id,
            "callid": None,
            "idDispositionOption": self.calificacion_cliente.opcion_calificacion.id,
            "comments": observaciones
        }
        self.assertEqual(response.json(), expected_result)

    def test_api_modificar_calificacion_NO_permite_modificarla_a_opcion_calificacion_oculta(self):
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        opcion_oculta = OpcionCalificacionFactory(
            campana=self.campana_activa, oculta=True)
        post_data = {
            'idContact': self.calificacion_cliente.contacto.pk,
            'idDispositionOption': opcion_oculta.pk,
            'comments': self.calificacion_cliente.observaciones
        }
        url = reverse('api_disposition-detail', args=(self.calificacion_cliente.pk,))
        response = client.put(url, post_data)
        self.assertEqual(response.status_code, 400)
        expected_result = {
            'status': 'ERROR',
            'idDispositionOption': 'Disposition option id not found'
        }
        self.assertEqual(response.json(), expected_result)

    def test_api_crear_calificacion_con_opcion_oculta_para_contacto_existente_falla(self):
        id_contacto = self.calificacion_cliente.contacto.pk
        CalificacionCliente.objects.all().delete()
        self.opcion_calificacion.oculta = True
        self.opcion_calificacion.save()

        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        observaciones = 'calificacion externa'
        post_data = {
            'idContact': id_contacto,
            'idAgent': self.agente_profile.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        url = reverse('api_disposition-list')
        response = client.post(url, post_data)
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'ERROR')
        self.assertIn('idDispositionOption', response_data)
        self.assertEqual(response_data['idDispositionOption'], 'Disposition option id not found')

    def test_api_muestra_solo_las_calificaciones_que_ha_hecho_el_agente_que_accede(self):
        contacto_nuevo = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion, contacto=contacto_nuevo)
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('api_disposition-list')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "login_agent")
    def test_api_vista_login_de_agente_retorno_de_valores_correctos(self, login_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        login_agent.return_value = False
        url = reverse('api_agent_asterisk_login')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "login_agent")
    def test_api_vista_login_de_agente_retorno_de_valores_erroneos(self, login_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        login_agent.return_value = True
        url = reverse('api_agent_asterisk_login')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "pause_agent")
    def test_api_vista_pausa_de_agente_retorno_de_valores_correctos(self, pause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        pause_agent.return_value = False, False
        cant_logs = ActividadAgenteLog.objects.count()
        url = reverse('api_make_pause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(ActividadAgenteLog.objects.count(), cant_logs + 1)
        log = ActividadAgenteLog.objects.last()
        self.assertEqual(log.pausa_id, '1')
        self.assertEqual(log.agente_id, self.agente_profile.id)
        self.assertEqual(log.event, ActividadAgenteLog.PAUSE)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "pause_agent")
    def test_api_vista_pausa_de_agente_retorno_de_valores_erroneos(self, pause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        pause_agent.return_value = True, False
        cant_logs = ActividadAgenteLog.objects.count()
        url = reverse('api_make_pause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(ActividadAgenteLog.objects.count(), cant_logs)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "unpause_agent")
    def test_api_vista_despausa_de_agente_retorno_de_valores_correctos(
            self, unpause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        cant_logs = ActividadAgenteLog.objects.count()
        unpause_agent.return_value = False, False
        url = reverse('api_make_unpause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(ActividadAgenteLog.objects.count(), cant_logs + 1)
        log = ActividadAgenteLog.objects.last()
        self.assertEqual(log.pausa_id, '1')
        self.assertEqual(log.agente_id, self.agente_profile.id)
        self.assertEqual(log.event, ActividadAgenteLog.UNPAUSE)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "unpause_agent")
    def test_api_vista_despausa_de_agente_retorno_de_valores_erroneos(self, unpause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        unpause_agent.return_value = True, False
        cant_logs = ActividadAgenteLog.objects.count()
        url = reverse('api_make_unpause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
        self.assertEqual(ActividadAgenteLog.objects.count(), cant_logs)
