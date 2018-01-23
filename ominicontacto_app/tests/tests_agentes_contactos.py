# -*- coding: utf-8 -*-

"""
Tests relacionados con la lista de contactos de los Agentes
"""
from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse

from ominicontacto_app.tests.factories import (CampanaFactory, ContactoFactory, UserFactory,
                                               QueueFactory, AgenteProfileFactory,
                                               QueueMemberFactory)
from ominicontacto_app.tests.utiles import OMLBaseTest
from ominicontacto_app.models import Campana


class AgentesContactosTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
        """
        Creo dos agentes con una campaña con un contacto cada una.
        """
        self.usuario_agente = self._crear_agente()
        self.campana_dialer, self.contacto_camp_dialer = \
            self._agregar_campana_y_contacto(
                self.usuario_agente, Campana.TYPE_DIALER)
        self.campana_entrante, self.contacto_camp_entrante = \
            self._agregar_campana_y_contacto(
                self.usuario_agente, Campana.TYPE_ENTRANTE)
        self.campana_manual, self.contacto_camp_entrante = \
            self._agregar_campana_y_contacto(
                self.usuario_agente, Campana.TYPE_MANUAL)
        self.campana_preview, self.contacto_camp_entrante = \
            self._agregar_campana_y_contacto(
                self.usuario_agente, Campana.TYPE_PREVIEW)

    def _agregar_campana_y_contacto(self, agente_profile, tipo_campana):
        campana = CampanaFactory.create(
            type=tipo_campana, tiempo_desconexion=3, estado=Campana.ESTADO_ACTIVA)
        self._hacer_miembro(agente_profile, campana)
        contacto = ContactoFactory.create(bd_contacto=campana.bd_contacto)
        return campana, contacto

    def _crear_agente(self):
        usuario_agente = UserFactory(is_staff=False, is_supervisor=False)
        usuario_agente.set_password(self.PWD)
        usuario_agente.save()
        AgenteProfileFactory.create(user=usuario_agente)
        return usuario_agente

    def _hacer_miembro(self, usuario_agente, campana):
        agente = usuario_agente.get_agente_profile()
        queue = QueueFactory.create(campana=campana)
        QueueMemberFactory.create(
            member=agente, queue_name=queue, id_campana='{0}_{1}'.format(campana.pk, campana.nombre))

    def test_contacto_list_muestra_campanas_dialer_entrantes_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        set_ids_campanas_esperadas = set([self.campana_dialer.pk, self.campana_entrante.pk])
        set_ids_campanas_devueltas = set([int(pk) for pk, _ in response.context_data['campanas']])
        self.assertEqual(set_ids_campanas_esperadas, set_ids_campanas_devueltas)

    def test_contacto_list_no_muestra_campanas_manuales_preview_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        set_ids_campanas_esperadas = set([self.campana_preview.pk, self.campana_manual.pk])
        set_ids_campanas_devueltas = set([int(pk) for pk, _ in response.context_data['campanas']])
        self.assertNotEqual(set_ids_campanas_esperadas, set_ids_campanas_devueltas)

    def test_api_contacto_list_devuelve_datos_campana_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse(
            'api_contactos_campana',
            kwargs={'pk_campana': self.campana_dialer.pk})
        response = self.client.get(url, {'start': 0, 'length': 1, 'draw': 1, 'search[value]': ''})
        json_content = json.loads(response.content)
        self.assertEqual(json_content['draw'], 1)
        self.assertEqual(json_content['recordsTotal'], 1)
        self.assertEqual(json_content['recordsFiltered'], 1)
        self.assertEqual(json_content['data'][0][1], unicode(self.contacto_camp_dialer.telefono))
