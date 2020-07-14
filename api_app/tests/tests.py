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
from django.urls import reverse
from django.test import RequestFactory

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_app.views.base import login
from ominicontacto_app.services.asterisk.agent_activity import AgentActivityAmiManager
from ominicontacto_app.models import Campana, User, Contacto
from ominicontacto_app.services.asterisk.asterisk_ami import AMIManagerConnector
from ominicontacto_app.tests.utiles import OMLBaseTest, PASSWORD
from ominicontacto_app.tests.factories import (CampanaFactory, SistemaExternoFactory,
                                               AgenteEnSistemaExternoFactory,
                                               OpcionCalificacionFactory, ContactoFactory,
                                               CalificacionCliente, QueueFactory,
                                               QueueMemberFactory, CalificacionClienteFactory)


class APITest(OMLBaseTest):
    """Agrupa todos los test relacionados con los servicios creados para la API del sistema"""

    def setUp(self):
        super(APITest, self).setUp()
        self.factory = RequestFactory()

        self.supervisor_admin = self.crear_supervisor_profile(rol=User.ADMINISTRADOR)
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.agente_profile = self.crear_agente_profile()

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
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        ids_campanas_esperadas = set(Campana.objects.obtener_activas().values_list('id', flat=True))
        ids_campanas_devueltas = set([campana['id'] for campana in response.data])
        self.assertEqual(ids_campanas_esperadas, ids_campanas_devueltas)

    def test_api_campanas_supervisor_usuario_supervisor_no_admin_obtiene_campanas_activas_asignadas(
            self):
        self.client.login(username=self.supervisor.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.campana_activa_supervisor.id)

    def test_servicio_campanas_supervisor_usuario_agente_no_accede_a_servicio(self):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        url = reverse('api_campanas_de_supervisor-list', kwargs={'format': 'json'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_servicio_campanas_supervisor_usuario_no_logueado_no_accede_a_servicio(self):
        url = reverse('api_campanas_de_supervisor-list', kwargs={'format': 'json'})
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
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_servicio_opciones_calificaciones_usuario_agente_accede_a_servicio(self):
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

    def _generar_ami_manager_response_agentes(self):
        # genera datos que simulan lo más aproximadamente posible las lineas de output de
        # los estados de los agentes obtenidos por el comando AMI 'database show OML/AGENT'
        linea_agente = 'Output: /OML/AGENT/{0}/NAME                                 : agente{0}'
        linea_sip = 'Output: /OML/AGENT/{0}/SIP                                  : 100{0}'
        linea_status = 'Output: /OML/AGENT/{0}/STATUS                               : {1}:155439223'
        response = []
        self.ag1 = self.agente_profile
        self.ag2 = self.crear_agente_profile()
        self.ag3 = self.crear_agente_profile()
        QueueMemberFactory.create(member=self.ag2, queue_name=self.queue)
        QueueMemberFactory.create(member=self.ag3, queue_name=self.queue)
        datos_agentes = [{'id': self.ag1.pk, 'status': 'READY'},
                         {'id': self.ag2.pk, 'status': 'PAUSE'},
                         {'id': self.ag3.pk, 'status': 'OFFLINE'}]
        for datos_agente in datos_agentes:
            id_agente = datos_agente['id']
            status_agente = datos_agente['status']
            response.extend([linea_agente.format(id_agente), linea_sip.format(id_agente),
                             linea_status.format(id_agente, status_agente)])
        return '\r\n'.join(response), None

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    def test_servicio_agentes_activos_muestra_activos_no_offline(
            self, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        agente = self.crear_agente_profile()
        QueueMemberFactory.create(member=agente, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = self._generar_ami_manager_response_agentes()
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 2)
        for datos_agente in response.json():
            self.assertIn(datos_agente['id'], [str(self.ag1.pk), str(self.ag2.pk)])
            if datos_agente['id'] == str(self.ag1.pk):
                self.assertEqual(datos_agente['status'], 'READY')
            else:
                self.assertEqual(datos_agente['status'], 'PAUSE')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    def test_servicio_agentes_activos_detecta_grupos_menos_lineas_previstas(
            self, ami_connect, ami_disconnect, _ami_manager, manager):
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                       : John Perkins\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                       : Silvia Pensive\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/SIP                        : 1001\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/STATUS                     : READY:1582309000\r\n".format(ag2.pk) + ""
            "2 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 1)
        datos_agente = response.json()[0]
        self.assertEqual(datos_agente['id'], str(ag2.pk))
        self.assertEqual(datos_agente['status'], 'READY')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    def test_servicio_agentes_no_adiciona_grupo_headers_desconocidos(
            self, ami_connect, ami_disconnect, _ami_manager, manager):
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                         : John Perkins\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1001\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : READY:1582309000\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STRANGE-HEADER               : strange-value\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Silvia Pensive\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1002\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309000\r\n".format(ag2.pk) + ""
            "2 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 2)
        datos_agente_1 = response.json()[0]
        datos_agente_2 = response.json()[1]
        self.assertEqual(datos_agente_2['id'], str(ag2.pk))
        self.assertEqual(datos_agente_2['status'], 'PAUSE')
        self.assertEqual([i for i in datos_agente_1.keys()],
                         ['id', 'nombre', 'sip', 'status', 'tiempo', 'grupo', 'campana'])

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    @patch('api_app.utiles.logger')
    def test_servicio_agentes_activos_detecta_grupos_headers_incompletos(
            self, logger, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag2 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                         : John Perkins\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/SIP                          : \r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : READY:1582309000\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Silvia Pensive\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1002\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309000\r\n".format(ag2.pk) + ""
            "2 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 2)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    @patch('api_app.utiles.logger')
    def test_servicio_agentes_activos_entradas_menos_lineas_son_detectadas_y_excluidas(
            self, logger, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag2 = self.crear_agente_profile()
        ag3 = self.crear_agente_profile()
        ag4 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        QueueMemberFactory.create(member=ag3, queue_name=self.queue)
        QueueMemberFactory.create(member=ag4, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                         : John Perkins\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1001\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : READY:1582309100\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Silvia Pensive\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1002\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309000\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Homero Simpson\r\n".format(ag3.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Marge Simpson\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1003\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309500\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1004\r\n".format(ag4.pk) + ""
            "2 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 3)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    @patch('api_app.utiles.logger')
    def test_servicio_agentes_activos_no_incluye_entradas_lineas_status_vacio(
            self, logger, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag10 = self.crear_agente_profile()
        ag11 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag10, queue_name=self.queue)
        QueueMemberFactory.create(member=ag11, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                        : Agente 01\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1004 \r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : \r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                        : Agente10 \n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1013\r\n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : \r\n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/NAME                        : Agente11\r\n".format(ag11.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1014\r\n".format(ag11.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : READY:1582309100\r\n".format(ag11.pk) + ""
            "3 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 1)

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    @patch('api_app.utiles.logger')
    def test_servicio_agentes_activos_no_incluye_agentes_no_asignados_al_supervisor(
            self, logger, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag1 = self.agente_profile
        ag10 = self.crear_agente_profile()
        ag11 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag10, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                        : Agente 01\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1004\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : READY:1582309004\r\n".format(ag1.pk) + ""
            "/OML/AGENT/{0}/NAME                        : Agente10\r\n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1013\r\n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : READY:1582309102\r\n".format(ag10.pk) + ""
            "/OML/AGENT/{0}/NAME                        : Agente11\r\n".format(ag11.pk) + ""
            "/OML/AGENT/{0}/SIP                         : 1014\r\n".format(ag11.pk) + ""
            "/OML/AGENT/{0}/STATUS                      : READY:1582309100\r\n".format(ag11.pk) + ""
            "3 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json), 2)
        for datos_agente in response_json:
            self.assertTrue(datos_agente.get('id') != str(ag11.pk))

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AMIManagerConnector, "_ami_manager")
    @patch.object(AMIManagerConnector, "disconnect")
    @patch.object(AMIManagerConnector, "connect")
    @patch('api_app.utiles.logger')
    def test_servicio_agentes_activos_entradas_mixtas_lineas_pause_id_aceptadas(
            self, logger, ami_connect, ami_disconnect, _ami_manager, manager):
        ami_connect.return_value = False
        ami_disconnect.return_value = False
        ag1_pk = self.agente_profile.pk
        self.campana_activa.supervisors.add(self.supervisor_admin.user)
        ag2 = self.crear_agente_profile()
        ag3 = self.crear_agente_profile()
        ag4 = self.crear_agente_profile()
        QueueMemberFactory.create(member=ag2, queue_name=self.queue)
        QueueMemberFactory.create(member=ag3, queue_name=self.queue)
        QueueMemberFactory.create(member=ag4, queue_name=self.queue)
        self.client.login(username=self.supervisor_admin.user.username, password=PASSWORD)
        _ami_manager.return_value = (
            "/OML/AGENT/{0}/NAME                         : John Perkins\r\n".format(ag1_pk) + ""
            "/OML/AGENT/{0}/PAUSE_ID                     : 1\r\n".format(ag1_pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1001\r\n".format(ag1_pk) + ""
            "/OML/AGENT/{0}/STATUS                       : \r\n".format(ag1_pk) + ""
            "/OML/AGENT/{0}/NAME                         : Silvia Pensive\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1002\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309000\r\n".format(ag2.pk) + ""
            "/OML/AGENT/{0}/NAME                         : FERNANDO XXX\r\n".format(ag3.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1105\r\n".format(ag3.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : \r\n".format(ag3.pk) + ""
            "/OML/AGENT/{0}/NAME                         : Marge Simpson\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/PAUSE_ID                     : 0\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/SIP                          : 1003\r\n".format(ag4.pk) + ""
            "/OML/AGENT/{0}/STATUS                       : PAUSE:1582309500\r\n".format(ag4.pk) + ""
            "2 results found."), None
        url = reverse('api_agentes_activos')
        response = self.client.get(url)
        response_json = response.json()
        agent1_dict = response_json[1]
        self.assertEqual(len(response_json), 2)
        self.assertEqual(agent1_dict['pause_id'], '0')

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
        url = reverse('api_make_pause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "pause_agent")
    def test_api_vista_pausa_de_agente_retorno_de_valores_erroneos(self, pause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        pause_agent.return_value = True, False
        url = reverse('api_make_pause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "unpause_agent")
    def test_api_vista_despausa_de_agente_retorno_de_valores_correctos(
            self, unpause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        unpause_agent.return_value = False, False
        url = reverse('api_make_unpause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'OK')

    @patch('ominicontacto_app.services.asterisk.asterisk_ami.AMIManagerConnector')
    @patch.object(AgentActivityAmiManager, "unpause_agent")
    def test_api_vista_despausa_de_agente_retorno_de_valores_erroneos(self, unpause_agent, manager):
        self.client.login(username=self.agente_profile.user.username, password=PASSWORD)
        unpause_agent.return_value = True, False
        url = reverse('api_make_unpause')
        post_data = {
            'pause_id': 1
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ERROR')
