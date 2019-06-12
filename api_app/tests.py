# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from api_app.utiles import EstadoAgentesService

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import (CampanaFactory, SupervisorProfileFactory,
                                               AgenteProfileFactory)


class APITest(TestCase):
    """Agrupa todos los test relacionados con los servicios creados para la API del sistema"""

    PWD = u'generica123'

    def setUp(self):
        self.supervisor_admin = SupervisorProfileFactory(is_administrador=True)
        self.supervisor_admin.user.set_password(self.PWD)
        self.supervisor_admin.user.save()

        self.supervisor = SupervisorProfileFactory(is_administrador=False)
        self.supervisor.user.set_password(self.PWD)
        self.supervisor.user.save()

        self.agente_profile = AgenteProfileFactory()
        self.agente_profile.user.set_password(self.PWD)
        self.agente_profile.user.save()

        self.campana_activa = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        self.campana_activa_supervisor = CampanaFactory.create(estado=Campana.ESTADO_ACTIVA)
        self.campana_activa_supervisor.supervisors.add(self.supervisor.user)
        self.campana_finalizada = CampanaFactory(estado=Campana.ESTADO_FINALIZADA)

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

    def _generar_ami_response_agentes(self):
        # genera datos que simulan lo más aproximadamente posible las lineas de output de
        # los estados de los agentes obtenidos por el comando AMI 'database show OML/AGENT'
        linea_agente = 'Output: /OML/AGENT/{0}/NAME                                 : agente{0}'
        linea_sip = 'Output:/OML/AGENT/{0}/SIP                                  : 100{0}'
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
