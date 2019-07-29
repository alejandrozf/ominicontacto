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

from __future__ import unicode_literals

from mock import patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_app.utiles import EstadoAgentesService
from api_app.views import login

from ominicontacto_app.models import Campana, User, Contacto
from ominicontacto_app.tests.factories import (CampanaFactory, SupervisorProfileFactory,
                                               AgenteProfileFactory, SistemaExternoFactory,
                                               AgenteEnSistemaExternoFactory,
                                               OpcionCalificacionFactory, ContactoFactory,
                                               CalificacionCliente, QueueFactory,
                                               QueueMemberFactory, CalificacionClienteFactory)


class APITest(TestCase):
    """Agrupa todos los test relacionados con los servicios creados para la API del sistema"""

    PWD = u'generica123'

    def setUp(self):
        self.factory = RequestFactory()

        self.supervisor_admin = SupervisorProfileFactory(is_administrador=True)
        self.supervisor_admin.user.set_password(self.PWD)
        self.supervisor_admin.user.save()

        self.supervisor = SupervisorProfileFactory(is_administrador=False)
        self.supervisor.user.set_password(self.PWD)
        self.supervisor.user.save()

        self.agente_profile = AgenteProfileFactory()
        self.agente_profile.user.set_password(self.PWD)
        self.agente_profile.user.is_agente = True
        self.agente_profile.user.save()

        self.campana_activa = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        self.campana_activa_supervisor = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        self.campana_activa_supervisor.supervisors.add(self.supervisor.user)
        self.campana_finalizada = CampanaFactory(estado=Campana.ESTADO_FINALIZADA)
        self.queue = QueueFactory.create(campana=self.campana_activa)
        QueueMemberFactory.create(member=self.agente_profile, queue_name=self.queue)
        self.sistema_externo = SistemaExternoFactory()
        self.opcion_calificacion = OpcionCalificacionFactory(campana=self.campana_activa)

        self.calificacion_cliente = CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion, agente=self.agente_profile)

        for user in User.objects.all():
            Token.objects.create(user=user)

    def test_api_campanas_supervisor_usuario_supervisor_admin_obtiene_todas_campanas_activas(
            self):
        self.client.login(username=self.supervisor_admin.user.username, password=self.PWD)
        url = reverse('supervisor_campanas-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        ids_campanas_esperadas = set(Campana.objects.obtener_activas().values_list('id', flat=True))
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_usuario_supervisor_no_admin_obtiene_campanas_activas_asignadas(
            self):
        self.client.login(username=self.supervisor.user.username, password=self.PWD)
        url = reverse('supervisor_campanas-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.campana_activa_supervisor.id)

    def test_servicio_campanas_supervisor_usuario_agente_no_accede_a_servicio(self):
        self.client.login(username=self.agente_profile.user.username, password=self.PWD)
        url = reverse('supervisor_campanas-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_servicio_campanas_supervisor_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('supervisor_campanas-list', kwargs={'format': 'json'})
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
        url = reverse('api_campana_opciones_calificacion-list', args=[self.campana_activa.pk, 1])
        self.client.login(username=self.supervisor_admin.user.username, password=self.PWD)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_servicio_opciones_calificaciones_usuario_agente_accede_a_servicio(self):
        id_externo = "id_externo_campana_activa"
        self.sistema_externo.campanas.add(self.campana_activa)
        self.campana_activa.id_externo = id_externo
        self.campana_activa.save()
        self.client.login(username=self.agente_profile.user.username, password=self.PWD)
        url = reverse(
            'api_campana_opciones_calificacion-list', args=[id_externo, self.sistema_externo.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], self.opcion_calificacion.nombre)

    def test_servicio_opciones_calificaciones_usuario_agente_accede_a_servicio_via_token(self):
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

    def _generar_ami_response_agentes(self):
        # genera datos que simulan lo más aproximadamente posible las lineas de output de
        # los estados de los agentes obtenidos por el comando AMI 'database show OML/AGENT'
        linea_agente = 'Output: /OML/AGENT/{0}/NAME                                 : agente{0}'
        linea_sip = 'Output: /OML/AGENT/{0}/SIP                                  : 100{0}'
        linea_status = 'Output: /OML/AGENT/{0}/STATUS                               : {1}:155439223'
        response = []
        datos_agentes = [{'id': 1, 'status': 'READY'}, {'id': 2, 'status': 'PAUSE'},
                         {'id': 3, 'status': 'OFFLINE'}]
        for datos_agente in datos_agentes:
            id_agente = datos_agente['id']
            status_agente = datos_agente['status']
            response.extend([linea_agente.format(id_agente), linea_sip.format(id_agente),
                             linea_status.format(id_agente, status_agente)])
        return '\r\n'.join(response)

    @patch('api_app.utiles.Manager')
    @patch.object(EstadoAgentesService, "_ami_obtener_agentes")
    def test_servicio_agentes_activos_muestra_activos(self, _ami_obtener_agentes, manager):
        self.client.login(username=self.supervisor_admin.user.username, password=self.PWD)
        _ami_obtener_agentes.return_value = self._generar_ami_response_agentes()
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 3)

    def test_api_login_devuelve_token_asociado_al_usuario_password(self):
        url = 'https://{0}{1}'.format(settings.OML_OMNILEADS_IP, reverse('api_login'))
        user = self.supervisor_admin.user
        password = self.PWD
        post_data = {
            'username': user.username,
            'password': password,
        }
        request = self.factory.post(url, data=post_data)
        response = login(request)
        token_obj = Token.objects.get(user=user)
        self.assertEqual(response.data['token'], token_obj.key)

    def test_api_vista_contactos_campanas_es_accessible_usando_token_agente(self):
        ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('api_contactos_campana', args=(self.campana_activa.pk,))
        response = client.get(url, {'search[value]': 1, 'start': 1, 'length': 10, 'draw': 10},
                              format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recordsTotal'], 1)

    def test_api_vista_contactos_campanas_no_es_accessible_usando_token_no_agente(self):
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
        url = reverse('disposition-list')
        post_data = {
            'idContact': contacto.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        calificaciones_count = CalificacionCliente.objects.count()
        client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)

    def test_api_adiciona_calificacion_ids_externos(self):
        self.client.login(username=self.agente_profile.user.username, password=self.PWD)
        observaciones = 'calificacion externa'
        id_contacto_externo = 'contacto_externo_1'
        AgenteEnSistemaExternoFactory(
            agente=self.agente_profile, sistema_externo=self.sistema_externo)
        ContactoFactory(bd_contacto=self.campana_activa.bd_contacto,
                        id_externo=id_contacto_externo)
        url = reverse('disposition-list')
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
        observaciones = 'calificacion externa'
        contacto = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        url = reverse('disposition-list')
        post_data = {
            'idContact': contacto.pk,
            'idAgent': self.agente_profile.pk,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones
        }
        token_supervisor = Token.objects.get(user=self.supervisor_admin.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_supervisor)
        url = reverse('disposition-list')
        response = client.post(url, post_data)
        self.assertEqual(response.status_code, 403)

    def test_api_crea_nueva_calificacion_con_nuevo_contacto_metadata_vacia(self):
        self.client.login(username=self.agente_profile.user.username, password=self.PWD)
        observaciones = 'calificacion externa'
        phone = '1232343523'
        id_contacto_externo = 'contacto_externo_1'
        url = reverse('disposition_new_contact-list')
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
        url = reverse('disposition_new_contact-list')
        post_data = {
            'phone': phone,
            'idExternalContact': id_contacto_externo,
            'idDispositionOption': self.opcion_calificacion.pk,
            'comments': observaciones,
        }
        contacto_a_crear = ContactoFactory.build(bd_contacto=self.campana_activa.bd_contacto)
        post_data.update(contacto_a_crear.obtener_datos())
        post_data.pop('telefono')
        calificaciones_count = CalificacionCliente.objects.count()
        contactos_count = Contacto.objects.count()
        client.post(url, post_data)
        self.assertEqual(CalificacionCliente.objects.count(), calificaciones_count + 1)
        self.assertEqual(Contacto.objects.count(), contactos_count + 1)
        self.assertTrue(Contacto.objects.filter(datos=contacto_a_crear.datos).exists())

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
        url = reverse('disposition-list')
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
        url = reverse('disposition-detail', args=(self.calificacion_cliente.pk,))
        response = client.put(url, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'ERROR')

    def test_api_muestra_solo_las_calificaciones_que_ha_hecho_el_agente_que_accede(self):
        contacto_nuevo = ContactoFactory(bd_contacto=self.campana_activa.bd_contacto)
        CalificacionClienteFactory(
            opcion_calificacion=self.opcion_calificacion, contacto=contacto_nuevo)
        token_agente = Token.objects.get(user=self.agente_profile.user).key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_agente)
        url = reverse('disposition-list')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
