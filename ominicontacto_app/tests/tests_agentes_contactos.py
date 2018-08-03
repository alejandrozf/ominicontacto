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
from ominicontacto_app.models import AgenteEnContacto, Campana


class AgentesContactosTests(OMLBaseTest):

    PWD = u'admin123'

    def setUp(self):
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
        self.client.login(username=self.usuario_agente.username, password=self.PWD)

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
            member=agente, queue_name=queue,
            id_campana='{0}_{1}'.format(campana.pk, campana.nombre))

    def test_contacto_list_muestra_campanas_entrantes_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        ids_campanas_devueltas = [int(pk) for pk, _ in response.context_data['campanas']]
        self.assertTrue(self.campana_entrante.pk in ids_campanas_devueltas)

    def test_contacto_list_muestra_campanas_dialer_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        ids_campanas_devueltas = [int(pk) for pk, _ in response.context_data['campanas']]
        self.assertTrue(self.campana_dialer.pk in ids_campanas_devueltas)

    def test_contacto_list_muestra_campanas_manuales_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        ids_campanas_devueltas = [int(pk) for pk, _ in response.context_data['campanas']]
        self.assertTrue(self.campana_manual.pk in ids_campanas_devueltas)

    def test_contacto_list_muestra_campanas_preview_agente(self):
        self.client.login(username=self.usuario_agente.username, password=self.PWD)
        url = reverse('contacto_list')
        response = self.client.get(url, follow=True)
        ids_campanas_devueltas = [int(pk) for pk, _ in response.context_data['campanas']]
        self.assertTrue(self.campana_preview.pk in ids_campanas_devueltas)

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

    def _obtener_datos_post_adicionar_contacto(self, campana):
        contacto_nuevo = ContactoFactory.build(bd_contacto=campana.bd_contacto)
        post_data = {'telefono': contacto_nuevo.telefono}
        columnas = json.loads(contacto_nuevo.bd_contacto.metadata)
        datos_contacto = json.loads(contacto_nuevo.datos)
        for columna, valor in zip(columnas['nombres_de_columnas'][1:], datos_contacto):
            post_data[columna] = valor
        return post_data

    def test_no_se_permite_adicionar_contacto_campanas_dialer(self):
        url = reverse('nuevo_contacto_campana', args=[self.campana_dialer.pk])
        post_data = self._obtener_datos_post_adicionar_contacto(self.campana_dialer)
        response = self.client.post(url, post_data, follow=True)
        self.assertTemplateNotUsed(response)

    def test_se_permite_adicionar_contacto_campanas_entrantes(self):
        url = reverse('nuevo_contacto_campana', args=[self.campana_entrante.pk])
        post_data = self._obtener_datos_post_adicionar_contacto(self.campana_entrante)
        n_contactos = self.campana_entrante.bd_contacto.contactos.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(self.campana_entrante.bd_contacto.contactos.count(), n_contactos + 1)

    def test_se_permite_adicionar_contacto_campanas_manuales(self):
        url = reverse('nuevo_contacto_campana', args=[self.campana_manual.pk])
        post_data = self._obtener_datos_post_adicionar_contacto(self.campana_manual)
        n_contactos = self.campana_manual.bd_contacto.contactos.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(self.campana_manual.bd_contacto.contactos.count(), n_contactos + 1)

    def test_se_permite_adicionar_contacto_campanas_preview(self):
        url = reverse('nuevo_contacto_campana', args=[self.campana_preview.pk])
        post_data = self._obtener_datos_post_adicionar_contacto(self.campana_preview)
        n_contactos = self.campana_preview.bd_contacto.contactos.count()
        self.client.post(url, post_data, follow=True)
        self.assertEqual(self.campana_preview.bd_contacto.contactos.count(), n_contactos + 1)

    def test_adicion_contactos_campanas_preview_adiciona_agente_en_contacto(self):
        url = reverse('nuevo_contacto_campana', args=[self.campana_preview.pk])
        post_data = self._obtener_datos_post_adicionar_contacto(self.campana_preview)
        self.assertFalse(AgenteEnContacto.objects.filter().exists())
        self.client.post(url, post_data, follow=True)
        self.assertTrue(AgenteEnContacto.objects.all().exists())
